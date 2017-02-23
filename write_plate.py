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
        plato = DXFPlato('%s.dxf' % name)
        plato.calculate_layout(keys)
        _, (w, h) = plato.key_bbox()
        plato.draw_adjusted_round_rect((0, 0), (w + 7, h + 7), radius=3)
        if name in ['plate', 'test']:
            for k in keys:
                plato.draw_cherry_mx_switch(k)
        if name in ['under', 'test']:
            for k in keys:
                plato.draw_cherry_mx_under_switch(k)
        plato.save()
