"""Explicit, stable regional questions alongside the unchanged ISO code roster."""
from collections import Counter
import hashlib
import json

NAMESPACE = 'rectoverso-maps-regions-v1'
ROSTER = 'iso-249-plus-named-regions-v1'


def polygon_fingerprints(outline):
    """Compare every coordinate and ring, independent of polygon order/JSON number spelling."""
    parts = [outline['coordinates']] if outline['type'] == 'Polygon' else outline['coordinates']
    def numbers(value):
        if isinstance(value, list):
            return [numbers(x) for x in value]
        number = float(value)
        return (0.0 if number == 0 else number).hex()
    return sorted(hashlib.sha256(json.dumps(numbers(part), separators=(',', ':')).encode()).hexdigest()
                  for part in parts)


def entries(spec, picture_groups):
    result, codes, guids, groups = [], set(), set(), set()
    for record in spec['questions']:
        code, parent, index = record['code'], record['parentCode'], record['groupIndex']
        if (record['codeNamespace'] != NAMESPACE or not code.startswith('MAPS-' + parent + '-')
                or code in codes or (parent, index) in groups):
            raise ValueError('Invalid or duplicate regional identity')
        if parent not in picture_groups or type(index) is not int or not 0 <= index < len(picture_groups[parent]):
            raise ValueError('Regional group index is invalid')
        group = picture_groups[parent][index]
        if record['name'] != group['name'] or index == spec['coreGroups'].get(parent):
            raise ValueError('Regional name/group differs or duplicates a core question')
        if set(record['guid']) != {'en', 'fr'} or set(record['regionHint']) != {'en', 'fr'}:
            raise ValueError('Regional language/identity contract differs')
        for language, guid in record['guid'].items():
            if guid != f'rv-map-{language}-{code.lower()}' or guid in guids:
                raise ValueError('Regional GUID differs or collides')
            guids.add(guid)
        codes.add(code)
        groups.add((parent, index))
        result.append(dict(record))
    expected = {(parent, i) for parent, values in picture_groups.items() for i in range(len(values))
                if i != spec['coreGroups'].get(parent)}
    if groups != expected or len(result) != spec['supplementaryCount']:
        raise ValueError('Regional roster omits or adds an unapproved named group')
    return result


def verify_partition(places, spec):
    """Every original field polygon appears exactly once across its separate questions."""
    indexed = {p['code']: p for p in places}
    for parent, reference in spec['parentGeometry'].items():
        children = [r for r in spec['questions'] if r['parentCode'] == parent]
        components = list(children)
        if parent in spec['coreGroups']:
            components.append({'code': parent})
        got = []
        for item in components:
            actual = polygon_fingerprints(json.loads(indexed[item['code']]['field'])['outline'])
            group = item.get('groupIndex', spec['coreGroups'].get(parent))
            if actual != reference['groups'][group]:
                raise ValueError(f'{item["code"]}: regional geometry differs from its named source group')
            got.extend(actual)
        if Counter(got) != Counter(reference['polygons']):
            raise ValueError(f'{parent}: regional geometry loses, duplicates or changes source polygons')
        if parent not in spec['coreGroups']:
            parent_parts = polygon_fingerprints(json.loads(indexed[parent]['field'])['outline'])
            if parent_parts != reference['polygons']:
                raise ValueError(f'{parent}: existing ISO overview geometry changed')
