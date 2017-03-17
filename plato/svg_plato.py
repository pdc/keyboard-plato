# -* coding: UTF-8 -*-

"""Subclass of Plato that renders as SVG."""

from __future__ import print_function, unicode_literals
from .base import Plato

from xml.etree import ElementTree


SVG_NS = 'http://www.w3.org/2000/svg'


class SVGPlato(Plato):
    """Keyboard plate drawing class that writes SVG."""

    stroke_default = 'rgba(0, 0, 0, 0.8)'
    stroke_alt = 'rgba(%d, %d, %d, 0.8)' % (0xBB, 0x00, 0xAA)

    def __init__(self, file=None, **kwargs):
        """Create instance with nothing in it."""
        super(SVGPlato, self).__init__(**kwargs)
        self.file = file

        self.elt = ElementTree.Element('svg', {
            'xmlns': SVG_NS,  # O
        })
        # Flip the y axis so it goes up not down.
        self.g = ElementTree.SubElement(self.elt, 'g', {
            'transform': 'scale(1, -1)',
            'stroke': self.stroke_default,
            'stroke-width': str(2 * self.kerf),
            'stroke-linejoin': 'round',
            'fill': 'none',
        })

        if self.width_in_units:
            self._set_viewbox()

    def save(self, file=None):
        """Write SVG representation of the graphics to this file."""
        tree = ElementTree.ElementTree(self.elt)
        tree.write(file or self.file, encoding='UTF-8')

    def draw_roundrect(self, (x, y), (wd, ht), radius, color=None):
        """Draw a rounded rectangle centred on (x, y) with this size and corner radius."""
        e = ElementTree.SubElement(self.g, 'rect', {
            'x': str(x - 0.5 * wd),
            'y': str(y - 0.5 * ht),
            'width': str(wd),
            'height': str(ht),
            'rx': str(radius),
            'ry': str(radius),
        })
        self.frig(e, color)

    def draw_polygon(self, points, color=None):
        """Draw closed polygon through these vertices."""
        x0, y0 = points[0]
        parts = ['M%s,%s' % (x0, y0)]
        for x, y in points[1:]:
            if x == x0:
                parts.append('v%s' % (y - y0))
            elif y == y0:
                parts.append('h%s' % (x - x0))
            else:
                parts.append('l%s,%s' % (x - x0, y - y0))
            x0, y0 = x, y
        parts.append('z')
        d = ''.join(parts)

        e = ElementTree.SubElement(self.g, 'path', {
            'd': d,
        })
        self.frig(e, color)

    def draw_circle(self, (x, y), radius, color=None):
        """Draw cirlce centred on x,y with this radius."""
        e = ElementTree.SubElement(self.g, 'circle', {
            'cx': str(x),
            'cy': str(y),
            'r': str(radius),
        })
        self.frig(e, color)

    def frig(self, e, color):
        if color and color != self.stroke_default:
            e.set('stroke', color)

    def calculate_layout(self, keys, **kwargs):
        """Calculate size of keyboard based on the layout."""
        super(SVGPlato, self).calculate_layout(keys, **kwargs)
        self._set_viewbox()

    def _set_viewbox(self):
        # Calculate viewBox.
        _, (wd, ht) = self.key_bbox()
        # Enlarge the drawing
        padding_wd, padding_ht = self.padding
        wd += 4 * self.kerf + 2 * padding_wd
        ht += 4 * self.kerf + 2 * padding_ht
        self.elt.set('width', '%fmm' % wd)
        self.elt.set('height', '%fmm' % ht)
        self.elt.set('viewBox', '%f %f %f %f' % (-0.5 * wd, -0.5 * ht, wd, ht))
