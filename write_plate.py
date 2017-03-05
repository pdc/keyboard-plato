#! /usr/bin/env python

"""Script to generate a DXF file."""

from __future__ import print_function, unicode_literals
from dxfwrite import DXFEngine as dxf, POLYLINE_CLOSED  # NOQA

from plato.dxf_plato import DXFPlato
from plato.svg_plato import SVGPlato
from plato.kle_parser import parse_kle


if __name__ == '__main__':
    with open('x1.kle', 'r') as input:
        kle = input.read().decode('UTF-8')
    keys = parse_kle(kle)

    for suf, cls in [('dxf', DXFPlato), ('svg', SVGPlato)]:
        for name in 'plate', 'under', 'test', 'caps':
            plato = cls('%s.%s' % (name, suf), case_thickness=5, padding=5, corner_radius=3, kerf=0.18)
            plato.calculate_layout(keys)
            plato.draw_outside()
            if name in ['plate', 'test']:
                plato.draw_cherry_mx_switches(keys)
            if name in ['under', 'test']:
                plato.draw_cherry_mx_under_switches(keys)
            if name in ['caps', 'test']:
                plato.draw_screw_heads(8, indent=2.5)
                plato.draw_key_caps(keys)
            plato.draw_screws(8, indent=2.5)
            plato.save()
