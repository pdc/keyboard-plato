# -* coding: UTF-8 -*-

"""Object for generating drawings of keyboard plates."""

from __future__ import print_function, unicode_literals

from .geometry import flip_clockwise, translate, rect_points, merge_shapes, screw_points


# Stabilizers: for simplicity I am sticking to Costar stabilizers
# (which have the simplest cutouts).

# https://deskthority.net/keyboards-f2/costar-stabilizer-plate-measurements-t5872.html

# Adapted from data stolen from kb_builder

STABILIZER_SIZE = (3.3, 14.0)
UNDER_STABILIZER_SIZE = (3.3, 15.5)

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

MIN_PADDING = -2.5  # At this point edge of plate aligns with edge of hole.


class Plato(object):
    """Abstract base for plate-drawing classes."""

    kerf = 0.18  # http://www.cutlasercut.com/resources/tips-and-advice/what-is-laser-kerf
    cherry_mx_hole_size = 14.0  # Width and height of standard hole for CHerry MX switch.
    clip_width = 0.75
    width_in_units = None  # Width of the layout in key units.
    height_in_units = None  # Height of the keyboard in units (= numberof rows).
    centre_col = None  # Centre of layout in units.
    centre_row = None  # Centre of layout in units.
    unit_mm = 19  # Size of a unit. The official standard is 19.05 mm but 19 mm is close enough.
    padding = (0, 0)  # Added to outside of keys
    case_thickness = (-MIN_PADDING, -MIN_PADDING)
    corner_radius = 3.5

    def __init__(self, file_path='out.dxf',
                 kerf=None,
                 size_in_units=None,
                 width_in_units=None, height_in_units=None,
                 centre_col=None, centre_row=None,
                 unit_mm=None,
                 padding=None, case_thickness=None, corner_radius=None):
        """Create instance with this file name."""
        if kerf is not None:
            self.kerf = kerf
        if width_in_units:
            self.width_in_units = width_in_units
        if height_in_units:
            self.height_in_units = height_in_units
        if size_in_units:
            self.width_in_units, self.height_in_units = size_in_units
        if centre_col is not None:
            self.centre_col = centre_col
        elif self.width_in_units:
            self.centre_col = self.width_in_units * 0.5
        if centre_row is not None:
            self.centre_row = centre_row
        elif self.height_in_units:
            self.centre_row = self.height_in_units * 0.5
        if unit_mm:
            self.unit_mm = unit_mm
        if padding:
            if isinstance(padding, (int, float)):
                self.padding = padding, padding
            else:
                self.padding = padding
        if case_thickness:
            if isinstance(case_thickness, (int, float)):
                self.case_thickness = case_thickness, case_thickness
            else:
                self.case_thickness = case_thickness
        if padding and case_thickness:
            for p, c in zip(self.padding, self.case_thickness):
                if p - c < MIN_PADDING:
                    raise ValueError('case_thickness %d; cannot be more than %d' % (c, p - MIN_PADDING))
        if corner_radius:
            self.corner_radius = corner_radius

    def draw_polygon(self, points, **kwargs):
        """Draw a hole (or well) whose inner edges are described by the points.

        Caller is responsible for adjusting the outline to allow for kerf.
        """
        raise NotImplementedError('%s: needs draw_polygon' % self.__class__.__name__)

    def draw_circle(self, point, radius, **kwargs):
        """Draw a circular hole or well.

        Caller is responsible for adjusting the outline to allow for kerf.
        """
        raise NotImplementedError('%s: needs draw_circle' % self.__class__.__name__)

    def draw_roundrect(self, point, size, radius, **kwargs):
        """Draw a rect centered at point with size and corner radius.

        Caller is responsible for adjusting the outline to allow for kerf.
        """
        raise NotImplementedError('%s: needs draw_roundrect' % self.__class__.__name__)

    def draw_outside_roundrect(self, (x, y), (width, height), radius, kerf=None, **kwargs):
        """Draw a rounded rect adjusted for kerf.

        Arguments –
            (x, y) – centre of rectangle
            (width, height) – effective dimensions of rectangle
            radius – of corners
            kerf (optional) – override default kerf value
        """
        k = kerf or self.kerf
        self.draw_roundrect((x, y), (width + 2 * k, height + 2 * k), radius + k, **kwargs)

    def draw_inside_roundrect(self, (x, y), (width, height), radius, kerf=None, **kwargs):
        """Draw a rounded rect adjusted for kerf.

        Arguments –
            (x, y) – centre of rectangle
            (width, height) – effective dimensions of rectangle
            radius – of corners
            kerf (optional) – override default kerf value
        """
        k = -(kerf or self.kerf)
        self.draw_roundrect((x, y), (width + 2 * k, height + 2 * k), radius + k, **kwargs)

    def draw_inside_rect(self, (x, y), (width, height), radius, kerf=None, **kwargs):
        """Draw a rounded rect adjusted for kerf.

        Arguments –
            (x, y) – centre of rectangle
            (width, height) – effective dimensions of rectangle
            radius – of corners
            kerf (optional) – override default kerf value
        """
        self.draw_rect((x, y), (width, height), -(kerf or self.kerf), **kwargs)

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

    def draw_cherry_mx_switches(self, keys, kerf=None, color=None):
        """The hole in to which a Cherry MX switch will be clipped.

        Should be 1.5 mm thick.
        """
        k = (self.kerf if kerf is None else kerf)
        switch_shape = rect_points((0, 0), (self.cherry_mx_hole_size, self.cherry_mx_hole_size), -k)
        for key in keys:
            self.draw_switch_and_stablizers(
                key, switch_shape, stabilizer_size=STABILIZER_SIZE,
                color=(color or self.stroke_default))

    def draw_cherry_mx_under_switches(self, keys, kerf=None, color=None):
        """For part of chery switch under the plate.

        Should be 1up to 3.5 mm thick.
        """
        k = (self.kerf if kerf is None else kerf)
        switch_shape = merge_shapes(
            rect_points((0, 0), (self.cherry_mx_hole_size, self.cherry_mx_hole_size), -k),
            rect_points((0, 0), (5, self.cherry_mx_hole_size + 2 * self.clip_width), -k),
        )
        for key in keys:
            self.draw_switch_and_stablizers(
                key, switch_shape, stabilizer_size=UNDER_STABILIZER_SIZE,
                color=(color or self.stroke_default))

    def draw_cherry_mx_switch_clips(self, keys, kerf=None, color=None):
        """The part of the under plate that is not the hole for the switch proper.

        Should be up to 3.5 mm thick.
        """
        k = (self.kerf if kerf is None else kerf)
        y = 0.5 * (self.cherry_mx_hole_size + self.clip_width)
        switch_polygons = [
            rect_points((0, -y), (5, self.clip_width), -k),
            rect_points((0, y), (5, self.clip_width), -k),
        ]
        stab_wd, stab_ht = STABILIZER_SIZE
        for key in keys:
            polygons = switch_polygons
            if key.w >= 2 or key.h >= 2:
                # Also draw stabilizers.
                stab_x = STABILIZER_X_OFFSETS.get(max(key.w, key.h))
                stab_y = 0.5 * (stab_ht + self.clip_width)
                polygons = polygons + [
                    rect_points((stab_x, STABILIZER_Y_OFFSET - stab_y), (stab_wd, self.clip_width), -k),
                    rect_points((-stab_x, STABILIZER_Y_OFFSET - stab_y), (stab_wd, self.clip_width), -k),
                    rect_points((stab_x, STABILIZER_Y_OFFSET + stab_y), (stab_wd, self.clip_width), -k),
                    rect_points((-stab_x, STABILIZER_Y_OFFSET + stab_y), (stab_wd, self.clip_width), -k),
                ]
                if key.h > key.w:
                    polygons = [flip_clockwise(zs) for zs in polygons]
            self.draw_switch_polygons(key, polygons, color=color)

    def draw_key_caps(self, keys, color=None):
        """Draw outlines of the key caps."""
        for key in keys:
            zs = rect_points((0, 0), (key.w * self.unit_mm, key.h * self.unit_mm))
            if hasattr(key, 'x2'):
                # Offset of second rect is measured between their top-left corners
                # in keyboard units, with y downwards.
                x2 = (0.5 * (key.w2 - key.w) + key.x2 - key.x) * self.unit_mm
                y2 = (0.5 * (key.h2 - key.h) + key.y2 - key.y) * -self.unit_mm
                zs = merge_shapes(zs, rect_points((x2, y2), (key.w2 * self.unit_mm, key.h2 * self.unit_mm)))
            self.draw_polygon(translate(self.key_coords(key), zs), color=(color or self.stroke_alt))

    def draw_switch_and_stablizers(self, key, switch_shape, stabilizer_size, color=None):
        """Draw the switch for this key, andits stabilizers if any."""
        # Build collection of shapes centerd on switch.
        zss = [switch_shape]

        if key.w >= 2 or key.h >= 2:
            # Also draw stabilizers.
            stab_x = STABILIZER_X_OFFSETS.get(max(key.w, key.h))
            zss.extend([
                rect_points((stab_x, STABILIZER_Y_OFFSET), stabilizer_size, -self.kerf),
                rect_points((-stab_x, STABILIZER_Y_OFFSET), stabilizer_size, -self.kerf),
            ])
            if key.h > key.w:
                zss = [flip_clockwise(zs) for zs in zss]

        self.draw_switch_shapes(key, zss)

    def draw_switch_polygons(self, key, polygons, color=None):
        """Draw the shapes at the correct position for the given key."""
        # Now draw in correct location.
        x, y = self.key_coords(key)
        zss = [translate((x, y), zs) for zs in polygons]
        for zs in zss:
            self.draw_polygon(zs, color=(color or self.stroke_default))

    def draw_outside(self):
        """Draw the outside edge of the keyboard."""
        _, (wd, ht) = self.key_bbox()
        (padding_wd, padding_ht) = self.padding
        self.draw_outside_roundrect((0, 0), (wd + 2 * padding_wd, ht + 2 * padding_ht), radius=self.corner_radius)

    def draw_screws(self, n=6, radius=1, indent=None, **kwargs):
        """Draw holes for screws.

        Arguments –
            n – how many screw holes; must be an even number ≥ 4
            radius – nominal radius of thread (e.g., 1 for an M2 screw)
            indent – distance between edge of case and screw; default is one-half case case_thickness
        """
        for z in self.screw_points(n, indent):
            self.draw_circle(z, radius - self.kerf)

    def draw_screw_heads(self, n=6, radius=2, indent=None, color=None, **kwargs):
        """Draw heads of screws.

        Arguments –
            n – how many screw holes; must be an even number ≥ 4
            radius – of head
            indent – distance between edge of case and screw; default is one-half case case_thickness
        """
        for z in self.screw_points(n, indent):
            self.draw_circle(z, radius + self.kerf, color=(color or self.stroke_alt), **kwargs)

    def screw_points(self, n=6, indent=None):
        """Calculate location of screws."""
        _, (wd, ht) = self.key_bbox()
        (padding_wd, padding_ht) = self.padding
        if not indent:
            (case_wd, case_ht) = self.case_thickness
            indent = (case_wd * 0.5, case_ht * 0.5)
        elif isinstance(indent, (int, float)):
            indent = indent, indent
        (indent_wd, indent_ht) = indent
        actual_wd, actual_ht = (wd + padding_wd * 2 - indent_wd * 2, ht + padding_ht * 2 - indent_ht * 2)

        return screw_points(n, (actual_wd, actual_ht))

    def draw_rect(self, (x, y), (wd, ht), adjustment=0, **kwargs):
        """Draw a rectangle centered on (x,y) with this size enlarged by adjustment."""
        self.draw_polygon(rect_points((x, y), (wd, ht), adjustment), **kwargs)
