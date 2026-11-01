"""Reject identity changes relative to a Git commit without executing its code."""
import argparse
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def snapshot(read):
    meta = read('rectoverso.json')
    places = read(meta['sourceFiles']['places'])
    languages = {}
    for language, artifact in meta['languages'].items():
        model = read(artifact['sourceFiles']['noteType'])
        deck = read(artifact['sourceFiles']['deck'])
        languages[language] = {
            'artifact': artifact['id'], 'deck': deck['id'], 'model': model['id'],
            'fields': [model['fieldIDs'][name] for name in model['fields']],
            'templates': [template['id'] for template in model['templates']],
            'guids': {place['code']: place['guid'][language] for place in places},
        }
    return {'deck': meta['id'], 'languages': languages}


def compare(before, after):
    if before['deck'] != after['deck']:
        raise ValueError('Source deck identity changed')
    additions = {}
    for language, old in before['languages'].items():
        if language not in after['languages']:
            raise ValueError(f'{language}: existing language removed')
        new = after['languages'][language]
        for field in ('artifact', 'deck', 'model', 'templates'):
            if old[field] != new[field]:
                raise ValueError(f'{language}: {field} identities changed; needs an explicit migration')
        # Append-only fields are the reviewed v0.4 metadata migration. Existing field
        # identities and order remain exact; reorder/replacement/deletion still fail.
        old_fields, new_fields = old['fields'], new['fields']
        if (not isinstance(new_fields, list) or new_fields[:len(old_fields)] != old_fields
                or len(set(new_fields)) != len(new_fields)):
            raise ValueError(f'{language}: fields identities changed; needs an explicit migration')
        for code, guid in old['guids'].items():
            if new['guids'].get(code) != guid:
                raise ValueError(f'{language}/{code}: existing note removed or GUID changed')
        additions[language] = sorted(set(new['guids']) - set(old['guids']))
    return {'existingIdentitiesPreserved': True, 'addedPlaces': additions,
            'addedLanguages': sorted(set(after['languages']) - set(before['languages']))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base', help='Full commit SHA, already fetched locally')
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', args.base) or args.base == '0' * 40:
        parser.error('base must be a nonzero full commit SHA')

    def previous(path):
        return json.loads(subprocess.check_output(['git', 'show', f'{args.base}:{path}'], cwd=ROOT))

    report = compare(snapshot(previous), snapshot(lambda path: json.loads((ROOT / path).read_text())))
    report['baseCommit'] = args.base
    args.output.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
