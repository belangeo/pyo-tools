# Copyright 2018 Olivier Belanger
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

from pyo import *

class BLOsc(PyoObject):
    """
    Band-limited oscillator that can crossfade between multiple waveforms.

    This oscillator can produce, according to its `shape` argument, a waveform
    that crossfades between a sawtooth, a square and a triangle waveform. The
    harmonics of the signal will never exceed the nyquist frequency (half the
    sampling rate).

    The sawtooth, square and triangle shapes are obtained by manipulating a
    Band-Limited Impulse Train (BLIT) with integration processes and comb filters.

    :Parent: :py:class:`PyoObject`

    :Args:

        freq: float or PyoObject, optional
            Fundamental frequency in cycles per second. Fundamental must be in
            the range 20 to 4000 Hz. Defaults to 100.
        bright: float or PyoObject, optional
            Brightness of the waveform, used to compute the number of harmonics
            for the given fundamental frequency. If set to 1, all harmonics below
            the nyquist frequency will be present. 0 means only a few harmonics.
            Defaults to 1.
        shape: float or PyoObject, optional
            Shape of the waveform. The range 0 to 1 will produce a crossfade
            between a sawtooth, a square and a triangle waveform.
            Defaults to 0.
        
    >>> s = Server().boot()
    >>> s.start()
    >>> from pyotools import *
    >>> bright = Sine(freq=[.1,.15]).range(0.1, 0.9)
    >>> shape = Sine(freq=[.2,.25]).range(0, 1)
    >>> blo = BLOsc(freq=200, bright=bright, shape=shape, mul=0.3).out()
    
    """
    def __init__(self, freq=100, bright=1, shape=0, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        # Raw arguments so that we can retrieve them with the attribute syntax.
        self._freq = freq
        self._bright = bright
        self._shape = shape
        # Audio conversions to facilitate computation.
        self._afreq = Sig(self._freq)
        self._abright = Sig(self._bright)
        self._ashape = Sig(self._shape)
        # Clipping values.
        self._cfreq = Clip(self._afreq, 20, 4000)
        self._cbright = Clip(self._abright, min=0, max=1, mul=0.9, add=0.1)
        self._cshape = Clip(self._ashape, min=0, max=1, mul=0.9999)

        sr = self._afreq.getSamplingRate()
        oneOverSr = 1.0 / sr

        # Compute the number of harmonics to generate.
        self._harms = sr / 2.1 / self._cfreq * self._cbright
        self._charms = Max(self._harms, 1.0)
        self._charms2 = self._charms + 1
        self._frac = self._charms - Floor(self._charms)

        # Scaling.
        self._ampscl = Scale(self._cbright, outmin=0.02, outmax=1)
        self._sqrscl = Scale(self._cfreq, 20, 4000, 0.0625, 0.125)
        self._triscl = Scale(self._cfreq, 20, 4000, 0.01, 0.5)

        # zero-centered impulse train.
        self._blit1 = Blit(freq=self._cfreq, harms=self._charms)
        self._blit2 = Blit(freq=self._cfreq, harms=self._charms2)
        self._blit = Interp(self._blit1, self._blit2, self._frac)
        self._train = DCBlock(self._blit)

        # Integrated impulse train = sawtooth.
        self._saw = DCBlock(Delay(self._train, oneOverSr, 1, oneOverSr))

        # sawtooth + comb filter = square wave.
        self._dlay = 1.0 / self._cfreq * 0.5
        self._sqr = Delay(self._saw, self._dlay, 0, 0.03, -1, self._saw)
        self._sqr2 = Delay(self._sqr, self._dlay, 0, 0.03, -1, self._sqr)
        self._sqr3 = Delay(self._sqr2, self._dlay, 0, 0.03, -1, self._sqr2)
        self._sqr4 = Delay(self._sqr3, self._dlay, 0, 0.03, -1, self._sqr3)
        self._square = self._sqr4 * self._sqrscl

        # Integrated square wave = triangle wave.
        self._tri = DCBlock(Delay(self._square, oneOverSr, 1, oneOverSr))

        # Linearly interpolate between the three waveforms.
        self._sawtab = LinTable([(0,1), (300,0), (600,0)], size=600)
        self._sqrtab = LinTable([(0,0), (300,1), (600,0)], size=600)
        self._tritab = LinTable([(0,0), (300,0), (600,1)], size=600)
        self._index = Scale(self._cshape, exp=0.75)
        self._sawgain = Pointer(self._sawtab, self._index)
        self._sqrgain = Pointer(self._sqrtab, self._index)
        self._trigain = Pointer(self._tritab, self._index)
        self._choose = (self._saw * self._sawgain + self._square * self._sqrgain +
                        self._tri * self._triscl * self._trigain) * self._ampscl

        # A Sig is the best way to properly handle "mul" and "add" arguments.        
        self._output = Sig(self._choose, mul, add)
        # Create the "_base_objs" attribute. This is the object's audio output.
        self._base_objs = self._output.getBaseObjects()

    def setFreq(self, x):
        """
        Replace the `freq` attribute.

        :Args:

            x: float or PyoObject
                New `freq` attribute.

        """
        self._freq = x
        self._afreq.value = x

    def setBright(self, x):
        """
        Replace the `bright` attribute.

        :Args:

            x: float or PyoObject
                New `bright` attribute.

        """
        self._bright = x
        self._abright.value = x

    def setShape(self, x):
        """
        Replace the `shape` attribute.

        :Args:

            x: float or PyoObject
                New `shape` attribute.

        """
        self._shape = x
        self._ashape.value = x

    def play(self, dur=0, delay=0):
        for key in self.__dict__.keys():
            if isinstance(self.__dict__[key], PyoObject):
                self.__dict__[key].play(dur, delay)
        return PyoObject.play(self, dur, delay)

    def stop(self):
        for key in self.__dict__.keys():
            if isinstance(self.__dict__[key], PyoObject):
                self.__dict__[key].stop()
        return PyoObject.stop(self)

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        for key in self.__dict__.keys():
            if isinstance(self.__dict__[key], PyoObject):
                self.__dict__[key].play(dur, delay)
        return PyoObject.out(self, chnl, inc, dur, delay)

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(20, 4000, "log", "freq", self._freq),
                          SLMap(0, 1, "lin", "bright", self._bright),
                          SLMap(0, 1, "lin", "shape", self._shape),
                          SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def freq(self):
        """float or PyoObject. Fundamental frequency in cycles per second.""" 
        return self._freq
    @freq.setter
    def freq(self, x): self.setFreq(x)

    @property
    def bright(self):
        """float or PyoObject. Brightness between 0 and 1.""" 
        return self._bright
    @bright.setter
    def bright(self, x): self.setBright(x)

    @property
    def shape(self):
        """float or PyoObject. Waveform shape between 0 and 1.""" 
        return self._shape
    @shape.setter
    def shape(self, x): self.setShape(x)

if __name__ == "__main__":
    # Test case...
    s = Server().boot()

    lfo = Sine(freq=[0.04, 0.05]).range(0, 1)
    lfo2 = Sine(freq=0.06).range(0.5, 1)
    #m = Metro(0.25).play()
    #amp = TrigEnv(m, CosTable([(0,0),(256,0.3),(7800,0.3),(8192,0)]), dur=0.25)
    #fr = TrigChoice(m, midiToHz([36,43,48,51,55,58,60]))
    blo = BLOsc(freq=80, bright=lfo2, shape=lfo, mul=0.5).out()
    blo.ctrl()

    sc = Scope(blo)
    sp = Spectrum(blo)

    s.gui(locals())
