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


if __name__ == '__main__':
    unittest.main()
