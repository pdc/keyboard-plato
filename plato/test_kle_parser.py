# -* coding: UTF-8 -*-

"""Tests for kle_parser."""

import unittest

from .kle_parser import parse_kle, _json_from_kle


class TestJsonFromKle(unittest.TestCase):
    """Test json_from_kle."""

    def test_returns_python_stuff(self):
        """Test json_from_kle returns Python stuff."""
        self.assertEqual(
            _json_from_kle('[{a:7},""]'),
            [[{'a': 7}, '']])

    def test_fiddlier_example(self):
        """Test json_from_kle can parse a more complex sample."""
        self.assertEqual(
            _json_from_kle("""
            [{y:1,x:12.5},"}\\n]",{x:0.25,w:1.25,h:2,w2:1.5,h2:1,x2:-0.25},"Enter"],
            [{x:12.75},"~\\n#"]
            """),
            [
                [
                    {'y': 1, 'x': 12.5},
                    '}\n]',
                    {'x': 0.25, 'w': 1.25, 'h': 2, 'w2': 1.5, 'h2': 1, 'x2': -0.25},
                    "Enter",
                ],
                [
                    {'x': 12.75},
                    '~\n#',
                ]
            ]
        )


class TestParseKle(unittest.TestCase):
    """Test kle."""

    def test_places_first_key_at_0_0(self):
        """Test kle places first key at 0,0."""
        kle = '[{a:7},""]'
        result = list(parse_kle(kle))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pos, (0, 0))
        self.assertEqual(result[0].x, 0)
        self.assertEqual(result[0].y, 0)
        self.assertEqual(result[0].size, (1, 1))
        self.assertEqual(result[0].w, 1)
        self.assertEqual(result[0].h, 1)

    def test_increments(self):
        """Test parse_kle increments position by default."""
        kle = '[{a:7},"",""],\n["",""]'
        result = list(parse_kle(kle))

        self.assertEqual(len(result), 4)
        self.assertEqual(result[0].pos, (0, 0))
        self.assertEqual(result[1].pos, (1, 0))
        self.assertEqual(result[2].pos, (0, 1))
        self.assertEqual(result[3].pos, (1, 1))

    def test_xy(self):
        """Test parse_kle handles x and y deltas."""
        kle = """[{a:7},"",{x:0.25},""],
            [{x:1},""],
            [{y:-0.75},""]"""
        result = list(parse_kle(kle))

        self.assertEqual(result[0].pos, (0, 0))
        self.assertEqual(result[1].pos, (1.25, 0))
        self.assertEqual(result[2].pos, (1, 1))
        self.assertEqual(result[3].pos, (0, 1.25))

    def test_w(self):
        """Test parse_kle handles w by changing width and positon of next key."""
        kle = """[{a:7,w:1.5},"",""]"""
        result = list(parse_kle(kle))

        self.assertEqual(result[0].pos, (0, 0))
        self.assertEqual(result[0].size, (1.5, 1))
        self.assertEqual(result[1].pos, (1.5, 0))
        self.assertEqual(result[1].size, (1, 1))

    def test_h(self):
        """Test parse_kle handles h by setting height ofnext key and NOT position of next row."""
        kle = """[{a:7,w:1,h:1.5},""],
            [{y:0.5},""]"""
        result = list(parse_kle(kle))

        self.assertEqual(result[0].pos, (0, 0))
        self.assertEqual(result[0].size, (1, 1.5))
        self.assertEqual(result[1].pos, (0, 1.5))
        self.assertEqual(result[1].size, (1, 1))

    def test_iso_enter(self):
        """Test parse_kle models ISO enter as two overlapping rectangles."""
        kle = """[{y:1,x:12.5},"}\\n]",{x:0.25,w:1.25,h:2,w2:1.5,h2:1,x2:-0.25},"Enter"],
            [{x:12.75},"~\\n#"]"""

        result = list(parse_kle(kle))
        self.assertEqual(result[1].pos, (13.75, 1))
        self.assertEqual(result[1].size, (1.25, 2))  # Main rect is 2 units tall
        self.assertEqual(result[1].pos2, (13.5, 1))
        self.assertEqual(result[1].size2, (1.5, 1))  # Overlaps the top of the first

