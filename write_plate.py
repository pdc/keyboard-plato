#! /usr/bin/env python

"""Script to generate a DXF file."""

from __future__ import print_function, unicode_literals
from dxfwrite import DXFEngine as dxf, POLYLINE_CLOSED  # NOQA

from plato.dxf_plato import DXFPlato
from plato.kle_parser import parse_kle


if __name__ == '__main__':
    with open('x1.kle', 'r') as input:
        kle = input.read().decode('UTF-8')
    keys = parse_kle(kle)

    for name in 'plate', 'under', 'test':
        plato = DXFPlato('%s.dxf' % name, case_thickness=6, padding=3.5, corner_radius=3, kerf=0.18)
        plato.calculate_layout(keys)
        plato.draw_outside()
        if name in ['plate', 'test']:
            plato.draw_cherry_mx_switches(keys)
        if name in ['under', 'test']:
            plato.draw_cherry_mx_under_switches(keys)
        plato.draw_screws(8, indent=3)
        plato.save()
