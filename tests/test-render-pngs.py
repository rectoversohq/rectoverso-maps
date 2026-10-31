"""Exercise process recovery without depending on an intermittent WebKit failure."""
import importlib.util
import os
from pathlib import Path
import sys
import shlex
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('render_pngs', Path(__file__).resolve().parents[1] / 'scripts/maps/render-pngs.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class RenderRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / 'CAN.svg'
        self.source.write_text('<svg/>')
        self.destination = self.source.with_suffix('.png')
        self.counter = self.root / 'attempts'
        self.converter = self.root / 'converter'
        program = self.root / 'converter.py'
        self.converter.write_text('#!/bin/sh\nexec ' + shlex.quote(sys.executable) + ' ' + shlex.quote(str(program)) + ' "$@"\n')
        program.write_text('''import os, sys, time
from pathlib import Path
counter = Path(os.environ['RENDER_TEST_COUNTER'])
n = int(counter.read_text()) + 1 if counter.exists() else 1
counter.write_text(str(n))
out = Path(sys.argv[1]) / Path(sys.argv[3]).with_suffix('.png').name
mode = os.environ['RENDER_TEST_MODE']
if mode == 'timeout': time.sleep(10)
if mode == 'empty': sys.exit(0)
if mode == 'fail' or (mode == 'recover' and n == 1):
    out.write_bytes(b'partial')
    sys.exit(1)
out.write_bytes(b'complete')
''')
        self.converter.chmod(0o755)

    def run_render(self, mode, **kwargs):
        with patch.dict(os.environ, RENDER_TEST_COUNTER=str(self.counter), RENDER_TEST_MODE=mode):
            renderer.render(self.converter, self.source, self.destination, 900, **kwargs)

    def test_fresh_process_recovers_without_reusing_partial_png(self):
        self.run_render('recover')
        self.assertEqual(self.counter.read_text(), '2')
        self.assertEqual(self.destination.read_bytes(), b'complete')
        self.assertEqual(list(self.root.glob('.render-*')), [])

    def test_persistent_failure_is_bounded_and_leaves_no_png(self):
        with self.assertRaises(RuntimeError): self.run_render('fail')
        self.assertEqual(self.counter.read_text(), '3')
        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.root.glob('.render-*')), [])

    def test_success_without_png_is_failure(self):
        with self.assertRaises(RuntimeError): self.run_render('empty')
        self.assertFalse(self.destination.exists())

    def test_timeout_is_bounded(self):
        with self.assertRaises(RuntimeError): self.run_render('timeout', attempts=2, timeout=0.2)
        self.assertEqual(self.counter.read_text(), '2')
        self.assertFalse(self.destination.exists())

    def test_existing_png_cannot_hide_failure(self):
        self.destination.write_bytes(b'old')
        with self.assertRaises(FileExistsError): self.run_render('fail')
        self.assertEqual(self.destination.read_bytes(), b'old')
        self.assertFalse(self.counter.exists())


if __name__ == '__main__':
    unittest.main()
