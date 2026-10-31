"""Whole-polygon regional partitioning rejects missing or overlapping targets."""
import importlib.util
from pathlib import Path
import sys
import unittest

from shapely.geometry import box

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('prepare_maps', ROOT / 'scripts/maps/prepare.py')
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)


class NamedRegionPartition(unittest.TestCase):
    def setUp(self):
        self.parts = [box(0, 0, 1, 1), box(10, 0, 11, 1), box(10, 2, 11, 3)]
        self.groups = [{'bounds': [-1, -1, 2, 2]}, {'bounds': [9, -1, 12, 4]}]

    def test_partition_preserves_entire_source_polygons(self):
        before = [part.wkt for part in self.parts]
        self.assertEqual(prepare.grouped_indices(self.parts, self.groups), [[0], [1, 2]])
        self.assertEqual([part.wkt for part in self.parts], before)

    def test_unassigned_land_fails(self):
        with self.assertRaisesRegex(ValueError, 'omit'):
            prepare.grouped_indices(self.parts, self.groups[:1])

    def test_overlapping_assignment_fails(self):
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            prepare.grouped_indices(self.parts, self.groups + [self.groups[0]])

    def test_empty_named_group_fails(self):
        with self.assertRaisesRegex(ValueError, 'Empty'):
            prepare.grouped_indices(self.parts, self.groups + [{'bounds': [30, 30, 40, 40]}])


if __name__ == '__main__':
    unittest.main()
