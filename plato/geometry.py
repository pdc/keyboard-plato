# -* coding: UTF-8 -*-

"""Claculating simple geometry.

Most shapes in this diagram are composed of vertical and horizontal lines.
The algorithms are therefore a bit simplistic.
"""

from __future__ import print_function, unicode_literals
from heapq import heappush, heappop
from math import pi, atan2
import sys


def adjusted_coords(x, width, adjustment):
    """Return a (left, right) or (bottom, top) pair or coordinates.

    Arguments –
        x – centre point
        width – how far apart the 2 points are
        adjustment – extra distance to be added each end (usually kerf or corner radius)

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
    """Find the union of n overlapping polygons.

    Limitations: finds one contiguous polygon; holes created by overlapping
    in clever ways will be filled in, and outlying islands may be dropped.

    Arguments –
        zss – list of shapes, each shape is a list of points

    Retunes –
        A lit ofpoints describing overlapping shape
    """
    segs = {seg for zs in zss for seg in segments(zs)}
    z0, z1 = min(segs, key=(lambda seg: (seg[0], -seg[1][1])))
    result = []
    count = 0
    while True:
        count += 1
        if count > 100:
            # This only happens if there is a bug.
            print(segs, file=sys.stderr)
            print(result[:10], '...', file=sys.stderr)
            sys.exit('Shape unexpectedly too complicated')
            break
        if len(result) > 1 and are_colinear(result[-2], result[-1], z0):
            result[-1] = z0
        else:
            result.append(z0)
        z, zs = nearest_intersections((z0, z1), segs)
        z0, z1 = leftmost_turn((z0, z1), z, zs)

        z0 = (round(z0[0], 3), round(z0[1], 3))
        z1 = (round(z1[0], 3), round(z1[1], 3))

        if z0 == result[0]:
            break
    if len(result) > 2 and are_colinear(result[-2], result[-1], result[0]):
        result.pop()
    return result


def segment_intersection(((x0, y0), (x1, y1)), ((x2, y2), (x3, y3))):
    """Find a point on the intersection between these two line segments.

    Arguments:
        ((x0, y0), (x1, y1)) – defines a line segment of interest
        ((x2, y2), (x3, y3)) – another line segment that might intersect it

    Intersections exclude (x0, y0) but may be at (x1, y1).

    Returns t, (x, y)
        where 0 < t ≤ 1 is the fraction of the distance from (x0, y0) to (x1, y1),
        and (x, y) is the point of intersection,
        or None, None
    """
    # Some algebra happened.
    d = ((x2 - x3) * (y0 - y1) - (x0 - x1) * (y2 - y3))
    if d == 0:
        return None, None
    b = (float(x0 - x1) * (y3 - y1) - (x3 - x1) * (y0 - y1)) / d
    a = (b * (x2 - x3) + (x3 - x1)) / (x0 - x1) if x0 != x1 else (b * (y2 - y3) + (y3 - y1)) / (y0 - y1)
    if 0.0 <= a <= 1.0 and 0.0 <= b <= 1.0:
        return 1 - a, (b * x2 + (1 - b) * x3, b * y2 + (1 - b) * y3)
    return None, None


def nearest_intersections(seg0, segs):
    """Find the nearest intesection between this line segment and those in segs.

    Argumebts – 
        seg0 – where we are and the direction we are travelling
        segs – lines that might be crossing this one
    Returns ((x, y), zs)
        where (x, y) is the nearest endpoint
        and each point z in zs is an endpoint of one of the intersecting segments.
    """
    heap = []
    for seg in segs:
        a, z = segment_intersection(seg0, seg)
        if a:
            heappush(heap, (a, z, seg))
    a1, z1, seg1 = heappop(heap)
    ends = set(seg1)
    while heap:
        a, z, seg = heappop(heap)
        if a != a1:
            break
        ends.update(seg)
    ends.add(seg0[1])
    ends.discard(z1)
    return z1, ends


def leftmost_turn(((x0, y0), (x1, y1)), (x, y), zs):
    """Find the line segment intersecting at the leftmost angle relative to initial segment.

    Arguments:
        (x0, y0) – where we started
        (x1, x2) – direction travelling in
        (x, y) – where intersected one or more alternative line segments
        zs – set of points definign direction to move in
    """
    if len(zs) == 1:
        return (x, y), zs.pop()
    theta = atan2(y1 - y, x1 - x)  # Direction currently headed.
    def fun((xn, yn)):
        phi = atan2(yn - y, xn - x) - theta
        if phi < -pi:
            phi += 2 * pi
        elif phi > pi:
            phi -= 2 * pi
        # Tie-breaker is length of segment:
        len2 = (yn - y) * (yn - y) + (xn - x) * (xn - x)
        return phi, len2
    zm = max(zs, key=fun)
    return (x, y), zm


def are_colinear((x0, y0), (x1, y1), (x2, y2)):
    """Check whether these points fall on a line."""
    if x0 != x2:
        a = (x1 - x2) / (x0 - x2)  # Find a such that x1 = a * x0 + (1 - a) * x2
        yn = a * y0 + (1 - a) * y2  # See where this would put the point betwen them.
        return yn == y1
    else:
        a = (y1 - y2) / (y0 - y2)  # Find a such that y1 = a * y0 + (1 - a) * y2
        xn = a * x0 + (1 - a) * x2  # See where this would put the point betwen them.
        return xn == x1


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
