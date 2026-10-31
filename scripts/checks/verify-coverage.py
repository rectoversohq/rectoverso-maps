"""Verify deck metadata against the frozen, directly inspected ISO OBP reference.

This checks consistency with the dated snapshot, not live registry freshness.
"""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from source_data import inputs
from regions import entries as regional_entries, verify_partition, NAMESPACE

ROOT = Path(__file__).resolve().parents[2]


def read(name):
    return json.loads((ROOT / name).read_text())


def indexed(rows, label):
    result = {row['code']: row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f'{label}: duplicate country code')
    return result


def main():
    coverage = read('source/geography/coverage.json')
    evidence = coverage['registryVerification']
    reference_path = ROOT / evidence['referenceFile']
    if hashlib.sha256(reference_path.read_bytes()).hexdigest() != evidence['referenceSHA256']:
        raise ValueError('ISO reference checksum differs')
    reference = json.loads(reference_path.read_text())
    official = indexed(reference['entries'], 'ISO reference')
    if len(official) != reference['count'] or reference['filter'] != 'Officially assigned codes':
        raise ValueError('ISO reference count or code type differs')
    for key, width in [('alpha2', 2), ('code', 3), ('numeric', 3)]:
        values = [row[key] for row in official.values()]
        if len(set(values)) != len(values) or any(len(v) != width for v in values):
            raise ValueError(f'ISO reference {key}: duplicate or malformed value')
    if coverage['referenceCount'] != len(official) or coverage['authoritativeRegistryVerified'] is not True:
        raise ValueError('Coverage count or verification status differs')
    spec = read('source/geography/regional-questions.json')
    regional = regional_entries(spec, read('source/geography/picture-groups.json'))
    if (coverage.get('supplementaryEntries') != regional or spec['isoCount'] != len(official)
            or coverage.get('supplementaryCount') != len(regional)
            or coverage.get('totalCount') != len(official) + len(regional)):
        raise ValueError('Supplementary coverage/count differs from approved regions')
    extras = indexed(regional, 'regional questions')
    expected_codes = official.keys() | extras.keys()
    sources = {
        'coverage': coverage['entries'] + regional,
        'codebook': read('source/geography/codebook.json'),
        'places': read('source/places.json'),
    }
    for label, rows in sources.items():
        entries = indexed(rows, label)
        if entries.keys() != expected_codes:
            raise ValueError(f'{label}: country roster differs from ISO reference')
        for code, row in entries.items():
            if code in extras:
                if row.get('codeNamespace') != NAMESPACE or any(k in row for k in ('alpha2', 'numeric', 'formalReferenceName')):
                    raise ValueError(f'{label}: regional question pretends to be an ISO entry')
                if any(row.get(k) != v for k, v in extras[code].items()):
                    raise ValueError(f'{label}: {code} differs from approved regional source')
                continue
            expected = official[code]
            if any(row[key] != expected[key] for key in ('alpha2', 'numeric')):
                raise ValueError(f'{label}: {code} code differs')
            if row['formalReferenceName'] != expected['officialShortName']:
                raise ValueError(f'{label}: {code} official short names differ')
            if row.get('formalReferenceNote') != expected.get('nameNote'):
                raise ValueError(f'{label}: {code} name annotation differs')
            if any('ISO OBP' not in row['formalReferenceSource'][lang] for lang in ('en', 'fr')):
                raise ValueError(f'{label}: {code} name provenance is missing')
            if label == 'places' and row['review']['authoritativeRegistryVerified'] is not True:
                raise ValueError(f'{label}: {code} verification status differs')
    verify_partition(sources['places'], spec)
    metadata = read('rectoverso.json')
    if (metadata['cards'] != len(expected_codes) or metadata['pictures'] != len(expected_codes)
            or metadata['coverage'].get('totalCount') != len(expected_codes)
            or metadata['coverage'].get('supplementaryCount') != len(extras)
            or metadata['sourceFiles'].get('regionalQuestions') != 'source/geography/regional-questions.json'):
        raise ValueError('Release metadata regional count or source differs')
    if metadata['coverage']['authoritativeRegistryVerified'] is not True or metadata['coverage']['referenceCount'] != len(official):
        raise ValueError('Release metadata verification status or count differs')
    if metadata['sourceFiles']['isoReference'] != evidence['referenceFile']:
        raise ValueError('Release metadata references a different ISO snapshot')
    if set(metadata['languages']) != {'en', 'fr'} or metadata['id'] != 'rectoverso-maps':
        raise ValueError('Expected one Maps deck with English and French artifacts')
    if metadata['releaseTag'] != 'v' + metadata['version']:
        raise ValueError('Version and release tag differ')
    credits = metadata['imageCredits']
    if len(credits) != metadata['pictures'] or len({credit['file'] for credit in credits}) != len(credits):
        raise ValueError('Missing or duplicate image credits')
    for credit in credits:
        picture = ROOT / metadata['sourceFiles']['pictures'] / credit['file']
        if (Path(credit['file']).name != credit['file'] or not picture.is_file()
                or not all(credit.get(key) for key in ('creator', 'source', 'license'))):
            raise ValueError('Missing image or incomplete image credit')
    if {place['picture'] for place in sources['places']} != {credit['file'] for credit in credits}:
        raise ValueError('Place pictures and image credits disagree')
    all_guids, model_ids, deck_ids, package_names = set(), set(), set(), set()
    for language, artifact in metadata['languages'].items():
        verify_language(language, sources, coverage, expected_codes)
        localized, notes, model, deck = inputs(language)
        guids = {note['guid'] for note in notes}
        if all_guids & guids or model['id'] in model_ids or deck['id'] in deck_ids:
            raise ValueError('Languages collide in note, model or deck identities')
        all_guids.update(guids); model_ids.add(model['id']); deck_ids.add(deck['id'])
        package = artifact['package']
        if Path(package['file']).name != package['file'] or package['file'] in package_names:
            raise ValueError('Invalid or duplicate language artifact filename')
        package_names.add(package['file'])
        expected_url = metadata['repository'] + '/releases/download/' + metadata['releaseTag'] + '/' + package['file']
        if package['url'] != expected_url:
            raise ValueError('Artifact URL differs from shared repository/tag')
        if localized['cards'] != len(notes) or deck['name'] != metadata['title'][language]:
            raise ValueError('Language card count or plain deck title differs')
    print(f'{len(official)} ISO entries + {len(extras)} regional questions: names, exact named-group geometry, both language answers and distinct identities verified.')


def verify_language(language, sources, coverage, expected_codes):
    metadata, notes, model, deck = inputs(language)
    by_guid = {note['guid']: note for note in notes}
    if len(by_guid) != len(notes) or len(notes) != len(expected_codes):
        raise ValueError('Duplicate note GUIDs or wrong note count')
    answer_field = {'en': 'Country or territory', 'fr': 'Pays ou territoire'}[language]
    places = indexed(sources['places'], 'places')
    codebook = indexed(sources['codebook'], 'codebook')
    for row in coverage['entries'] + coverage['supplementaryEntries']:
        code = row['code']
        if row['name'] != places[code]['name'] or row['name'] != codebook[code]['name']:
            raise ValueError(f'{code}: learner names disagree across source records')
        note = by_guid[row['guid'][language]]
        if note['fields'][answer_field] != row['name'][language]:
            raise ValueError(f'{code}: learner answer differs from approved name')
        if note['fields']['RectoVerso place'] != places[code]['field']:
            raise ValueError(f'{code}: note geometry differs from source place field')



if __name__ == '__main__':
    main()
