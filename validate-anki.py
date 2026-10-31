"""Validate original and RectoVerso-exported packages with Anki's own library."""
import argparse
import json
from pathlib import Path
import re
import tempfile
from anki.collection import Collection
from anki.import_export_pb2 import ImportAnkiPackageRequest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('packages', nargs='+', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    results = []
    for package in args.packages:
        metadata = json.loads(package.with_suffix('.rectoverso.json').read_text())
        expected = metadata['cards']
        with tempfile.TemporaryDirectory(prefix='anki-check-', dir=args.output) as temporary:
            col = Collection(str(Path(temporary) / 'collection.anki2'))
            try:
                col.import_anki_package(ImportAnkiPackageRequest(package_path=str(package)))
                if col.card_count() != expected:
                    raise ValueError(f'{package}: expected {expected} cards, found {col.card_count()}')
                guids = []
                for cid in col.find_cards(''):
                    card = col.get_card(cid)
                    guids.append(card.note().guid)
                    front, back = card.question(), card.answer()
                    if not re.search(r'<img\b', front) or not re.search(r'<img\b', back):
                        raise ValueError(f'{package}: card {cid} lacks its image')
                    if '<hr' not in back or not re.sub(r'<[^>]*>', '', back.split('<hr', 1)[1]).strip():
                        raise ValueError(f'{package}: card {cid} has no answer')
                    if '"outline"' in front + back:
                        raise ValueError(f'{package}: card {cid} exposes place metadata')
                if len(set(guids)) != expected or col.media.check().missing:
                    raise ValueError(f'{package}: duplicate GUIDs or missing media')
                cid = col.find_cards('')[0]
                card = col.get_card(cid)
                card.type, card.queue, card.ivl, card.due, card.factor, card.reps = 2, 2, 17, 30, 2500, 4
                col.update_card(card)
                col.import_anki_package(ImportAnkiPackageRequest(package_path=str(package)))
                kept = col.get_card(cid)
                if col.card_count() != expected or (kept.type, kept.queue, kept.ivl, kept.due, kept.reps) != (2, 2, 17, 30, 4):
                    raise ValueError(f'{package}: repeat import changed cards or progress')
                result = {'package': package.name, 'cards': expected, 'renderedSides': expected * 2,
                          'missingMedia': 0, 'uniqueGUIDs': len(set(guids)), 'progressPreserved': True}
                results.append(result)
                print(json.dumps(result))
            finally:
                col.close()
    (args.output / 'anki-validation.json').write_text(json.dumps(results, indent=2) + '\n')

if __name__ == '__main__':
    main()
