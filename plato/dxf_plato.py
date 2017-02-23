#! /usr/bin/env python

"""Script to generate a DXF file."""

from __future__ import print_function, unicode_literals
from dxfwrite import DXFEngine as dxf, POLYLINE_CLOSED  # NOQA

from .base import Plato
from .geometry import adjusted_coords


class DXFPlato(Plato):
    """Plate renderer with DXF backend."""

    def __init__(self, file_path='out.dxf', **kwargs):
        """Create instance with this file name."""
        super(DXFPlato, self).__init__(**kwargs)
        self.drawing = dxf.drawing(file_path)

    def save(self):
        """Write to file."""
        self.drawing.save()

    def draw_adjusted_round_rect(self, (x, y), (width, height), radius, is_outside=True, color=7, **kwargs):
        """Draw a rectangle with rounded corners.

        Arguments –
            (x, y) – centre of rectangle
            (widht, height) – effective dimensions of rectangle
            radius – of corners
            is_outside – whether this is the outside of the plate
                (so laser should be shifted outwards for laser kerf)

        """
        k = self.kerf if is_outside else -self.kerf
        line_left, line_right = adjusted_coords(x, width, -radius)
        line_bottom, line_top = adjusted_coords(y, height, -radius)
        left, right = adjusted_coords(x, width, k)
        bottom, top = adjusted_coords(y, height, k)

        self.drawing.add(dxf.line((line_left, bottom), (line_right, bottom), color=color))
        self.drawing.add(dxf.arc(radius + k, (line_right, line_bottom), 270, 0, color=color))
        self.drawing.add(dxf.line((right, line_bottom), (right, line_top), color=color))
        self.drawing.add(dxf.arc(radius + k, (line_right, line_top), 0, 90, color=color))
        self.drawing.add(dxf.line((line_left, top), (line_right, top), color=color))
        self.drawing.add(dxf.arc(radius + k, (line_left, line_top), 90, 180, color=color))
        self.drawing.add(dxf.line((left, line_bottom), (left, line_top), color=color))
        self.drawing.add(dxf.arc(radius + k, (line_left, line_bottom), 180, 270, color=color))

    def draw_polygon(self, points, color=7):
        """Draw a hole (or well) whose inner edges are described by the points.

        The actual polyline rendered will be adjusted by the amount of kerf.
        """
        self.drawing.add(dxf.polyline(points, color=color, flags=POLYLINE_CLOSED))
