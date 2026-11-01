"""Exercise update hazards that a pair of builds from the same source cannot catch."""
import copy
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('identities', Path(__file__).resolve().parents[1] / 'scripts/checks/check-identities.py')
identities = importlib.util.module_from_spec(spec)
spec.loader.exec_module(identities)


class UpdateIdentities(unittest.TestCase):
    def setUp(self):
        self.before = {'deck': 'maps', 'languages': {'en': {
            'artifact': 'maps-en', 'deck': 1, 'model': 2, 'fields': [3, 4],
            'templates': [5], 'guids': {'ITA': 'italy', 'FRA': 'france'}}}}
        self.after = copy.deepcopy(self.before)

    def test_guid_replacement_and_retirement_fail(self):
        for guids in ({'ITA': 'changed', 'FRA': 'france'}, {'ITA': 'italy'}):
            self.after['languages']['en']['guids'] = guids
            with self.assertRaisesRegex(ValueError, 'GUID changed'):
                identities.compare(self.before, self.after)

    def test_schema_and_deck_changes_fail(self):
        for key in ('artifact', 'deck', 'model', 'fields', 'templates'):
            with self.subTest(key=key):
                self.after = copy.deepcopy(self.before)
                self.after['languages']['en'][key] = 'changed'
                with self.assertRaisesRegex(ValueError, 'identities changed'):
                    identities.compare(self.before, self.after)

    def test_append_only_fields_keep_existing_identities(self):
        self.after['languages']['en']['fields'] += [6, 7]
        self.assertTrue(identities.compare(self.before, self.after)['existingIdentitiesPreserved'])
        for bad in ([4, 3, 6], [3, 6], [3, 4, 3]):
            self.after['languages']['en']['fields'] = bad
            with self.assertRaisesRegex(ValueError, 'fields identities changed'):
                identities.compare(self.before, self.after)

    def test_language_removal_fails(self):
        self.after['languages'].clear()
        with self.assertRaisesRegex(ValueError, 'language removed'):
            identities.compare(self.before, self.after)

    def test_additions_are_reported(self):
        self.after['languages']['en']['guids']['BEL'] = 'belgium'
        self.after['languages']['fr'] = copy.deepcopy(self.after['languages']['en'])
        result = identities.compare(self.before, self.after)
        self.assertEqual(result['addedPlaces'], {'en': ['BEL']})
        self.assertEqual(result['addedLanguages'], ['fr'])


if __name__ == '__main__':
    unittest.main()
