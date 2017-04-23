pyo-dev - ready-to-use audio classes for pyo
============================================

Description
-----------

The `pyodev` package is a collection of python classes for building audio
fxs and synths with pyo. This package assumes that the latest stable release
of pyo is already installed under the current distribution of python. Pyo
actually supports python 2.7 and 3.5 (but can probably be compiled under any
version of python 3).

Pyo is available on ajaxsoundstudio.com:

`http://ajaxsoundstudio.com/software/pyo/ <http://ajaxsoundstudio.com/software/pyo/>`_

Pyo also offers some GUI facilities to control or visualize the audio
processing. If you want to use all of pyo’s GUI features, you must install
WxPython 3.0 (classic for python 2.7 and phoenix for python 3.5), available
at:

`https://wxpython.org <https://wxpython.org>`_

Install
-------

To install under the current distribution of python, simply run the standard
setup script::

    python setup.py install

You will probably need to run this command as root.

Usage
-----

In order to use the classes in this package, you should first import pyo, and
then import pyodev. The order is important especially in the case where the
double precision version of pyo is to be used. The choice of precision is made
when importing pyo (or pyo64). Pyodev will then follow the choice made previously.

Typical program will look like this::

    import pyo
    import pyodev
    s = pyo.Server().boot()
    # use pyo or pyodev objects to build a processing chain.
    s.gui(locals())

One can also run pyodev object's example through the pyo `example` function::

    import pyo
    import pyodev
    pyo.example(pyodev.PWM)

Classes
-------

Available classes through this package are:

* PWM: Pulse-Width-Modulation oscillator with optional linear-phase lowpass filter.

    PWM(freq=100, phase=0, duty=0.5, damp=0, mul=1, add=0)

* DCO: Digitally-controlled oscillator with optional linear-phase lowpass filter.

    DCO(freq=100, phase=0, shape=0, damp=0, mul=1, add=0)

* HarmoFilter: Filter that removes every nth harmonic of a fundamental frequency.

    HarmoFilter(input, freq, harm=2, mul=1, add=0)

To see the complete documentation of a specific class (PWM in this example),
type in an interpreter::

    help(pyodev.PWM)

