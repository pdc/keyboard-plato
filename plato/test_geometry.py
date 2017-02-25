"""Tests for geometry stuff."""

from __future__ import print_function, unicode_literals
import unittest

from .geometry import (
    adjusted_coords, flip_clockwise, translate, rect_points, merge_shapes,
    segments, screw_holes)


class TestAdjustedCoords(unittest.TestCase):
    """Test adjusted_coords."""

    def test_adjusted_coords_expands_gap(self):
        """Test adjusted_coords expands gap."""
        left, right = adjusted_coords(13, 56, 2.5)

        self.assertAlmostEqual(left, 13 - 28 - 2.5)
        self.assertAlmostEqual(right, 13 + 28 + 2.5)


class TestFlipCLockwise(unittest.TestCase):
    """Test flip_clockwise."""

    def test_flip_clockwise(self):
        """Test flip_clockwise can flip a list of points clockwise."""
        self.assertEqual(
            flip_clockwise([(1, 2), (-2, -3)]),
            [(2, -1), (-3, 2)])


class TestTranslate(unittest.TestCase):
    """Test translate."""

    def test_translate(self):
        """Test translate can translate points."""
        self.assertEqual(
            translate((6, 7), [(1, 2), (-2, -3)]),
            [(7, 9), (4, 4)])


class TestSegments(unittest.TestCase):
    """Test segments."""

    def test_returns_lines_pointing_up_or_right(self):
        """Test segments returns lines pointing up or right."""
        self.assertEqual(
            set(segments(rect_points((0, 0), (2, 4)))),
            {
                ((-1., 2.), (1., 2.)),
                ((1., -2.), (1., 2.)),
                ((-1., -2.), (1., -2.)),  # up lhs
                ((-1., -2.), (-1., 2.)),  # right bot
            })


class TestMergeShapes(unittest.TestCase):
    """Test merge_shapes."""

    def test_makes_cross_from_two_rects(self):
        """Test merge_shapes rmakes a cross from two rects."""
        self.assertEqual(
            merge_shapes(rect_points((0, 0), (2, 6)), rect_points((0, 0), (4, 2))),
            [
                (-2, -1), (-2, 1), (-1, 1), (-1, 3), (1, 3), (1, 1), (2, 1),
                (2, -1), (1, -1), (1, -3), (-1, -3), (-1, -1),
            ]
        )


class TestScrewHoles(unittest.TestCase):
    """Test screw_holes."""

    def test_places_four_scres_at_corners(self):
        """Test screw_holes places four screws at corners."""
        self.assertEqual(set(screw_holes(4, (90, 50))), {(-45, -25), (45, -25), (45, 25), (-45, 25)})

    def test_adds_screws_to_top_and_bottom_with_six(self):
        """Test screw_holes places four screws at corners."""
        self.assertEqual(set(screw_holes(6, (90, 50))), {
            (0, -25), (0, 25),
            (-45, -25), (45, -25), (45, 25), (-45, 25)})

    def test_adds_on_all_sides_with_ten(self):
        """Test screw_holes places four screws at corners."""
        self.assertEqual(set(screw_holes(12, (90, 50))), {
            (-45, 0), (45, 0),
            (-15, -20), (15, -20), (-15, 20), (15, 20),
            (-45, -20), (45, -20), (45, 20), (-45, 20)})
