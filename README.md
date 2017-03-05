Keyboard Plato
==============

Python modules to render CAD drawings for the plate for a custom computer keyboard.

The plate is a flat plane with holes in it in to which the switch
modules for the keys are snapped. Usually it is hidden inside the
keyboard case, but hand-built keyboards tend to leave it exposed as the
top of the case.


What this does
--------------

This software does the same thing as online services like the [swillkb Plate &
Case Builder][] and [Keyboard CAD Assistant][]: it takes the serialized
data from the [Keyboard Layout Editor][] and writes DXF and SVG files
that might be converted in to instructions for a CNC mill or laser cutter.

Part of the motivation for rolling my own rather than exploiting the
Swill version was plan to use acrylic or wood rather than metal for the
plate, so I need to create an ‘under-plate’ support layer. This has
almost the same design but with a few cutouts that allow the switches
to clip on to the top layer.


Usage
-----

Create a Python [virtualenv][] with [virtualenvwrapper][] or otherwise and install the dependencies:

    mkvirtualenv plato
    pip install -r requirements.txt

Now run the command that writes the plate.

    ./write_plate.py

The driver command `write_plate.py` does not yet have arguments; instead it is hard-coded
to read `x1.kle` and generate DXF and SVG files for the plate,
the under-plate, an indicative diagram of the key cap outlines,
and a combined image that shows what the combination
might look like. The DXF version is hard to display if you don’t have
CAD software, which is where the SVG file is convenient—it can be
loaded in to your favourite web browser and you should be able to zoom
and pan with your browser’s ususal controls.

The SVG version sets the line widths to a representative _kerf_ width,
that is, it represents the thin slice of material that is destroyed by
the laser. The effectinve edge of the holes will therefore be the outer
edge of the outline of the hole.

  [Keyboard CAD Assistant]: http://www.keyboardcad.com/
  [Keyboard Layout Editor]: http://www.keyboard-layout-editor.com/
  [swillkb Plate & Case Builder]: http://builder.swillkb.com/


  [I built a keyboard from scratch]: http://gizmodo.com/i-built-a-keyboard-from-scratch-1649325860

  [virtualenv]: https://virtualenv.pypa.io/en/latest/
  [virtualenvwrapper]: https://virtualenvwrapper.readthedocs.io/en/latest/
