"""Script to generate a DXF or SVG file."""

from dxfwrite import DXFEngine as dxf, POLYLINE_CLOSED  # NOQA


class DXFPlato(object):
    """Plate renderer with DXF backend."""

    kerf = 0.18  # http://www.cutlasercut.com/resources/tips-and-advice/what-is-laser-kerf

    cherry_mx_hole_size = 14.0  # Width and height of standard hole for CHerry MX switch,

    def __init__(self, file_path='out.dxf'):
        """Create instance with this file name."""
        self.drawing = dxf.drawing(file_path)

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
        line_left = x - 0.5 * width + radius
        line_right = x + 0.5 * width - radius
        line_top = y + 0.5 * height - radius
        line_bottom = y - 0.5 * height + radius
        left = x - 0.5 * width - k
        right = x + 0.5 * width + k
        top = y + 0.5 * height + k
        bottom = y - 0.5 * height - k

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

    def cherry_mx_top_hole(self, (x, y), color=7):
        """The hole in to which a Cherry MX switch will be clipped.

        Should be 1.5 mm thick.
        """
        left, right = self.adjusted_coords(x, self.cherry_mx_hole_size, -self.kerf)
        bottom, top = self.adjusted_coords(y, self.cherry_mx_hole_size, -self.kerf)
        self.drawing.add(dxf.polyline(
            [(left, bottom), (right, bottom), (right, top), (left, top)],
            color=color, flags=POLYLINE_CLOSED))


if __name__ == '__main__':
    plato = DXFPlato('test.dxf')
    plato.round_rect((0, 0), (280, 140), 3)
    plato.cherry_mx_top_hole((0, 0))
    plato.cherry_mx_top_hole((19, 0))
    plato.cherry_mx_top_hole((0, 19))
    plato.save()
