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

class FatBass(PyoObject):
    """
    Modulated Pulse-Width-Modulation oscillator with resonant lowpass filter.

    This generator contains a carrier unipolar square wave oscillator that is
    modulated by a square wave bipolar oscillator. The modulator's frequency
    is interpolated between one or two octaves below the carrier's frequency.
    A 4-pole 24dB/oct resonant lowpass filter is applied after the modulation.

    :Parent: :py:class:`PyoObject`

    :Args:

        freq: float or PyoObject, optional
            Frequency in cycles per second. Defaults to 100.
        octave: float or PyoObject, optional
            This argument linearly interpolates between a square wave oscillator
            2 octaves below the fundamental frequency and another square wave
            oscillator 1 octave below the fundamental frequency. The result 
            produces the modulating oscillator. Defaults to 0.
        duty: float or PyoObject, optional
            Duty cycle of the carrier oscillator, ie. the fraction of the whole
            period, between 0 and 1, spent on the positive value. Defaults to 0.5.
        cutoff: float or PyoObject, optional
            Cutoff frequency of the lowpass filter in Hz. Defaults to 1000.
        res: float or PyoObject, optional
            Amount of resonance of the lowpass filter, between 0 and 2. Values
            above 1 produces a self-oscillating filter. Defaults to 0.
        
    >>> s = Server().boot()
    >>> s.start()
    >>> from pyotools import *
    >>> octave = Sine([0.15,0.13]).range(0.1, 0.9)
    >>> duty = Sine([0.07, .1]).range(0.1, 0.5)
    >>> osc = FatBass(80, octave, duty, 2500, 0, mul=0.4).out()
    
    """
    def __init__(self, freq=100, octave=0, duty=0.5, cutoff=5000, res=0, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        # Raw arguments so that we can retrieve them with the attribute syntax.
        self._freq = freq
        self._octave = octave
        self._duty = duty
        self._cutoff = cutoff
        self._res = res
        # Audio conversion to declare the comparison only once.
        self._afreq = Sig(self._freq)
        self._aoctave = Sig(self._octave)
        self._aduty = Sig(self._duty)
        # Cycle running phase.
        self._cycle = Phasor(self._afreq)
        # Clip the duty stream
        self._cduty = Clip(self._aduty, 0, 1)
        # Split the cycle in two parts, 0 and 1. Rescale the cuty between 0.05 and 0.95.
        self._unisqr = self._cycle < Scale(self._cduty, 0, 1, 0.05, 0.95)
        # 2 octaves down bipolar modulator.
        self._mod1 = Phasor(self._afreq * 0.25)
        self._sqr1 = (self._mod1 < 0.5) * 2 - 1
        # 1 octave down bipolar modulator.
        self._mod2 = Wrap(self._mod1 * 2)
        self._sqr2 = (self._mod2 < 0.5) * 2 - 1
        # Linear interpolation between the two modulators.
        self._modu = self._sqr1 + (self._sqr2 - self._sqr1) * self._aoctave
        # Modulate the unipolar oscillator with the interpolated modulator
        # and lowpass filter the result.
        self._filter = MoogLP(self._unisqr * self._modu, cutoff, res)
        # A Sig is the best way to properly handle "mul" and "add" arguments.        
        self._output = Sig(self._filter, mul, add)
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

    def setOctave(self, x):
        """
        Replace the `octave` attribute.

        :Args:

            x: float or PyoObject
                New `octave` attribute.

        """
        self._octave = x
        self._aoctave.value = x

    def setDuty(self, x):
        """
        Replace the `duty` attribute.

        :Args:

            x: float or PyoObject
                New `duty` attribute.

        """
        self._duty = x
        self._aduty.value = x

    def setCutoff(self, x):
        """
        Replace the `cutoff` attribute.

        :Args:

            x: float or PyoObject
                New `cutoff` attribute.

        """
        self._cutoff = x
        self._filter.freq = x

    def setRes(self, x):
        """
        Replace the `res` attribute.

        :Args:

            x: float or PyoObject
                New `res` attribute.

        """
        self._res = x
        self._filter.res = x

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
        self._map_list = [SLMapFreq(self._freq),
                          SLMap(0, 1, "lin", "octave", self._octave),
                          SLMap(0, 1, "lin", "duty", self._duty),
                          SLMap(50, 10000, "log", "cutoff", self._cutoff),
                          SLMap(0, 2, "lin", "res", self._res),
                          SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def freq(self):
        """float or PyoObject. Fundamental frequency in cycles per second.""" 
        return self._freq
    @freq.setter
    def freq(self, x): self.setFreq(x)

    @property
    def octave(self):
        """float or PyoObject. octave shifting between 0 and 1.""" 
        return self._octave
    @octave.setter
    def octave(self, x): self.setOctave(x)

    @property
    def duty(self):
        """float or PyoObject. Duty cycle of the carrier between 0 and 1.""" 
        return self._duty
    @duty.setter
    def duty(self, x): self.setDuty(x)

    @property
    def cutoff(self):
        """float or PyoObject. Lowpass filter cutoff frequency.""" 
        return self._cutoff
    @cutoff.setter
    def cutoff(self, x): self.setCutoff(x)

    @property
    def res(self):
        """float or PyoObject. Lowpass filter resonance.""" 
        return self._res
    @res.setter
    def res(self, x): self.setRes(x)

if __name__ == "__main__":
    s = Server().boot()

    octave = Sine([0.15,0.13]).range(0.1, 0.9)
    duty = Sine([0.07, .1]).range(0.1, 0.5)
    osc = FatBass(80, octave, duty, 2500, 0, mul=0.4).out()
    osc.ctrl()

    sc = Scope(osc)
    sp = Spectrum(osc)

    s.gui(locals())
