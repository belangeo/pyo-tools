pyo-tools: ready-to-use audio classes for pyo
=============================================

Description
-----------

The `pyotools` package is a collection of python classes for building audio
fxs and synths with pyo. This package requires Python 3.7 or later and pyo.
The pyotools wheel is pure Python and works across Linux distributions and
CPU architectures, as well as other platforms supported by pyo. Pyo itself
contains native code and must be installed with the audio libraries required
by your platform.

Pyo is available on ajaxsoundstudio.com:

`http://ajaxsoundstudio.com/software/pyo/ <http://ajaxsoundstudio.com/software/pyo/>`_

Pyo also offers some GUI facilities to control or visualize the audio
processing. To use pyo's GUI features, install a compatible wxPython,
available at:

`https://wxpython.org <https://wxpython.org>`_

Install
-------

Install in a virtual environment::

    python3 -m venv .venv
    . .venv/bin/activate
    python -m pip install pyotools

Pip installs the pyo dependency if needed. On Linux, building pyo may require
system development packages; see pyo's installation instructions. To install
this checkout instead, use ``python -m pip install .``.

Build and publish
-----------------

Create release artifacts from a clean checkout in a virtual environment::

    python -m pip install --upgrade build twine
    python -m build
    python -m twine check --strict dist/*

This produces ``dist/pyotools-0.1.0-py3-none-any.whl`` and
``dist/pyotools-0.1.0.tar.gz``. The wheel contains no native binaries and
does not need a manylinux build. Both archives include the package license.

After checking the version in ``pyproject.toml`` and
``pyotools.PYOTOOLS_VERSION``, upload both artifacts using your PyPI account::

    python -m twine upload dist/pyotools-0.1.0-py3-none-any.whl dist/pyotools-0.1.0.tar.gz

PyPI does not allow replacing an uploaded release file. For a subsequent
release, update both version values and build into an empty ``dist/``
directory before uploading. Keep PyPI credentials outside this repository.

Usage
-----

In order to use the classes in pyotools package, you should import pyo first,
and then import pyotools. The order is important especially in the case where the
double precision version of pyo is to be used. The choice of precision is made
when importing pyo (or pyo64). pyotools will then follow the choice made previously.

Typical program will look like this::

    import pyo
    import pyotools
    s = pyo.Server().boot()
    # use pyo and pyotools objects to build a processing chain.
    s.gui(locals())

One can also run pyotools object's example through the pyo `example` function::

    import pyo
    import pyotools
    pyo.example(pyotools.PWM)

Classes
-------

Available classes within the pyotools package are:

* PWM: Pulse-Width-Modulation oscillator with optional linear-phase lowpass filter.

    PWM(freq=100, phase=0, duty=0.5, damp=0, mul=1, add=0)

* VCO: Voltage-controlled oscillator with optional linear-phase lowpass filter.

    VCO(freq=100, phase=0, shape=0, damp=0, mul=1, add=0)

* TB303: Simple emulation of the Roland TB-303 oscillator.

    TB303(freq=100, duty=0.5, cutoff=1000, res=1, octave=-3, mul=1, add=0)

* OscSync: A soft sync oscillator which is reset according to a master frequency.

    OscSync(table, master=100, slave=110, xfade=0.5, mul=1, add=0)

* FatBass: Modulated Pulse-Width-Modulation oscillator with resonant lowpass filter.

    FatBass(freq=100, octave=0, duty=0.5, cutoff=5000, res=0, mul=1, add=0)

* BLOsc: Band-limited oscillator that can crossfade between multiple waveforms.

    BLOsc(freq=100, bright=1, shape=0, mul=1, add=0)

* HarmoFilter: Filter that removes every nth harmonic of a fundamental frequency.

    HarmoFilter(input, freq, harm=2, mul=1, add=0)

* MatrixVerb: Delay-line rotating-matrix reverb inspired by Miller Puckette's rev3~.

    MatrixVerb(input, liveness=0.7, depth=0.7, crossover=3500, highdamp=0.75,
    balance=0.25, numechoes=8, quality=4, filtorder=2, echoesrange=[0.03, 0.08],
    echoesmode="linmin", matrixrange=[0.05, 0.15], matrixmode="linmin", mul=1, add=0)

To see the complete documentation of a specific class (PWM in this example),
type in a python interpreter::

    import pyotools
    help(pyotools.PWM)

