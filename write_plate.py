#! /usr/bin/env python

"""Script to generate a DXF file."""

from __future__ import print_function, unicode_literals
from dxfwrite import DXFEngine as dxf, POLYLINE_CLOSED  # NOQA

from plato.dxf_plato import DXFPlato
from plato.kle_parser import parse_kle


if __name__ == '__main__':
    plato = DXFPlato('test.dxf')
    with open('x1.kle', 'r') as input:
        kle = input.read().decode('UTF-8')
    keys = parse_kle(kle)
    plato.calculate_layout(keys)
    _, size = plato.key_bbox()
    plato.draw_adjusted_round_rect((0, 0), size, radius=0.75)
    for k in keys:
        plato.cherry_mx_top_hole(k)
    plato.save()
