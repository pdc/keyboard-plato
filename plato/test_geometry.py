# -* coding: UTF-8 -*-

"""Tests for geometry stuff."""

from __future__ import print_function, unicode_literals
import unittest

from .geometry import (
    adjusted_coords, flip_clockwise, translate, rect_points, merge_shapes,
    segment_intersection, nearest_intersections, leftmost_turn, are_colinear,
    segments, screw_points)


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

    def test_not_confused_by_overlapping_line_segments(self):
        """Test merge shapes is nit confused by overapping line segments."""
        # This should create an L-shape.
        self.assertEqual(
            merge_shapes(
                rect_points((2, 3), (4, 2)),
                rect_points((3, 2), (2, 4))),
            [(0, 2), (0, 4), (4, 4), (4, 0), (2, 0), (2, 2)]
        )

    def test_gamma(self):
        """Test merge shapes is nit confused by overapping line segments."""
        # This should create an gamma-shape.
        self.assertEqual(
            merge_shapes(
                rect_points((2, 3), (4, 2)),
                rect_points((1, 2), (2, 4))),
            [(0, 0), (0, 4), (4, 4), (4, 2), (2, 2), (2, 0)]
        )

    def test_another_elle(self):
        """Test merge shapes on another L."""
        # This should create an L-shape.
        self.assertEqual(
            merge_shapes(
                rect_points((2, 1), (4, 2)),
                rect_points((3, 2), (2, 4))),
            [(0, 0), (0, 2), (2, 2), (2, 4), (4, 4), (4, 0)]
        )

    def test_actual_elle(self):
        """Test merge shapes on actual L."""
        # This should create an L-shape.
        self.assertEqual(
            merge_shapes(
                rect_points((2, 1), (4, 2)),
                rect_points((1, 2), (2, 4))),
            [(0, 0), (0, 4), (2, 4), (2, 2), (4, 2), (4, 0)]
        )


class TestScrewHoles(unittest.TestCase):
    """Test screw_points."""

    def test_places_four_scres_at_corners(self):
        """Test screw_points places four screws at corners."""
        self.assertEqual(set(screw_points(4, (90, 50))), {(-45, -25), (45, -25), (45, 25), (-45, 25)})

    def test_adds_screws_to_top_and_bottom_with_six(self):
        """Test screw_points places four screws at corners."""
        self.assertEqual(set(screw_points(6, (90, 50))), {
            (0, -25), (0, 25),
            (-45, -25), (45, -25), (45, 25), (-45, 25)})


class TestSegmentIntersection(unittest.TestCase):
    """Test segment_intersection."""

    def test_finds_point(self):
        """Test segment_intersection finds intersection in simple case."""
        self.assertEqual(
            segment_intersection(((0, 0), (4, 2)), ((3, 0), (3, 3))),
            (0.75, (3, 1.5))
        )

    def test_doesnt_find_nonintersection(self):
        """Test segment_intersection doesnt find non-intersection."""
        t, z = segment_intersection(((0, 2), (2, 3)), ((0, 5), (2, 4)))
        self.assertFalse(t)

    def test_finds_match_at_start_point(self):
        """Test segment_intersection doesnt find intersection with start point."""
        t, z = segment_intersection(((0, 0), (1, 1)), ((0, -1), (0, 1)))
        self.assertEqual(t, 0)

    def test_does_find_intersection_at_end_of_first_line(self):
        """Test segment_intersection does find intersection at end of first line."""
        t, z = segment_intersection(((0, 0), (1, 1)), ((1, -1), (1, 2)))
        self.assertEqual(t, 1)
        x, y = z
        self.assertAlmostEqual(x, 1)
        self.assertAlmostEqual(y, 1)


class TestNearestIntersections(unittest.TestCase):
    """Test nearest_intersections."""

    def test_finds_multiple_lines_endpoints(self):
        """Test nearest_intersections finds multiple lines’ endpoints."""
        z, zs = nearest_intersections(((1, 2), (5, 2)), {((2, 0), (4, 4)), ((5, 0), (5, 4)), ((2, 4), (4, 0))})
        self.assertEqual(z, (3, 2))  # The intersection
        self.assertEqual(zs, {(2, 4), (2, 0), (4, 4), (4, 0), (5, 2)})  # Endpoints of the intersected lines.

    def test_finds_one_endpoint_if_intersecting_at_vertex(self):
        """Test nearest_intersections finds one endpoint if intersecting at a vertex."""
        z, zs = nearest_intersections(((1, 2), (5, 2)), {((2, 0), (3, 2))})
        self.assertEqual(z, (3, 2))  # The intersection
        self.assertEqual(zs, {(2, 0), (5, 2)})  # Endpoint of the intersected line.

    def test_finds_own_extrapolation(self):
        """Test nearest_intersections finds its own extrapolation."""
        z, zs = nearest_intersections(((4, 4), (4, 0)), {((0, 2), (4, 2)), ((0, 0), (4, 0)), ((2, 0), (4, 0))})
        self.assertEqual(z, (4, 2))
        self.assertEqual(zs, {(4, 0), (0, 2)})


class TestLeftmostTurn(unittest.TestCase):
    """Test leftmost_turn."""

    def test_chooses_only_option(self):
        """Test leftmost_turn chooses only option."""
        z2, z3 = leftmost_turn(((0, 2), (4, 2)), (3, 2), {(3, 5)})
        self.assertEqual(z2, (3, 2))  # The intersection.
        self.assertEqual(z3, (3, 5))  # THe endpoint.

    def test_chooses_up_if_going_right(self):
        """Test leftmost_turn chooses only option."""
        z2, z3 = leftmost_turn(((0, 2), (4, 2)), (3, 2), {(3, 5), (5, 5), (3, 0)})
        self.assertEqual(z2, (3, 2))
        self.assertEqual(z3, (3, 5))

    def test_chooses_right_if_headed_down(self):
        """Test leftmost_turn chooses right if headed down."""
        z0, z1 = leftmost_turn(((1, 3), (1, -3)), (1, 1), {(-2, 1), (2, 1)})
        self.assertEquals(z0, (1, 1))
        self.assertEquals(z1, (2, 1))

    def test_chooses_down_if_headed_left(self):
        """Test leftmost_turn chooses right if headed down."""
        z0, z1 = leftmost_turn(((2, -1), (-2, -1)), (1, -1), {(1, -3), (1, 3)})
        self.assertEquals(z0, (1, -1))
        self.assertEquals(z1, (1, -3))

    def test_doesnt_got_backwards(self):
        """Test leftmost_turn doesn’t go backwards."""
        z0, z1 = leftmost_turn(((4, 2), (4, 0)), (4, 2), {(4, 0), (2, 2)})
        self.assertEquals(z0, (4, 2))
        self.assertEquals(z1, (4, 0))

    def test_chooses_longest_option(self):
        """Test leftmost_turn choose3s longest option."""
        z0, z1 = leftmost_turn(((2, 4), (4, 4)), (4, 4), [(4, 2), (4, 0), (4, 1)])
        self.assertEqual(z0, (4, 4))
        self.assertEqual(z1, (4, 0))


class TestAreColinear(unittest.TestCase):
    """Test are_colinear."""

    def test_is_yes_if_point_on_line(self):
        """Test are_colinear is yes if point is on line."""
        self.assertTrue(are_colinear((0, 1), (2, 1), (4, 1)))

    def test_is_no_if_point_not_on_line(self):
        """Test are_colinear is yes if point is on line."""
        self.assertFalse(are_colinear((0, 1), (2, 1), (2, 5)))

    def test_is_yes_if_point_on_vertical_line(self):
        """Test are_colinear is yes if point is on line."""
        self.assertTrue(are_colinear((3, 1), (3, 5), (3, 10)))

    def test_is_no_if_point_not_on_vertical_line(self):
        """Test are_colinear is yes if point is on line."""
        self.assertFalse(are_colinear((3, 1), (5, 8), (3, 10)))


