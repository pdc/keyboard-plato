#! /usr/bin/env python

"""Script to generate a DXF file."""

from __future__ import print_function, unicode_literals
import argparse
import sys

from plato.dxf_plato import DXFPlato
from plato.svg_plato import SVGPlato
from plato.kle_parser import Key, parse_kle


FORMATS = ['svg', 'dxf']
LAYERS = ['plate', 'under', 'caps', 'combined']
TESTS = ['size']

FORMAT_CLASSES = {
    'dxf': DXFPlato,
    'svg': SVGPlato,
}


def write_plate(keys, format, layer, out_file):
    """Write plate with these keys to this file."""
    plato = FORMAT_CLASSES[format](out_file, case_thickness=5, padding=5, corner_radius=3, kerf=0.18)
    plato.calculate_layout(keys)
    plato.draw_outside()
    if layer in ['plate', 'combined']:
        plato.draw_cherry_mx_switches(keys)
    if layer in ['under', 'combined']:
        plato.draw_cherry_mx_under_switches(keys)
    if layer in ['caps', 'combined']:
        plato.draw_screw_heads(8, indent=2.5)
        plato.draw_key_caps(keys)
    plato.draw_screws(8, indent=2.5)
    plato.save()


def write_tester(format, layer, out_file):
    """Write plate with these keys to this file."""
    plato = FORMAT_CLASSES[format](out_file,
        width_in_units=15, height_in_units=2, unit_mm=19,
        case_thickness=3.5, padding=1, corner_radius=2, kerf=0.18)
    plato.draw_outside()
    for i in range(15):
        k = (i - 4) * 0.05  # Range from -0.20 to +0.50
        key = Key(str(k), (i, 0), (1, 2))
        if layer in ['plate', 'combined']:
            plato.draw_cherry_mx_switches([key], kerf=k)
        if layer in ['under', 'combined']:
            plato.draw_cherry_mx_under_switches([key], kerf=k)
        if layer in ['caps', 'combined']:
            plato.draw_key_caps([key])
    if layer in ['caps', 'combined']:
        plato.draw_screw_heads(8, indent=2)
    plato.draw_screws(8, indent=2)
    plato.save()


def arg_parser():
    """Return an instance of argparse for this app."""
    parser = argparse.ArgumentParser(description='Write CAD files for a custom keyboard plate.')
    parser.add_argument(
        'kle_file', metavar='FILE', nargs='?',
        help='a file containing raw data from keyboard-layout-editor.org')
    parser.add_argument(
        '--formats', '-g', action='append', default=[],
        help='comma-separated list of output formats (%s)' % ', '.join(FORMATS))
    parser.add_argument(
        '--layers', '-l', action='append', default=[],
        help='comma-separated list of layers to write (%s)' % ', '.join(LAYERS))
    parser.add_argument(
        '--tester', '-t', nargs='?', action='store', const='size',
        help='create test layout insted of using a keynoard layout')
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='write more messages')
    return parser

def unpack_list_option(what, wordss, permitted_words):
    """Given a list of comma-separated keywords return list of words.

    Arguments –
        what – how to refer to the keywords in error messages
        wordss – the list of strings, each potentially comma-separated list
        permitted_words – the words that are permitted
    """
    words = [x.strip() for s in wordss for x in s.split(',')] if wordss else permitted_words[:1]
    unknown = set(words).difference(permitted_words)
    if unknown:
        sys.exit('%s: unknown %s%s' % (', '.join(words), what, 's' if len(words) != 1 else ''))
    return words


def main(argv=None):
    options = arg_parser().parse_args(argv)

    formats = unpack_list_option('format', options.formats, FORMATS)
    layers = unpack_list_option('layer', options.layers, LAYERS)

    if options.tester:
        for format in formats:
            for layer in layers:
                out_file = '%s.%s.%s' % (options.tester, layer, format)
                write_tester(out_file=out_file, format=format, layer=layer)
                if options.verbose:
                    print('Wrote', format.upper(), 'to', out_file)
    if options.kle_file:
        with open(options.kle_file, 'r') as input:
            kle = input.read().decode('UTF-8')
        keys = parse_kle(kle)

        for format in formats:
            for layer in layers:
                out_file = '%s.%s' % (layer, format)
                write_plate(keys, out_file=out_file, format=format, layer=layer)
                if options.verbose:
                    print('Wrote', format.upper(), 'to', out_file)

if __name__ == '__main__':
    sys.exit(main())
