"""Parse the ‘raw data’ format of the Keyboard Layout Editor.

https://github.com/ijprest/keyboard-layout-editor/wiki/Serialized-Data-Format

"""

from __future__ import print_function, unicode_literals
import json
import re


class Key(object):
    """Information about a keyboard key."""

    def __init__(self, label, pos, size, pos2=None, size2=None):
        """Create instance with this key data."""
        self.pos = pos
        self.x, self.y = pos
        self.size = size
        self.w, self.h = size
        if pos2 or size2:
            x2, y2 = pos2 or (0, 0)
            self.pos2 = (x2 + self.x, y2 + self.y)
            self.size2 = size2 or (1, 1)


class Keyboard(object):
    """Information about the keyboard as a whole."""

    pass


bare_attr_name = re.compile(r'(?<=[,{])(\w+):')


def json_from_kle(kle):
    """Convert from KLE’s human-friendly format to echt JSON."""
    return json.loads('[%s]' % bare_attr_name.sub('"\\1":', kle))


def parse_kle(kle):
    """Parse the raw data from the keyboard layout editor."""
    kss = json_from_kle(kle)
    y = 0
    w = h = 1  # Defaults for size
    pos2 = size2 = None
    for ks in kss:
        x = 0
        for k in ks:
            if isinstance(k, basestring):
                yield Key(k, (x, y), (w, h), pos2, size2)
                x += w
                w = h = 1
                pos2 = size2 = None
            else:
                x += k.get('x', 0)
                y += k.get('y', 0)
                w = k.get('w', 1)
                h = k.get('h', 1)
                if 'x2' in k or 'y2' in k:
                    pos2 = k.get('x2', 0), k.get('y2', 0)
                if 'w2' in k or 'h2' in k:
                    size2 = k.get('w2', 1), k.get('h2', 1)
        y += 1
