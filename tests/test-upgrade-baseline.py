"""Reject substituted or malformed release-fixture locations before networking."""
import copy
import importlib.util
from pathlib import Path
import unittest

script = Path(__file__).resolve().parents[1] / 'scripts/checks/fetch-upgrade-baseline.py'
spec = importlib.util.spec_from_file_location('baseline', script)
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)


class PinnedUpgradeBaseline(unittest.TestCase):
    def setUp(self):
        self.value = {'version': '0.2.0-rc.2', 'languages': {
            language: {'file': language + '.apkg', 'bytes': 10, 'sha256': 'a' * 64,
                       'url': baseline.REPOSITORY + '/releases/download/v0.2.0-rc.2/' + language + '.apkg'}
            for language in ('en', 'fr')}}

    def test_public_frozen_reference_is_accepted(self):
        self.assertEqual(baseline.validate(self.value), self.value)

    def test_redirecting_or_substituting_the_declared_source_fails(self):
        for url in ('https://example.com/en.apkg', baseline.REPOSITORY + '/releases/download/latest/en.apkg'):
            with self.subTest(url=url):
                value = copy.deepcopy(self.value)
                value['languages']['en']['url'] = url
                with self.assertRaisesRegex(ValueError, 'URL/hash/size'):
                    baseline.validate(value)

    def test_path_escape_and_bad_digest_fail(self):
        for field, value in (('file', '../en.apkg'), ('sha256', 'unverified'), ('bytes', 0), ('bytes', True)):
            with self.subTest(field=field, value=value):
                changed = copy.deepcopy(self.value)
                changed['languages']['en'][field] = value
                with self.assertRaises(ValueError):
                    baseline.validate(changed)

    def test_missing_language_fails(self):
        del self.value['languages']['fr']
        with self.assertRaisesRegex(ValueError, 'both languages'):
            baseline.validate(self.value)


if __name__ == '__main__':
    unittest.main()
