"""Record Anki's default schema-upgrade result without claiming it is supported."""
import argparse
import json
from pathlib import Path
import tempfile
from anki.collection import Collection
from anki.import_export_pb2 import ImportAnkiPackageOptions, ImportAnkiPackageRequest


def load(collection, package):
    result = collection.import_anki_package(ImportAnkiPackageRequest(
        package_path=str(package.resolve()),
        options=ImportAnkiPackageOptions(merge_notetypes=True, with_scheduling=True)))
    collection.models._clear_cache()
    return result


def snapshot(collection):
    return {note.guid: {'mid': note.mid, 'fields': note.fields,
                       'noteModified': note.mod,
                       'modelModified': collection.models.get(note.mid)['mod']}
            for note in (collection.get_note(nid) for nid in collection.find_notes(''))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('updated', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='default-control-', dir=args.output.parent) as temp:
        root = Path(temp)
        (root / 'target').mkdir()
        target = Collection(str(root / 'target' / 'collection.anki2'))
        try:
            load(target, args.updated)
            expected = snapshot(target)
        finally:
            target.close()
        (root / 'upgrade').mkdir()
        collection = Collection(str(root / 'upgrade' / 'collection.anki2'))
        try:
            load(collection, args.original)
            before = snapshot(collection)
            result = load(collection, args.updated)
            actual = snapshot(collection)
            if set(actual) != set(expected):
                raise ValueError('Default import changed the identity roster unexpectedly')
            applied = all(actual[g]['fields'] == expected[g]['fields'] for g in expected)
            missing = [g for g in before if actual[g]['fields'] != expected[g]['fields']]
            if not applied:
                for guid in missing:
                    old, new, got = before[guid], expected[guid], actual[guid]
                    old_count = len(old['fields'])
                    if not (len(new['fields']) > old_count
                            and got['fields'][:old_count] == old['fields']
                            and all(not value for value in got['fields'][old_count:])
                            and new['noteModified'] > old['noteModified']
                            and new['modelModified'] > old['modelModified']
                            and got['noteModified'] >= new['noteModified']):
                        raise ValueError('Failure differs from the known append-only mtime limitation')
            guid = sorted(before)[0]
            evidence = {'mergeNoteTypes': True, 'updateExisting': 'if-newer',
                        'defaultContentApplied': applied, 'affectedOldNotes': len(missing),
                        'importedNewNotes': len(result.log.new),
                        'updatedNotes': len(result.log.updated),
                        'duplicates': len(result.log.duplicate),
                        'example': {name: {'noteModified': value[guid]['noteModified'],
                                          'modelModified': value[guid]['modelModified'],
                                          'fieldCount': len(value[guid]['fields'])}
                                    for name, value in [('published', before), ('candidate', expected), ('afterDefaultImport', actual)]},
                        'supportedMigration': 'Merge note types + Always update notes and note types',
                        'diagnosticPassed': True,
                        'meaning': 'A passing diagnostic documents this result; it is not a default-upgrade compatibility pass.'}
        finally:
            collection.close()
    args.output.write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence))


if __name__ == '__main__':
    main()
