"""Tests for Plato base class."""

from __future__ import print_function, unicode_literals
import unittest

from .base import Plato


class TestPlato(unittest.TestCase):
    """Tests for Plato."""

    def test_adjusted_coords_expands_gap(self):
        """Test DXFPlato adjusted_coords expands gap."""
        plato = Plato()
        left, right = plato.adjusted_coords(13, 56, 2.5)

        self.assertAlmostEqual(left, 13 - 28 - 2.5)
        self.assertAlmostEqual(right, 13 + 28 + 2.5)

    def test_key_coords_of_0_0_is_top_left(self):
        """Test DXFPlato key_coords of (0, 0) is top left."""
        plato = Plato(width_in_units=3, height_in_units=2, unit_mm=16)

        x, y = plato.key_coords(0, 0)
        self.assertAlmostEqual(x, -16)  # 1 unit to left of centre because 3 keys across
        self.assertAlmostEqual(y, 8)  # half unit above centre because 2 units high
