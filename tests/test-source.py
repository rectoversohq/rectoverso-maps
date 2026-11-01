"""Reject damaged multilingual source before producing an installable package."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import source_data

spec = importlib.util.spec_from_file_location('coverage_check', Path(__file__).resolve().parents[1] / 'scripts/checks/verify-coverage.py')
coverage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coverage)


class MultilingualSourceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        shutil.copytree(source_data.ROOT / 'source', self.root / 'source')
        shutil.copyfile(source_data.ROOT / 'rectoverso.json', self.root / 'rectoverso.json')
        self.addCleanup(patch.stopall)
        patch.object(source_data, 'ROOT', self.root).start()
        patch.object(coverage, 'ROOT', self.root).start()

    def edit(self, name, mutate):
        path = self.root / name
        value = json.loads(path.read_text())
        mutate(value)
        path.write_text(json.dumps(value))

    def check(self):
        with contextlib.redirect_stdout(io.StringIO()):
            coverage.main()

    def test_missing_country_is_rejected(self):
        self.edit('source/geography/coverage.json', lambda value: value['entries'].pop())
        with self.assertRaisesRegex(ValueError, 'roster'):
            self.check()

    def test_changed_learner_name_is_rejected(self):
        self.edit('source/places.json', lambda value: value[0]['name'].update(fr='Incorrect'))
        with self.assertRaisesRegex(ValueError, 'learner names'):
            self.check()

    def test_colliding_model_identity_is_rejected(self):
        model = source_data.read('source/languages/en/note-type.json')['id']
        self.edit('source/languages/fr/note-type.json', lambda value: value.update(id=model))
        with self.assertRaisesRegex(ValueError, 'collide'):
            self.check()

    def test_unknown_boundary_note_is_rejected(self):
        self.edit('source/languages/fr/translation.json', lambda value: value['boundaryNotes'].update(XXX='Invalid'))
        with self.assertRaisesRegex(ValueError, 'unknown place'):
            self.check()

    def test_external_language_source_is_rejected(self):
        self.edit('rectoverso.json', lambda value: value['languages']['fr']['sourceFiles'].update(deck='../outside.json'))
        with self.assertRaisesRegex(ValueError, 'leaves the repository'):
            self.check()

    def test_missing_picture_is_rejected(self):
        next((self.root / 'source/media').glob('*.png')).unlink()
        with self.assertRaisesRegex(ValueError, 'image'):
            self.check()

    def test_wrong_release_repository_is_rejected(self):
        self.edit('rectoverso.json', lambda value: value['languages']['fr']['package'].update(url='https://example.com/wrong.apkg'))
        with self.assertRaisesRegex(ValueError, 'Artifact URL'):
            self.check()

    def test_missing_supplementary_group_is_rejected(self):
        self.edit('source/geography/coverage.json', lambda value: value['supplementaryEntries'].pop())
        with self.assertRaisesRegex(ValueError, 'Supplementary'):
            self.check()

    def test_regional_code_cannot_claim_iso_namespace(self):
        self.edit('source/geography/regional-questions.json', lambda value: value['questions'][0].update(codeNamespace='ISO-3166-1-alpha3'))
        with self.assertRaisesRegex(ValueError, 'regional identity'):
            self.check()

    def test_changed_regional_name_is_rejected(self):
        def change(value):
            next(row for row in value if row.get('parentCode'))['name']['en'] = 'Wrong island'
        self.edit('source/places.json', change)
        with self.assertRaisesRegex(ValueError, 'approved regional source'):
            self.check()

    def test_swapping_regional_geometries_is_rejected(self):
        def swap(value):
            first, second = [row for row in value if row.get('parentCode') == 'PRT']
            a, b = json.loads(first['field']), json.loads(second['field'])
            a['outline'], b['outline'] = b['outline'], a['outline']
            first['field'], second['field'] = json.dumps(a), json.dumps(b)
        self.edit('source/places.json', swap)
        with self.assertRaisesRegex(ValueError, 'named source group'):
            self.check()

    def test_lost_core_polygon_is_rejected(self):
        def remove(value):
            row = next(row for row in value if row['code'] == 'FRA')
            field = json.loads(row['field'])
            field['outline']['coordinates'].pop()
            row['field'] = json.dumps(field)
        self.edit('source/places.json', remove)
        with self.assertRaisesRegex(ValueError, 'named source group'):
            self.check()

    def test_total_question_count_is_not_iso_count(self):
        self.edit('source/geography/coverage.json', lambda value: value.update(referenceCount=288))
        with self.assertRaisesRegex(ValueError, 'Coverage count'):
            self.check()


    def test_continent_search_is_localized_and_keeps_cross_continent_membership(self):
        for lang in ('en', 'fr'):
            _, notes, _, _ = source_data.inputs(lang)
            by_guid = {n['guid']:n for n in notes}
            russia = by_guid[f'rv-map-{lang}-rus']['fields']
            query = json.loads(russia['RectoVerso search'])
            self.assertEqual(query['v'], 1)
            self.assertEqual(query['fields'][0]['values'], ['Europe', 'Asia' if lang == 'en' else 'Asie'])
            self.assertIn('Asie', query['fields'][0]['aliases'])
            self.assertIn('Asia', query['fields'][0]['aliases'])
        assignments = source_data.read('source/geography/continents.json')['assignments']
        self.assertEqual(assignments['FRA'], ['EU'])
        self.assertEqual(assignments['MAPS-FRA-CLIPPERTON-ISLAND'], ['NA'])
        self.assertEqual(assignments['MAPS-PRT-MADEIRA'], ['AF'])
        self.assertEqual(assignments['MAPS-UMI-NAVASSA-ISLAND'], ['NA'])
        self.assertEqual(assignments['MAPS-UMI-WAKE-ATOLL'], ['OC'])

    def test_missing_continent_or_unknown_membership_is_rejected(self):
        self.edit('source/geography/continents.json', lambda v: v['assignments'].pop('FRA'))
        with self.assertRaisesRegex(ValueError, 'Continent coverage'):
            self.check()

    def test_card_kind_matches_the_existing_app_mapping(self):
        self.edit('rectoverso.json', lambda value: value['cardKinds'][0].update(en='Map → Place'))
        with self.assertRaisesRegex(ValueError, 'Card kind differs'):
            self.check()


if __name__ == '__main__':
    unittest.main()
