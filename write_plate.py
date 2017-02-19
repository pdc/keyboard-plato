"""Script to generate a DXF or SVG file."""

from dxfwrite import DXFEngine as dxf, POLYLINE_CLOSED  # NOQA
import unittest


class DXFPlato(object):
    """Plate renderer with DXF backend."""

    kerf = 0.18  # http://www.cutlasercut.com/resources/tips-and-advice/what-is-laser-kerf
    cherry_mx_hole_size = 14.0  # Width and height of standard hole for CHerry MX switch,

    def __init__(self, file_path='out.dxf', width_in_units=15, height_in_units=5, unit_mm=19):
        """Create instance with this file name."""
        self.drawing = dxf.drawing(file_path)
        self.width_in_units = width_in_units
        self.height_in_units = height_in_units
        self.unit_mm = unit_mm

    def save(self):
        """Write to file."""
        self.drawing.save()

    def round_rect(self, (x, y), (width, height), radius, is_outside=True, color=7, **kwargs):
        u"""Drw a rectangle with rounded corners.

        Arguments –
            (x, y) – centre of rectangle
            (widht, height) – effective dimensions of rectangle
            radius – of corners
            is_outside – whether this is the outside of the plate (so laser should be shifted outwards)

        """
        k = self.kerf if is_outside else -self.kerf
        line_left, line_right = self.adjusted_coords(x, width, -radius)
        line_bottom, line_top = self.adjusted_coords(y, height, -radius)
        left, right = self.adjusted_coords(x, width, k)
        bottom, top = self.adjusted_coords(y, height, k)

        self.drawing.add(dxf.line((line_left, bottom), (line_right, bottom), color=color))
        self.drawing.add(dxf.arc(radius + k, (line_right, line_bottom), 270, 0, color=color))
        self.drawing.add(dxf.line((right, line_bottom), (right, line_top), color=color))
        self.drawing.add(dxf.arc(radius + k, (line_right, line_top), 0, 90, color=color))
        self.drawing.add(dxf.line((line_left, top), (line_right, top), color=color))
        self.drawing.add(dxf.arc(radius + k, (line_left, line_top), 90, 180, color=color))
        self.drawing.add(dxf.line((left, line_bottom), (left, line_top), color=color))
        self.drawing.add(dxf.arc(radius + k, (line_left, line_bottom), 180, 270, color=color))

    def adjusted_coords(self, x, width, adjustment):
        u"""Return a left, right pair or coordinates.

        Arguments –
            x – centre point
            width – how far apart the 2 points are
            adjustment – extra distance t ibe added each end (usually kerf or corner radius)

        Returns two x-coordinates.
        """
        left = x - 0.5 * width - adjustment
        right = x + 0.5 * width + adjustment
        return left, right

    def key_coords(self, col, row):
        """Calculate centre of a switch in this column and row in the layout."""
        x = (col - 0.5 * (self.width_in_units - 1)) * self.unit_mm
        y = -(row - 0.5 * (self.height_in_units - 1)) * self.unit_mm
        return x, y

    def cherry_mx_top_hole(self, (x, y), color=7):
        """The hole in to which a Cherry MX switch will be clipped.

        Should be 1.5 mm thick.
        """
        left, right = self.adjusted_coords(x, self.cherry_mx_hole_size, -self.kerf)
        bottom, top = self.adjusted_coords(y, self.cherry_mx_hole_size, -self.kerf)
        self.drawing.add(dxf.polyline(
            [(left, bottom), (right, bottom), (right, top), (left, top)],
            color=color, flags=POLYLINE_CLOSED))


class TestDXFPlato(unittest.TestCase):
    """Tests for DXFPlato."""

    def test_adjusted_coords_expands_gap(self):
        """Test DXFPlato adjusted_coords expands gap."""
        plato = DXFPlato()
        left, right = plato.adjusted_coords(13, 56, 2.5)

        self.assertAlmostEqual(left, 13 - 28 - 2.5)
        self.assertAlmostEqual(right, 13 + 28 + 2.5)

    def test_key_coords_of_0_0_is_top_left(self):
        """Test DXFPlato key_coords of (0, 0) is top left."""
        plato = DXFPlato(width_in_units=3, height_in_units=2, unit_mm=16)

        x, y = plato.key_coords(0, 0)
        self.assertAlmostEqual(x, -16)  # 1 unit to left of centre because 3 keys across
        self.assertAlmostEqual(y, 8)  # half unit above centre because 2 units high


if __name__ == '__main__':
    plato = DXFPlato('test.dxf', width_in_units=15, height_in_units=5)
    plato.round_rect((0, 0), (plato.width_in_units * plato.unit_mm, plato.height_in_units * plato.unit_mm), 1.5)
    for z in [(0, 0), (1, 0), (1.5, 1), (1.75, 2), (2.25, 3), (14, 4)]:
        plato.cherry_mx_top_hole(plato.key_coords(*z))
    plato.save()
