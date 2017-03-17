# -* coding: UTF-8 -*-

"""Tests for svg_plato."""

from __future__ import print_function, unicode_literals
import unittest

from .kle_parser import Key
from .svg_plato import SVGPlato


class TestSVGPlato(unittest.TestCase):
    """Test SVGPlato."""

    def test_calculates_viewbox(self):
        """Test SVGPlato calculates viewbox."""
        plato = SVGPlato(kerf=0.5, padding=5, unit_mm=20)
        plato.calculate_layout([Key('q', (0, 0), (1, 1)), Key('s', (1.25, 1), (1, 1))])

        # Expect
        w, h = 1 + 5 + 2.25 * 20 + 5 + 1, 1 + 5 + 2 * 20 + 5 + 1
        self.assertEqual(plato.elt.attrib['width'], '%fmm' % w)
        self.assertEqual(plato.elt.attrib['height'], '%fmm' % h)
        self.assertEqual(plato.elt.attrib['viewBox'], '%f %f %f %f' % (-0.5 * w, -0.5 * h, w, h))

    def test_uses_relative_moves(self):
        """Test SVGPlato uses relative moves."""
        plato = SVGPlato()

        plato.draw_polygon([(-10, -7), (-10, 7), (10, 7), (10, -7)])
        result = plato.g[-1].attrib['d']

        self.assertEquals(result, 'M-10,-7v14h20v-14z')

    def test_can_also_do_diagonal_moves(self):
        """Test SVGPlato can also do diagonal moves."""
        plato = SVGPlato()

        plato.draw_polygon([(1, 2), (2, 5), (3, 4), (4, 2)])
        result = plato.g[-1].attrib['d']

        self.assertEquals(result, 'M1,2l1,3l1,-1l1,-2z')
