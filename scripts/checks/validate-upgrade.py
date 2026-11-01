"""Verify an additive release applies new content and preserves old review state.

Use explicit local packages; neither package is downloaded or published here.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import tempfile

from anki.collection import Collection
from anki.cards_pb2 import FsrsMemoryState
from anki.import_export_pb2 import ImportAnkiPackageOptions, ImportAnkiPackageRequest


def import_package(collection, package):
    options = ImportAnkiPackageOptions(with_scheduling=True, merge_notetypes=True)
    collection.import_anki_package(ImportAnkiPackageRequest(
        package_path=str(package.resolve()), options=options))


def schedule(card):
    memory = card.memory_state.SerializeToString() if card.memory_state else None
    return (card.id, card.nid, card.did, card.type, card.queue, card.ivl, card.due,
            card.factor, card.reps, card.lapses, memory, card.desired_retention)


def contents(collection):
    # Anki preserves old files and renames colliding imports. Compare the bytes
    # actually referenced by each note, rather than requiring a clean media folder.
    media = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
             for p in Path(collection.media.dir()).iterdir() if p.is_file()}

    def normalized(field):
        def image(match):
            name = match.group(1)
            if name not in media:
                raise ValueError(f'Missing referenced picture: {name}')
            return f'src="sha256:{media[name]}"'
        return re.sub(r'src="([^"\n]+)"', image, field)

    notes = {note.guid: (note.mid, tuple(normalized(field) for field in note.fields))
             for note in (collection.get_note(nid) for nid in collection.find_notes(''))}
    models = {model['id']: model for model in collection.models.all()
              if model['id'] in {mid for mid, _ in notes.values()}}
    # Anki may retain a local template display name. IDs and rendered templates
    # must match; a display-name alias does not change the question or its answer.
    schemas = {mid: {'fields': [(f['name'], f['id']) for f in model['flds']],
                     'templates': [(t['id'], t['qfmt'], t['afmt']) for t in model['tmpls']],
                     'css': model['css']}
               for mid, model in models.items()}
    return notes, schemas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('updated', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    expected = json.loads(args.updated.with_suffix('.rectoverso.json').read_text())['cards']
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='upgrade-', dir=args.output.parent) as temporary:
        root = Path(temporary)
        (root / 'target').mkdir()
        (root / 'upgrade').mkdir()
        target = Collection(str(root / 'target' / 'collection.anki2'))
        try:
            import_package(target, args.updated)
            target_contents = contents(target)
        finally:
            target.close()
        collection = Collection(str(root / 'upgrade' / 'collection.anki2'))
        try:
            import_package(collection, args.original)
            before = {}
            for index, cid in enumerate(collection.find_cards('')):
                card = collection.get_card(cid)
                card.type = 2
                card.queue = 2
                card.ivl = 17 + index % 9
                card.due = 30 + index % 7
                card.factor = 2500
                card.reps = 4 + index % 5
                card.lapses = index % 3
                card.memory_state = FsrsMemoryState(stability=12.25 + index % 5, difficulty=5.125)
                card.desired_retention = 0.9
                collection.update_card(card)
                before[card.note().guid] = schedule(collection.get_card(cid))
            old_schemas = contents(collection)[1]
            import_package(collection, args.updated)
            if collection.card_count() != expected:
                raise ValueError('Upgrade duplicates or loses cards')
            after = {card.note().guid: card for card in
                     (collection.get_card(cid) for cid in collection.find_cards(''))}
            for guid, original_schedule in before.items():
                if schedule(after[guid]) != original_schedule:
                    raise ValueError(f'{guid}: identity or scheduling changed')
            actual_contents = contents(collection)
            if actual_contents != target_contents:
                raise ValueError('Upgrade did not apply the target notes, image bytes or rendering schema')
            for mid, old_schema in old_schemas.items():
                new_schema = actual_contents[1][mid]
                if [f[1] for f in new_schema['fields']] != [f[1] for f in old_schema['fields']]:
                    raise ValueError('Upgrade changed field identities')
                if [t[0] for t in new_schema['templates']] != [t[0] for t in old_schema['templates']]:
                    raise ValueError('Upgrade changed template identities')
            if collection.media.check().missing:
                raise ValueError('Missing upgrade media')
            for card in after.values():
                if not card.question().strip() or not card.answer().strip():
                    raise ValueError('Empty upgraded render')
            result = {'original': args.original.name, 'updated': args.updated.name,
                      'before': len(before), 'after': expected, 'added': expected - len(before),
                      'everyOldCardIDAndSchedulePreserved': True, 'FSRSMemoryPreserved': True,
                      'fieldAndTemplateIDsPreserved': True, 'targetContentAndMediaApplied': True,
                      'allSidesRender': True, 'missingMedia': 0}
            args.output.write_text(json.dumps(result, indent=2) + '\n')
            print(json.dumps(result))
        finally:
            collection.close()


if __name__ == '__main__':
    main()
