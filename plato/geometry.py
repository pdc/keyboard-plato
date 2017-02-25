"""Claculating simple geometry.

Most shapes in this diagram are composed of vertical and horizontal lines.
The algorithms are therefore a bit simplistic.
"""

from __future__ import print_function, unicode_literals
import sys


def adjusted_coords(x, width, adjustment):
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


def rect_points((x, y), (wd, ht), adjustment=0):
    """Calculate a rectangle centered on (x,y) with this size enlarged by adjustment."""
    left, right = adjusted_coords(x, wd, adjustment)
    bottom, top = adjusted_coords(y, ht, adjustment)
    return [(left, bottom), (right, bottom), (right, top), (left, top)]


def flip_clockwise(points):
    """Rotate points 90° around the origin."""
    return [(y, -x) for x, y in points]


def translate((dx, dy), points):
    """Trnslate the points by the vector delta."""
    return [(x + dx, y + dy) for x, y in points]


def segments(zs):
    """Return list of segments in this shape."""
    return [
        ((x1, y1), (x2, y2)) if x1 < x2 or y1 < y2 else ((x2, y2), (x1, y1))
        for (x1, y1), (x2, y2) in zip(zs, zs[1:] + [zs[0]])
    ]


def overlapping_segments(((x1, y1), (x2, y2)), segs):
    """Return set of segments overlapping the first one."""
    is_vert = x1 == x2  # Whether we are tracing an vertical segment
    return {
        ((u1, v1), (u2, v2))
        for ((u1, v1), (u2, v2)) in segs
        if (v1 == v2 and u1 <= x1 and x2 <= u2
            if is_vert
            else u1 == u2 and v1 <= y1 and y2 <= v2)
    }


def merge_shapes(*zss):
    """Find the union of n overlapping rectilinear shapes.

    Arguments –
        zss – list of shapes, each shape is a list of points

    Retunes –
        A lit ofpoints describing overlapping shape
    """
    segs = {seg for zs in zss for seg in segments(zs)}
    ((x1, y1), (x2, y2)) = seg = min(segs)
    is_upright = True  # Whether we are tracing upwards/rightwards
    is_vert = x1 == x2  # Whether we are tracing an vertical segment
    result = []
    start = (x, y) = (x1, y1) if is_upright else (x2, y2)
    count = 0
    while True:
        count += 1
        if count > 100:
            # This only happens if there is a bug.
            sys.exit('Shape unexpectedly too complicated')
            break
        result.append((x, y))
        overlaps = overlapping_segments(seg, segs)

        # Find the first overlap in the forwards direction:
        if is_vert:
            if is_upright:
                candidates = [((u1, v1), (u2, v2)) for ((u1, v1), (u2, v2)) in overlaps if v1 > y]
            else:
                candidates = [((u1, v1), (u2, v2)) for ((u1, v1), (u2, v2)) in overlaps if v1 < y]
            candidates.sort(key=lambda seg: seg[0][1])
        else:
            if is_upright:
                candidates = [((u1, v1), (u2, v2)) for ((u1, v1), (u2, v2)) in overlaps if u1 > x]
            else:
                candidates = [((u1, v1), (u2, v2)) for ((u1, v1), (u2, v2)) in overlaps if u1 < x]
            candidates.sort(key=lambda seg: seg[0][0])
        next = ((u1, v1), (u2, v2)) = candidates[0] if is_upright else candidates[-1]

        # Find the point of intersection:
        if is_vert:
            y = v1
        else:
            x = u1
        if (x, y) == start:
            break

        # Turn left if possible:
        if is_vert:
            if is_upright:
                is_upright = u1 >= x
            else:
                is_upright = u2 > x
        else:
            if is_upright:
                is_upright = v2 > y
            else:
                is_upright = v1 >= y
        is_vert = not is_vert

        ((x1, y1), (x2, y2)) = seg = next
    return result


def screw_points(n, (wd, ht)):
    """Return centres of holes for screws evenly distributed around rect.

    Arguments –
        n – total numer of screws; must be an even numebr ≥ 4
        wd, ht – size of rect the centres of the holes are to be distributed
    """
    left, right = -0.5 * wd, 0.5 * wd
    bottom, top = -0.5 * ht, 0.5 * ht
    rem = (n - 4) // 2  # How many to split between sides.
    vert_count = int(max(0, round(ht * rem - wd) / (wd + ht)))
    # According to some scribbles I made on paper.
    zs = [(x, i * ht / float(vert_count + 1) - 0.5 * ht) for i in range(1, vert_count + 1) for x in (left, right)]
    horiz_count = rem - vert_count
    zs.extend((i * wd / float(horiz_count + 1) - 0.5 * wd, y) for i in range(0, horiz_count + 2) for y in (bottom, top))

    return zs
