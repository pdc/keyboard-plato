"""Object for generating drawings of keyboard plates."""

from __future__ import print_function, unicode_literals

# Stabilizers: for simplicity I am sticking to Costar stabilizers
# (which have the simplest cutouts).

# https://deskthority.net/keyboards-f2/costar-stabilizer-plate-measurements-t5872.html

# Adapted from data stolen from kb_builder

STABILIZER_SIZE = (3.3, 14.0)

STABILIZER_X_OFFSETS = {
    2: 11.95,
    2.25: 11.95,
    2.5: 11.95,
    2.75: 11.95,
    3: 19.05,  # 3 unit
    4: 28.575,  # 4 unit
    4.5: 34.671,  # 4.5 unit
    5.5: 42.8625,  # 5.5 unit
    6.25: 50,  # 6.25 unit
    6.5: 52.38,  # 6.5 unit
    7: 57.15,  # 7 unit
    8: 66.675,  # 8 unit
    9: 66.675,  # 9 unit
    10: 66.675  # 10 unit
}
STABILIZER_Y_OFFSET = -0.75


def flip_clockwise(points):
    """Rotate points 90° around the origin."""
    return [(y, -x) for x, y in points]


def translate((dx, dy), points):
    """Trnslate the points by the vector delta."""
    return [(x + dx, y + dy) for x, y in points]


class Plato(object):
    """Abstract base for plate-drawing classes."""

    kerf = 0.18  # http://www.cutlasercut.com/resources/tips-and-advice/what-is-laser-kerf
    cherry_mx_hole_size = 14.0  # Width and height of standard hole for CHerry MX switch.
    width_in_units = None  # Width of the layout in key units.
    height_in_units = None  # Height of the keyboard in units (= numberof rows).
    centre_col = None  # Centre of layout in units.
    centre_row = None  # Centre of layout in units.
    unit_mm = 19  # Size of a unit. The official standard is 19.05 mm but 19 mm is close enough.

    def __init__(self, file_path='out.dxf', kerf=None, size_in_units=None,
                 width_in_units=None, height_in_units=None,
                 centre_col=None, centre_row=None,
                 unit_mm=None):
        """Create instance with this file name."""
        if width_in_units:
            self.width_in_units = width_in_units
        if height_in_units:
            self.height_in_units = height_in_units
        if centre_col is not None:
            self.centre_col = centre_col
        if centre_row is not None:
            self.centre_row = centre_row
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

    def calculate_layout(self, keys):
        """Calculate the width and height of the layut in cols and rows."""
        lf = min(k.x for k in keys)
        rt = max(k.x + k.w for k in keys)
        tp = min(k.y for k in keys)
        bt = max(k.y + k.h for k in keys)

        self.width_in_units = rt - lf
        self.height_in_units = bt - tp
        self.centre_col = 0.5 * (lf + rt)
        self.centre_row = 0.5 * (tp + bt)

    def key_bbox(self):
        """Calculate a rectangle that exactly encloses these keys.

        Outer edge aligns with edge of keycaps.
        Does NOT adjust for kerf.
        """
        # Find boundaries in key units (with y increasing downwards).

        # Translate in to mm.
        w = self.width_in_units * self.unit_mm
        h = self.height_in_units * self.unit_mm
        x = -self.centre_col * self.unit_mm
        y = -self.centre_row * self.unit_mm

        return (x, y), (w, h)

    def key_coords(self, key):
        """Calculate centre of a switch in this column and row in the layout."""
        x = (key.x - self.centre_col + 0.5 * key.w) * self.unit_mm
        y = -(key.y - self.centre_row + 0.5 * key.h) * self.unit_mm
        return x, y

    def cherry_mx_top_hole(self, key, color=7):
        """The hole in to which a Cherry MX switch will be clipped.

        Should be 1.5 mm thick.
        """
        # Build collection of shapes centerd on switch.
        zss = [self.rect_points((0, 0), (self.cherry_mx_hole_size, self.cherry_mx_hole_size), -self.kerf)]

        if key.w >= 2 or key.h >= 2:
            # Also draw stabilizers.
            stab_x = STABILIZER_X_OFFSETS.get(max(key.w, key.h))
            zss.extend([
                self.rect_points((stab_x, STABILIZER_Y_OFFSET), STABILIZER_SIZE, -self.kerf),
                self.rect_points((-stab_x, STABILIZER_Y_OFFSET), STABILIZER_SIZE, -self.kerf),
            ])
            if key.h > key.w:
                zss = [flip_clockwise(zs) for zs in zss]

        # Now draw in correct location.
        x, y = self.key_coords(key)
        zss = [translate((x, y), zs) for zs in zss]
        for zs in zss:
            self.draw_polygon(zs)

    def rect_points(self, (x, y), (wd, ht), adjustment):
        """Calculate a rectangle centered on (x,y) with this size enlarged by adjustment."""
        left, right = self.adjusted_coords(x, wd, adjustment)
        bottom, top = self.adjusted_coords(y, ht, adjustment)
        return [(left, bottom), (right, bottom), (right, top), (left, top)]

    def draw_rect(self, (x, y), (wd, ht), adjustment):
        """Draw a rectangle centered on (x,y) with this size enlarged by adjustment."""
        self.draw_polygon(self.rect_points((x, y), (wd, ht), adjustment))
