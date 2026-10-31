"""Prepare ISO questions and approved named-region questions from frozen geometry.

Regional questions partition whole source polygons, never clipping coastlines.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from shapely import make_valid, union_all
from shapely.geometry import shape, mapping, MultiPolygon
from shapely.geometry.polygon import orient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from regions import entries as regional_entries, polygon_fingerprints

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(path.read_text())


def polygons(geometry):
    if geometry.geom_type == 'Polygon':
        return [geometry]
    if geometry.geom_type in ('MultiPolygon', 'GeometryCollection'):
        return [part for child in geometry.geoms for part in polygons(child)]
    return []


def joined(parts):
    return parts[0] if len(parts) == 1 else MultiPolygon(parts)


def grouped_indices(parts, groups):
    assigned, indices = set(), []
    for group in groups:
        west, south, east, north = group['bounds']
        current = [i for i, part in enumerate(parts)
                   if west <= part.representative_point().x <= east
                   and south <= part.representative_point().y <= north]
        if not current or assigned.intersection(current):
            raise ValueError(f'Empty or overlapping picture group {group}')
        assigned.update(current)
        indices.append(current)
    if groups and len(assigned) != len(parts):
        raise ValueError(f'Picture groups omit {len(parts)-len(assigned)} polygons')
    return indices


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('--exclude-pending', action='store_true')
    args = parser.parse_args()
    coverage = read(ROOT / 'source/geography/coverage.json')
    selections = read(ROOT / 'source/geography/geometry-selections.json')
    picture_groups = read(ROOT / 'source/geography/picture-groups.json')
    regional = read(ROOT / 'source/geography/regional-questions.json')
    extra = regional_entries(regional, picture_groups)
    entries = coverage['entries']
    assert len(entries) == len({p['code'] for p in entries}) == coverage['referenceCount']
    assert set(selections) == {p['code'] for p in entries}
    files = {name: args.sources / f'ne_10m_admin_0_{name}.geojson'
             for name in ('countries', 'map_units', 'disputed_areas')}
    files['minor_islands'] = args.sources / 'ne_10m_admin_0_scale_rank_minor_islands.geojson'
    files['aadc_mcdonald'] = ROOT / 'source/geography/supplements/aadc-mcdonald-2020.geojson'
    layers = {key: read(path)['features'] for key, path in files.items()}
    expected = read(ROOT / 'source/geography/natural-earth-sha256.json')
    supplement = read(ROOT / 'source/geography/supplements/provenance.json')
    for key, path in files.items():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if key != 'aadc_mcdonald' and digest != expected[path.name]:
            raise ValueError(f'Source checksum changed: {path.name}')
        if key == 'aadc_mcdonald' and digest != supplement['sha256']:
            raise ValueError('Supplementary coastline checksum changed')
    pending = [p['code'] for p in entries if selections[p['code']].get('pendingPolicy')]
    if pending and not args.exclude_pending:
        raise ValueError('Unresolved boundary policy: ' + ', '.join(pending))

    def selected(selection):
        matches = [f for f in layers[selection['layer']]
                   if f['properties'].get(selection['key']) == selection['value']]
        if not matches:
            raise ValueError(f'No source feature for {selection}')
        return matches

    places, features, audits, prepared_regions, partition_audit = [], [], [], [], []

    def emit(entry, parts, field_parts, region, source, views=(), scope=None, repairs=(), context=None):
        geometry, field_geometry = joined(parts), joined(field_parts)
        if not geometry.is_valid or not field_geometry.is_valid:
            raise ValueError(f'{entry["code"]}: invalid question geometry')
        is_region = 'parentCode' in entry
        place = dict(entry, region=region,
                     rosters=['maps-named-regions-v1'] if is_region else ['iso-countries-territories-249'],
                     geometry_source=source, review={'provisional_names': False,
                     'authoritativeRegistryVerified': False if is_region else coverage['authoritativeRegistryVerified']})
        if scope:
            place['questionScope'] = scope
        if source.get('answerNote'):
            place['answerNote'] = source['answerNote']
        if views:
            place['pictureGroups'] = [dict(v['properties'], polygons=len(polygons(shape(v['geometry'])))) for v in views]
        properties = {'code': entry['code'], 'name': entry['name']['en'], 'region': region,
                      'pictureGroups': list(views), 'fieldOutline': mapping(field_geometry)}
        if is_region:
            properties.update(parentCode=entry['parentCode'], wholeQuestion=True, regionalContext=context)
        places.append(place)
        features.append({'type': 'Feature', 'properties': properties, 'geometry': mapping(geometry)})
        audits.append({'code': entry['code'], 'polygons': len(parts), 'bounds': list(geometry.bounds),
                       'valid': True, 'fieldPolygons': len(field_parts), 'fieldValid': True,
                       'fieldHausdorffDegrees': geometry.hausdorff_distance(field_geometry),
                       'repairs': list(repairs), 'selection': source})

    for entry in entries:
        code = entry['code']
        if code in pending:
            continue
        record = selections[code]
        included = [f for selection in record['include'] for f in selected(selection)]
        excluded = [f for selection in record['exclude'] for f in selected(selection)]
        repairs = []

        def valid(feature):
            geometry = shape(feature['geometry'])
            if not geometry.is_valid:
                fixed = make_valid(geometry)
                repairs.append({'feature': feature.get('id'), 'beforeArea': geometry.area,
                                'afterArea': fixed.area, 'method': 'Shapely make_valid'})
                geometry = fixed
            return geometry

        geometry = union_all([valid(f) for f in included])
        if excluded:
            geometry = geometry.difference(union_all([valid(f) for f in excluded]))
        parts = polygons(geometry)
        if not parts or not geometry.is_valid:
            raise ValueError(f'{code}: empty or invalid prepared geometry')
        parts = [orient(part, sign=-1) for part in parts]
        # Simplify the complete original once. Every child takes identical whole field
        # polygons; it must not introduce another tolerance or fallback decision.
        field_parts = []
        for part in parts:
            x0, y0, x1, y1 = part.bounds
            tolerance = min(0.02, max(x1-x0, y1-y0) / 200)
            field_parts.append(orient(part.simplify(tolerance, preserve_topology=True), sign=-1))
        if not joined(field_parts).is_valid:
            field_parts = parts
        region = included[0]['properties'].get('SUBREGION')
        if not region:
            raise ValueError(f'{code}: missing region')
        groups = picture_groups.get(code, [])
        indices = grouped_indices(parts, groups)
        views = [{'type': 'Feature', 'properties': {'name': group['name']},
                  'geometry': mapping(joined([parts[i] for i in members]))}
                 for group, members in zip(groups, indices)]
        if code in regional['parentGeometry']:
            fingerprint = polygon_fingerprints(json.loads(json.dumps(mapping(joined(field_parts)))))
            if fingerprint != regional['parentGeometry'][code]['polygons']:
                raise ValueError(f'{code}: complete baseline field geometry changed')
            partition_audit.append({'parentCode': code, 'sourcePolygons': len(parts),
                                    'groups': [len(i) for i in indices],
                                    'allPolygonsAssignedExactlyOnce': True,
                                    'baselineFieldPolygonsUnchanged': True})
        core = regional['coreGroups'].get(code)
        if core is None:
            emit(entry, parts, field_parts, region, record, views, repairs=repairs)
        else:
            members = indices[core]
            emit(entry, [parts[i] for i in members], [field_parts[i] for i in members], region, record,
                 scope={'kind': 'core-region', 'groupIndex': core, 'name': groups[core]['name']}, repairs=repairs)
        for child in (r for r in extra if r['parentCode'] == code):
            index = child['groupIndex']
            members = indices[index]
            source = {'parentCode': code, 'groupIndex': index, 'bounds': groups[index]['bounds'],
                      'sourceSelection': record}
            prepared_regions.append((child, [parts[i] for i in members], [field_parts[i] for i in members], source, mapping(joined(parts))))
    for child, parts, field_parts, source, context in prepared_regions:
        emit(child, parts, field_parts, child['regionHint']['en'], source, context=context)

    args.out.mkdir(parents=True, exist_ok=True)
    neutral = read(ROOT / 'source/geography/neutral-areas.json')
    neutral_features = [f for selection in neutral['areas'] for f in selected(selection)]
    outputs = {'places.json': places, 'places.geojson': {'type': 'FeatureCollection', 'features': features},
               'neutral-areas.geojson': {'type': 'FeatureCollection', 'features': neutral_features},
               'geometry-audit.json': {'complete': not pending, 'pending': pending, 'places': audits},
               'regional-partition-audit.json': partition_audit,
               'sources.json': {key: {'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                                for key, path in files.items()}}
    for name, value in outputs.items():
        (args.out / name).write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(f'Prepared {len(places)} questions ({len(extra)} regional); {len(pending)} held pending policy.')


if __name__ == '__main__':
    main()
