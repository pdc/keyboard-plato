#! /usr/bin/env python

"""Script to generate a DXF file."""

from __future__ import print_function, unicode_literals
from dxfwrite import DXFEngine as dxf, POLYLINE_CLOSED  # NOQA

from plato.dxf_plato import DXFPlato


if __name__ == '__main__':
    plato = DXFPlato('test.dxf', width_in_units=15, height_in_units=5)
    plato.draw_adjusted_round_rect(
        (0, 0), (plato.width_in_units * plato.unit_mm, plato.height_in_units * plato.unit_mm), 1.5)
    for z in [(0, 0), (1, 0), (1.5, 1), (1.75, 2), (2.25, 3), (14, 4)]:
        plato.cherry_mx_top_hole(plato.key_coords(*z))
    plato.save()
