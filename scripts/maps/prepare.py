"""Prepare explicit ISO-entry geometry from frozen sources and approved selections.

Requires pinned Shapely. Pending policy rows are rejected unless explicitly
excluded for incomplete visual review; that review cannot be a complete package.
"""
import argparse
import hashlib
import json
from pathlib import Path
from shapely import make_valid, union_all
from shapely.geometry import shape, mapping, MultiPolygon
from shapely.geometry.polygon import orient

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(path.read_text())


def polygons(geometry):
    if geometry.geom_type == 'Polygon':
        return [geometry]
    if geometry.geom_type in ('MultiPolygon', 'GeometryCollection'):
        return [part for child in geometry.geoms for part in polygons(child)]
    return []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', type=Path)
    parser.add_argument('out', type=Path)
    parser.add_argument('--exclude-pending', action='store_true')
    args = parser.parse_args()
    coverage = read(ROOT / 'source/geography/coverage.json')
    selections = read(ROOT / 'source/geography/geometry-selections.json')
    picture_groups = read(ROOT / 'source/geography/picture-groups.json')
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

    places, features, audits = [], [], []
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
        geometry = parts[0] if len(parts) == 1 else MultiPolygon(parts)
        # Keep small-island shape and topology. The maximum tolerance is about
        # 2 km at the equator; small polygons use a much finer relative tolerance.
        field_parts = []
        for part in parts:
            x0, y0, x1, y1 = part.bounds
            tolerance = min(0.02, max(x1-x0, y1-y0) / 200)
            field_parts.append(orient(part.simplify(tolerance, preserve_topology=True), sign=-1))
        field_geometry = field_parts[0] if len(field_parts) == 1 else MultiPolygon(field_parts)
        if not field_geometry.is_valid:
            # Keep exact source topology rather than silently repair a simplified result.
            field_geometry = geometry
        region = included[0]['properties'].get('SUBREGION')
        if not region:
            raise ValueError(f'{code}: missing region')
        place = dict(entry, region=region, rosters=['iso-countries-territories-249'],
                     geometry_source=record, review={'provisional_names': False,
                     'authoritativeRegistryVerified': coverage['authoritativeRegistryVerified']})
        if record.get('answerNote'):
            place['answerNote'] = record['answerNote']
        views = []
        assigned = set()
        for group in picture_groups.get(code, []):
            west, south, east, north = group['bounds']
            indices = [i for i, part in enumerate(parts)
                       if west <= part.representative_point().x <= east
                       and south <= part.representative_point().y <= north]
            if not indices or assigned.intersection(indices):
                raise ValueError(f'{code}: empty or overlapping picture group {group}')
            assigned.update(indices)
            group_geometry = parts[indices[0]] if len(indices) == 1 else MultiPolygon([parts[i] for i in indices])
            views.append({'type': 'Feature', 'properties': {'name': group['name']},
                          'geometry': mapping(group_geometry)})
        if views and len(assigned) != len(parts):
            raise ValueError(f'{code}: picture groups omit {len(parts)-len(assigned)} polygons')
        if views:
            place['pictureGroups'] = [dict(v['properties'], polygons=len(polygons(shape(v['geometry'])))) for v in views]
        places.append(place)
        features.append({'type': 'Feature', 'properties': {'code': code, 'name': entry['name']['en'],
                         'region': region, 'pictureGroups': views,
                         'fieldOutline': mapping(field_geometry)}, 'geometry': mapping(geometry)})
        audits.append({'code': code, 'includedFeatures': len(included), 'excludedFeatures': len(excluded),
                       'polygons': len(parts), 'bounds': list(geometry.bounds), 'valid': geometry.is_valid,
                       'fieldPolygons': len(polygons(field_geometry)), 'fieldValid': field_geometry.is_valid,
                       'fieldHausdorffDegrees': geometry.hausdorff_distance(field_geometry),
                       'repairs': repairs, 'selection': record})
    args.out.mkdir(parents=True, exist_ok=True)
    neutral = read(ROOT / 'source/geography/neutral-areas.json')
    neutral_features = [f for selection in neutral['areas'] for f in selected(selection)]
    outputs = {'places.json': places, 'places.geojson': {'type': 'FeatureCollection', 'features': features},
               'neutral-areas.geojson': {'type': 'FeatureCollection', 'features': neutral_features},
               'geometry-audit.json': {'complete': not pending, 'pending': pending, 'places': audits},
               'sources.json': {key: {'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                                for key, path in files.items()}}
    for name, value in outputs.items():
        (args.out / name).write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(f'Prepared {len(places)} geometries; {len(pending)} held pending an owner boundary decision.')


if __name__ == '__main__':
    main()
