import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts/checks/verify-covers.py"
sys.path.insert(0, str(ROOT / "scripts"))
from covers import render_covers


class CoverRenderer(unittest.TestCase):
    def test_incompatible_master_aspect_ratio_leaves_no_jpg(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            masters = root / "masters"
            masters.mkdir()
            (masters / "rv-map-cover-1.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" '
                'width="100" height="100" viewBox="0 0 100 100">'
                '<rect width="100" height="100" fill="#211e18"/></svg>'
            )
            output = root / "output"
            with patch("covers.MASTERS", masters):
                with self.assertRaisesRegex(ValueError, "3:2 viewport"):
                    render_covers(output)
            self.assertEqual(list(output.glob("*.jpg")), [])


class CoverCheck(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.output = Path(temporary.name)
        self.add_cover("rv-map-cover-1.jpg")

    def add_cover(self, name, size=(2010, 1340), mark=None):
        with Image.new("RGB", size, "#202020") as image:
            if mark is not None:
                point, color = mark
                image.putpixel(point, color)
            image.save(self.output / name, format="JPEG", quality=100, subsampling=0)

    def check(self):
        return subprocess.run(
            [sys.executable, str(CHECK), "--output", str(self.output)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_shared_covers_supply_both_languages(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def assert_rejected(self, message):
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr)

    def test_wrong_dimensions_are_rejected(self):
        self.add_cover("rv-map-cover-1.jpg", size=(2010, 1339))
        self.assert_rejected("must be a 2010 × 1340 JPEG")

    def test_invalid_names_are_rejected(self):
        for name in (
            "rv-map-cover-LIGHT-2.jpg",
            "rv-map-cover-dark-0.jpg",
            "rv-map-de-cover-dark-2.jpg",
            "rv-map-cover-dark-2.JPG",
        ):
            with self.subTest(name=name):
                self.add_cover(name)
                self.assert_rejected(f"Invalid cover filename: {name}")
                (self.output / name).unlink()

    def test_missing_appearance_is_rejected(self):
        (self.output / "rv-map-cover-1.jpg").unlink()
        self.add_cover("rv-map-cover-light-1.jpg")
        self.assert_rejected("en missing cover appearances: dark")

    def test_worded_cover_requires_every_language_at_the_same_number_and_appearance(self):
        self.add_cover("rv-map-en-cover-dark-2.jpg")
        self.add_cover("rv-map-fr-cover-dark-3.jpg")
        self.add_cover("rv-map-fr-cover-light-2.jpg")
        self.assert_rejected("Worded cover dark-2 missing languages: fr")

    def test_fully_localized_set_supplies_both_appearances(self):
        for path in self.output.iterdir():
            path.unlink()
        for language in ("en", "fr"):
            for appearance in ("light", "dark"):
                self.add_cover(f"rv-map-{language}-cover-{appearance}-1.jpg")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_artwork_at_the_inclusive_corner_boundary_is_rejected(self):
        self.add_cover(
            "rv-map-cover-1.jpg", mark=((1608, 335), (237, 230, 216))
        )
        self.assert_rejected("has artwork in the language-pill corner")

    def test_minor_background_variation_and_art_outside_the_corner_are_allowed(self):
        self.add_cover(
            "rv-map-cover-4.jpg", mark=((1608, 335), (34, 34, 34))
        )
        self.add_cover(
            "rv-map-cover-1.jpg", mark=((1608, 344), (237, 230, 216))
        )
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_explicit_appearances_remain_supported(self):
        (self.output / "rv-map-cover-1.jpg").unlink()
        for appearance in ("light", "dark"):
            self.add_cover(f"rv-map-cover-{appearance}-1.jpg")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_localized_shared_appearance_covers_supply_both_modes(self):
        (self.output / "rv-map-cover-1.jpg").unlink()
        for language in ("en", "fr"):
            self.add_cover(f"rv-map-{language}-cover-2.jpg")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_shared_appearance_worded_cover_requires_matching_localization(self):
        self.add_cover("rv-map-en-cover-2.jpg")
        for appearance in ("light", "dark"):
            self.add_cover(f"rv-map-fr-cover-{appearance}-2.jpg")
        self.assert_rejected("Worded cover None-2 missing languages: fr")

    def test_mixed_shared_and_explicit_appearance_is_rejected(self):
        self.add_cover("rv-map-cover-light-1.jpg")
        self.assert_rejected("Ambiguous appearance scope")

    def test_mixed_appearances_in_one_localized_language_are_rejected(self):
        for language in ("en", "fr"):
            self.add_cover(f"rv-map-{language}-cover-2.jpg")
        self.add_cover("rv-map-en-cover-dark-2.jpg")
        self.assert_rejected("Ambiguous appearance scope")

    def test_mixed_shared_and_localized_number_is_rejected(self):
        for appearance in ("", "-light", "-dark"):
            name = f"rv-map-en-cover{appearance}-1.jpg"
            with self.subTest(name=name):
                self.add_cover(name)
                self.assert_rejected("Ambiguous language scope")
                (self.output / name).unlink()
