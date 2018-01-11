# Copyright 2017 Olivier Belanger
#
# This file is part of pyo-tools.
#
# pyo-tools is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyo-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pyo-tools. If not, see <http://www.gnu.org/licenses/>.

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

* FatBass: Modulated Pulse-Width-Modulation oscillator with resonant lowpass filter.

    FatBass(freq=100, octave=0, duty=0.5, cutoff=5000, res=0, mul=1, add=0)

* BLOsc: Band-limited oscillator that can crossfade between multiple waveforms.

    BLOsc(freq=100, bright=1, shape=0, mul=1, add=0)

* HarmoFilter: Filter that removes every nth harmonic of a fundamental frequency.

    HarmoFilter(input, freq, harm=2, mul=1, add=0)

* MatrixVerb: Delay-line rotating-matrix reverb inspired by Miller Puckette's rev3~.

    MatrixVerb(input, liveness=0.7, depth=0.7, crossover=3500, highdamp=0.75,
               balance=0.25, numechoes=8, quality=4, filtorder=2,
               echoesrange=[0.03, 0.08], echoesmode="linmin", 
               matrixrange=[0.05, 0.15], matrixmode="linmin", mul=1, add=0)

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
from .fatbass import FatBass
from .blosc import BLOsc
from .harmofilter import HarmoFilter
from .matrixverb import MatrixVerb

PYOTOOLS_VERSION = "0.1.0"

def version():
    return PYOTOOLS_VERSION
