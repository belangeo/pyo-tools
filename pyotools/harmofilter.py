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

from pyo import *

class HarmoFilter(PyoObject):
    """
    Filter that removes every nth harmonic of a fundamental frequency.

    HarmoFilter constructs a comb filter based on a fundamental frequency
    and the order of the first harmonic to remove. All multiples of that
    harmonic will also be filtered out.

    :Parent: :py:class:`PyoObject`

    :Args:

        input: PyoObject
            Input signal to filter.
        freq: float or PyoObject
            Fundamental frequency in cycle per second.
        harm: float or Pyoobject, optional
            Order of the first removed harmonic. Defaults to 2.

    >>> s = Server().boot()
    >>> s.start()
    >>> from pyotools import *
    >>> freq = Choice([200, 250, 300, 350, 400], freq=4)
    >>> ph = LFO(freq, sharp=1)
    >>> he = HarmoFilter(ph, freq, 3, mul=0.3).out()
    
    """
    def __init__(self, input, freq, harm=2, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        # Raw arguments so that we can retrieve them with the attribute syntax.
        self._input = input
        self._freq = freq
        self._harm = harm
        # Audio conversion to facilitate the computation of the delay time.
        self._afreq = Sig(self._freq)
        self._aharm = Sig(self._harm)
        # InputFader is used to allow crossfade on audio input changes.
        self._in_fader = InputFader(input)
        # Comb filter. Signal is delayed, reversed and added to the original.
        self._filter = Delay(input=self._in_fader,
                             delay=1.0/self._afreq/self._aharm, 
                             mul=-1,
                             add=self._in_fader)
        # A Sig is the best way to properly handle "mul" and "add" arguments.
        self._out = Sig(self._filter, mul=mul, add=add)
        # Create the "_base_objs" attribute. This is the object's audio output.
        self._base_objs = self._out.getBaseObjects()

    def setFreq(self, x):
        """
        Replace the `freq` attribute.

        :Args:

            x: float or PyoObject
                New `freq` attribute.

        """
        self._freq = x
        self._afreq.value = x

    def setHarm(self, x):
        """
        Replace the `harm` attribute.

        :Args:

            x: float or PyoObject
                New `harm` attribute.

        """
        self._harm = x
        self._aharm.value = x

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
        self._map_list = [SLMap(2, 20, "lin", "harm", self._harm, res="int"),
                          SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def freq(self):
        """float or PyoObject. Fundamental frequency in cycles per second.""" 
        return self._freq
    @freq.setter
    def freq(self, x): self.setFreq(x)

    @property
    def harm(self):
        """float or PyoObject. Order of the first removed harmonic.""" 
        return self._harm
    @harm.setter
    def harm(self, x): self.setHarm(x)

if __name__ == "__main__":
    # Test case...
    s = Server().boot()

    amp = Fader(fadein=0.1, mul=0.3).play()
    lfo = Sine(Randi(4, 6, 0.3), mul=Randi(0.01, 0.02, 0.2), add=1)
    mel = XnoiseMidi(12, freq=[2,4], x1=1, x2=0.2, mrange=[(48,73),(60,85)])
    freq = Snap(mel, [0,2,5,7,9], scale=1, mul=lfo)
    pfreq = Port(freq, 0.005, 0.005)
    wave = LFO(pfreq, sharp=1)
    hael = HarmoFilter(wave, pfreq, 3, mul=amp).out()
    hael.ctrl()
    # Show the spectrum of the higher voice
    sp = Spectrum(hael[1])

    s.gui(locals())
