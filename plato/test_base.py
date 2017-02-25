"""Tests for Plato base class."""

from __future__ import print_function, unicode_literals
import unittest

from .base import Plato
from .kle_parser import Key


class TestPlato(unittest.TestCase):
    """Tests for Plato."""

    def test_calculate_layout_width_height(self):
        """Test Plato calculate_layout works out width and height."""
        plato = Plato(unit_mm=19)
        keys = [Key('q', (0, 0), (1, 1)), Key('m', (12, 5), (2, 3))]

        plato.calculate_layout(keys)

        self.assertAlmostEqual(plato.width_in_units, 14)
        self.assertAlmostEqual(plato.height_in_units, 8)
        self.assertAlmostEqual(plato.centre_col, 7)
        self.assertAlmostEqual(plato.centre_row, 4)

    def test_key_bbox(self):
        """Test key_bbox of a list of keys is centred on 0,0."""
        plato = Plato(unit_mm=19)
        keys = [Key('q', (0, 0), (1, 1)), Key('m', (12, 5), (2, 1))]

        plato.calculate_layout(keys)
        (x, y), (wd, ht) = plato.key_bbox()

        self.assertAlmostEqual(wd, 14 * 19)  # Because of wide letter m
        self.assertAlmostEqual(ht, 6 * 19)
        self.assertAlmostEqual(x, -7 * 19)
        self.assertAlmostEqual(y, -3 * 19)  # Bottom left

    def test_key_coords_of_0_0_is_top_left(self):
        """Test Plato key_coords of (0, 0) is top left."""
        # Define a 3×2 layout.
        plato = Plato(unit_mm=16)
        keys = [Key('q', (0, 0), (1, 1)), Key('s', (2, 1), (1, 1))]
        plato.calculate_layout(keys)

        x, y = plato.key_coords(Key('q', (0, 0), (1, 1)))
        self.assertAlmostEqual(x, -16)  # 1 unit to left of centre because 3 keys across
        self.assertAlmostEqual(y, 8)  # half unit above centre because 2 units high

        x, y = plato.key_coords(Key('s', (2, 1), (1, 1)))
        self.assertAlmostEqual(x, 16)
        self.assertAlmostEqual(y, -8)

        x, y = plato.key_coords(Key('Ent', (1, 0), (2, 1)))
        self.assertAlmostEqual(x, 8)  # Adjusted for width
        self.assertAlmostEqual(y, 8)

    def test_key_coords_offset_if_not_key_in_col_zero(self):
        """Test Plato key_coords of (0, 0) is top left."""
        # Define a 3×2 where for some reason there is space at top and left.
        plato = Plato(unit_mm=16)
        keys = [Key('q', (2, 1), (1, 1)), Key('s', (4, 2), (1, 1))]
        plato.calculate_layout(keys)

        x, y = plato.key_coords(Key('q', (2, 1), (1, 1)))  # the q is top left of this 2x2 layout
        self.assertAlmostEqual(x, -16)  # 1 unit to left of centre because 3 keys across
        self.assertAlmostEqual(y, 8)  # half unit above centre because 2 units high
