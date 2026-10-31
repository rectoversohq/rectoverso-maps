"""Make an Anki package from this repository's tracked notes, template and media."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from anki.collection import Collection, ExportAnkiPackageOptions
from anki.decks import DeckId
from source_data import inputs, read

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--language', required=True, choices=tuple(read('rectoverso.json')['languages']))
    args = parser.parse_args()
    metadata, notes, model, deck = inputs(args.language)
    source = metadata['sourceFiles']
    args.out = args.out.resolve()
    if args.out.is_relative_to(ROOT) or args.out.exists() or args.out.with_suffix('.rectoverso.json').exists():
        raise ValueError('Use a new package path outside the source repository')
    if args.out.name != metadata['package']['file']:
        raise ValueError('Output filename differs from the language artifact name')
    if len(notes) != metadata['cards'] or len({n['guid'] for n in notes}) != len(notes):
        raise ValueError('Source note count or GUIDs disagree with metadata')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='anki-build-', dir=args.out.parent) as temporary:
        col = Collection(str(Path(temporary) / 'collection.anki2'))
        try:
            note_type = col.models.new(model['name'])
            for name in model['fields']:
                field = col.models.new_field(name)
                field['id'] = model['fieldIDs'][name]
                col.models.add_field(note_type, field)
            for template in model['templates']:
                entry = col.models.new_template(template['name'])
                entry.update(template)
                col.models.add_template(note_type, entry)
            note_type.update(id=model['id'], css=model['css'])
            col.models.update(note_type)
            if col.models.by_name(model['name'])['id'] != model['id']:
                raise ValueError('Anki changed the stable note-type id')
            entry = col.decks.new_deck_legacy(False)
            entry.update(id=deck['id'], name=deck['name'], desc=deck['description'])
            col.decks.update(entry)
            for source_note in notes:
                note = col.new_note(note_type)
                note.guid = source_note['guid']
                for name, value in source_note['fields'].items():
                    note[name] = value
                note.tags = source_note['tags']
                col.add_note(note, DeckId(deck['id']))
            for credit in metadata['imageCredits']:
                name = credit['file']
                if Path(name).name != name:
                    raise ValueError('Media filenames must be basenames')
                shutil.copyfile(ROOT / source['pictures'] / name, Path(col.media.dir()) / name)
            if col.card_count() != metadata['cards']:
                raise ValueError('Generated card count disagrees with metadata')
            col.export_anki_package(out_path=str(args.out),
                options=ExportAnkiPackageOptions(with_scheduling=False, with_media=True), limit=None)
        finally:
            col.close()
    metadata['package'] = metadata['package'] | {'file': args.out.name, 'bytes': args.out.stat().st_size,
                           'sha256': hashlib.sha256(args.out.read_bytes()).hexdigest()}
    args.out.with_suffix('.rectoverso.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(metadata['package']))

if __name__ == '__main__':
    main()
