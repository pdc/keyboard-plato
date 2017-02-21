"""Object for generating drawings of keyboard plates."""

from __future__ import print_function, unicode_literals


class Plato(object):
    """Abstract base for plate-drawing classes."""

    kerf = 0.18  # http://www.cutlasercut.com/resources/tips-and-advice/what-is-laser-kerf
    cherry_mx_hole_size = 14.0  # Width and height of standard hole for CHerry MX switch.
    width_in_units = 15  # Width of the layout in key units.
    height_in_units = 5  # Heightof the keyboard in units (= numberof rows).
    unit_mm = 19  # Size of a unit. The official standard is 19.05 mm but 19 mm is close enough.

    def __init__(self, file_path='out.dxf', kerf=None, size_in_units=None,
                 width_in_units=None, height_in_units=None, unit_mm=None):
        """Create instance with this file name."""
        if width_in_units:
            self.width_in_units = width_in_units
        if height_in_units:
            self.height_in_units = height_in_units
        if size_in_units:
            self.width_in_units, self.height_in_units = size_in_units
        if unit_mm:
            self.unit_mm = unit_mm

    def draw_polygon(self, points):
        """Draw a hole (or well) whose inner edges are described by the points.

        Caller is responsible for adjusting the outline to allow for kerf.
        """
        raise NotImplementedError('%s: needs draw_polygon' % self.__class__.name)

    def adjusted_coords(self, x, width, adjustment):
        """Return a (left, right) or (bottom, top) pair or coordinates.

        Arguments –
            x – centre point
            width – how far apart the 2 points are
            adjustment – extra distance t ibe added each end (usually kerf or corner radius)

        Returns two x-coordinates.
        """
        left = x - 0.5 * width - adjustment
        right = x + 0.5 * width + adjustment
        return left, right

    def key_bbox(self, keys):
        """Calculate a rectangle that exactly encloses these keys.

        Outer edge aligns with edge of keycaps.
        Does not adjust for kerf.
        """
        # Find boundaries in key units (with y increasing downwards).
        lf = min(k.x - 0.5 for k in keys)
        rt = max(k.x + k.w - 0.5 for k in keys)
        tp = min(k.y - 0.5 for k in keys)
        bt = max(k.y + k.h - 0.5 for k in keys)

        # Translate in to mm.
        w = (rt - lf) * self.unit_mm
        h = (bt - tp) * self.unit_mm
        x = -0.5 * w
        y = -0.5 * h
        return (x, y), (w, h)

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
        self.draw_polygon([(left, bottom), (right, bottom), (right, top), (left, top)])
