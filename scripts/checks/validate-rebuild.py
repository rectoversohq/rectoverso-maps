"""Check an independently rebuilt package preserves source ids and scheduled progress.

Python 3.14+, Anki 26.09.3. Usage: validate-rebuild.py ORIGINAL REBUILT OUTPUT.json
"""
from compression import zstd
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import zipfile
from anki.collection import Collection
from anki.import_export_pb2 import ImportAnkiPackageRequest

original, rebuilt, output = map(Path, sys.argv[1:])
def identities(package, temporary):
    with zipfile.ZipFile(package) as archive:
        data = zstd.decompress(archive.read('collection.anki21b'))
    dbpath = temporary / (package.stem + '-inspect.sqlite')
    dbpath.write_bytes(data)
    with sqlite3.connect(dbpath) as db:
        result = {'guids': sorted(x[0] for x in db.execute('select guid from notes')),
                  'models': sorted(x[0] for x in db.execute('select distinct mid from notes')),
                  'decks': sorted(x[0] for x in db.execute('select distinct did from cards'))}
    with tempfile.TemporaryDirectory(prefix='schema-', dir=temporary) as directory:
        col = Collection(str(Path(directory) / 'collection.anki2'))
        try:
            col.import_anki_package(ImportAnkiPackageRequest(package_path=str(package)))
            result['schemas'] = [
                {'id': model['id'], 'fields': [(f['name'], f['id']) for f in model['flds']],
                 'templates': [(t['name'], t['id']) for t in model['tmpls']]}
                for model in sorted(col.models.all(), key=lambda m: m['id'])
                if model['id'] in result['models']]
        finally:
            col.close()
    return result
output.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='rebuild-check-', dir=output.parent) as directory:
    temporary = Path(directory)
    before, after = identities(original, temporary), identities(rebuilt, temporary)
    assert before == after, 'A rebuilt source changed deck/model ids or note GUIDs'
    col = Collection(str(temporary / 'collection.anki2'))
    try:
        col.import_anki_package(ImportAnkiPackageRequest(package_path=str(original)))
        count = col.card_count()
        cards = col.find_cards('')
        card = col.get_card(cards[0]); guid = card.note().guid
        card.type=2; card.queue=2; card.ivl=17; card.due=30; card.factor=2500; card.reps=4
        col.update_card(card)
        decks = sorted(x[0] for x in col.db.all('select distinct did from cards'))
        col.import_anki_package(ImportAnkiPackageRequest(package_path=str(rebuilt)))
        assert col.card_count() == count
        assert sorted(col.find_cards('')) == sorted(cards)
        assert sorted(x[0] for x in col.db.all('select distinct did from cards')) == decks
        kept=col.get_card(card.id)
        assert kept.note().guid == guid
        assert (kept.type,kept.queue,kept.ivl,kept.due,kept.reps)==(2,2,17,30,4)
        result={'original':original.name,'rebuilt':rebuilt.name,'cards':count,
                'sourceDeckIDs':before['decks'],'sourceModelIDs':before['models'],
                'GUIDsStable':True,'sourceIDsStable':True,'fieldAndTemplateIDsStable':True,'cardIDsStable':True,
                'noDuplicateDeck':True,'scheduledProgressPreserved':True}
        output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
    finally: col.close()
