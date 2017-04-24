"""
Description
===========

The `pyotools` package is a collection of python classes for building audio
fxs and synths with pyo. This package assumes that the latest stable release
of pyo is already installed under the current distribution of python. Pyo
actually supports python 2.7 and 3.5 (but can probably be compiled under any
version of python 3).

Pyo is available on ajaxsoundstudio.com:

    http://ajaxsoundstudio.com/software/pyo/

Pyo also offers some GUI facilities to control or visualize the audio
processing. If you want to use all of pyo’s GUI features, you must install
WxPython 3.0 (classic for python 2.7 and phoenix for python 3.5), available
at:

    https://wxpython.org

Usage
=====

In order to use the classes in pyotools package, you should import pyo first,
and then import pyotools. The order is important especially in the case where
the double precision version of pyo is to be used. The choice of precision is
made when importing pyo (or pyo64). pyotools will then follow the choice made
previously.

Typical program will look like this:

>>> import pyo
>>> import pyotools
>>> s = pyo.Server().boot()
>>>
>>> # use pyo and pyotools objects to build a processing chain.
>>>
>>> s.gui(locals())

One can also run pyotools object's example through the pyo `example` function:

>>> import pyo
>>> import pyotools
>>> pyo.example(pyotools.PWM)

Classes
=======

Available classes within the pyotools package are:

* PWM: Pulse-Width-Modulation oscillator with optional linear-phase lowpass filter.

    PWM(freq=100, phase=0, duty=0.5, damp=0, mul=1, add=0)

* VCO: Voltage-controlled oscillator with optional linear-phase lowpass filter.

    VCO(freq=100, phase=0, shape=0, damp=0, mul=1, add=0)

* TB303: Simple emulation of the Roland TB-303 oscillator.

    TB303(freq=100, duty=0.5, cutoff=1000, res=1, octave=-3, mul=1, add=0)

* OscSync: A soft sync oscillator which is reset according to a master frequency.

    OscSync(table, master=100, slave=110, xfade=0.5, mul=1, add=0)

* HarmoFilter: Filter that removes every nth harmonic of a fundamental frequency.

    HarmoFilter(input, freq, harm=2, mul=1, add=0)

To see the complete documentation of a specific class (PWM in this example),
type in a python interpreter::

    import pyotools
    help(pyotools.PWM)

"""
from __future__ import absolute_import

from .pwm import PWM
from .vco import VCO
from .tb303 import TB303
from .oscsync import OscSync
from .harmofilter import HarmoFilter

PYOTOOLS_VERSION = "0.1.0"

def version():
    return PYOTOOLS_VERSION