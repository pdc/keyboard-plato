#! /usr/bin/env python
# -* coding: UTF-8 -*-

"""Script to generate a DXF file."""

from __future__ import print_function, unicode_literals
from dxfwrite import DXFEngine as dxf, POLYLINE_CLOSED  # NOQA

from .base import Plato


class DXFPlato(Plato):
    """Plate renderer with DXF backend."""

    # DXF colours are specified as indexes in to a colour table.
    stroke_default = 7  # White
    stroke_alt = 6  # Magenta

    def __init__(self, file_path='out.dxf', **kwargs):
        """Create instance with this file name."""
        super(DXFPlato, self).__init__(**kwargs)
        self.drawing = dxf.drawing(file_path)

    def save(self):
        """Write to file."""
        self.drawing.save()

    def draw_roundrect(self, (x, y), (width, height), radius, color=stroke_default, **kwargs):
        """Draw a rectangle with rounded corners."""
        left, right = x - 0.5 * width, x + 0.5 * width
        bottom, top = y - 0.5 * height, y + 0.5 * height

        self.drawing.add(dxf.line((left + radius, bottom), (right - radius, bottom), color=color))
        self.drawing.add(dxf.arc(radius, (right - radius, bottom + radius), 270, 0, color=color))
        self.drawing.add(dxf.line((right, bottom + radius), (right, top - radius), color=color))
        self.drawing.add(dxf.arc(radius, (right - radius, top - radius), 0, 90, color=color))
        self.drawing.add(dxf.line((left + radius, top), (right - radius, top), color=color))
        self.drawing.add(dxf.arc(radius, (left + radius, top - radius), 90, 180, color=color))
        self.drawing.add(dxf.line((left, bottom + radius), (left, top - radius), color=color))
        self.drawing.add(dxf.arc(radius, (left + radius, bottom + radius), 180, 270, color=color))

    def draw_polygon(self, points, color=stroke_default):
        """Draw a hole (or well) described by the points."""
        self.drawing.add(dxf.polyline(points, color=color, flags=POLYLINE_CLOSED))

    def draw_circle(self, point, radius, color=stroke_default):
        """Draw a circular hole or well."""
        self.drawing.add(dxf.circle(radius=radius, center=point, color=color))
