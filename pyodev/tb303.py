#!/usr/bin/env python
# encoding: utf-8
from pyo import *

class TB303(PyoObject):
    """
    Simple emulation of the Roland TB-303 oscillator.

    The TB303 object produces a square wave with control for the cuty cycle.
    This waveform is used to excite a 4-poles 24dB/octave resonant lowpass
    filter with controls for the cutoff frequency and the amount of resonance.

    :Parent: :py:class:`PyoObject`

    :Args:

        freq: float or PyoObject, optional
            Frequency in cycles per second. Defaults to 100.
        duty: float or PyoObject, optional
            Duty cycle, ie. the fraction of the whole period, between 0 and 1
            spent on the positive value. Defaults to 0.5.
        cutoff: float or PyoObject, optional
            Cutoff frequency of the lowpass filter in Hz. Defaults to 1000.
        res: float or PyoObject, optional
            Amount of resonance of the lowpass filter, between 0 and 2. Values
            above 1 produces a self-oscillating filter. Defaults to 1.
        octave: float or PyoObject, optional
            Transposition of the oscillator frequency as octave multiplier.
            The defaults, -3, means three octave below the frequency given as
            `freq` argument. Fractional value will detune the oscillator.
        
    >>> s = Server().boot()
    >>> s.start()
    >>> from pyodev import *
    >>> duty = Sine(freq=[.1, .15]).range(0.25, 0.75)
    >>> out = TB303(750, duty, 3500, 0.1, octave=[-4, -3], mul=0.3).out()
    
    """
    def __init__(self, freq=100, duty=0.5, cutoff=1000, res=1, octave=-3, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        # Raw arguments so that we can retrieve them with the attribute syntax.
        self._freq = freq
        self._duty = duty
        self._cutoff = cutoff
        self._res = res
        self._octave = octave
        # Audio conversion to facilitate the computation of the delay time.
        self._afreq = Sig(self._freq)
        self._aduty = Sig(self._duty)
        self._atranspo = Sig(self._octave, mul=12, add=60)
        # Cycle running phase.
        self._cycle = Phasor(self._afreq * MToT(self._atranspo))
        # Split the cycle in two parts, 0 and 1 and convert to bipolar waveform.
        self._square = (self._cycle < Clip(self._aduty, 0.02, 0.98)) - 0.5
        # Use the square wave to excite a resonant lowpass filter.
        self._filter = MoogLP(self._square, freq=cutoff, res=res)
        # Remove D and properly handle "mul" and "add" arguments.
        self._output = DCBlock(self._filter, mul=mul, add=add)
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

    def setOctave(self, x):
        """
        Replace the `octave` attribute.

        :Args:

            x: float or PyoObject
                New `octave` attribute.

        """
        self._octave = x
        self._atranspo.value = x

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMapFreq(self._freq),
                          SLMap(0, 1, "lin", "duty", self._duty),
                          SLMap(50, 10000, "log", "cutoff", self._cutoff),
                          SLMap(0, 2, "lin", "res", self._res),
                          SLMap(-4, 4, "lin", "octave", self._octave),
                          SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def freq(self):
        """float or PyoObject. Fundamental frequency in cycles per second.""" 
        return self._freq
    @freq.setter
    def freq(self, x): self.setFreq(x)

    @property
    def duty(self):
        """float or PyoObject. Duty cycle between 0 and 1.""" 
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

    @property
    def octave(self):
        """float or PyoObject. Transposition in octave multiplier.""" 
        return self._octave
    @octave.setter
    def octave(self, x): self.setOctave(x)

if __name__ == "__main__":
    # Test case...
    s = Server().boot()
    s.amp = 0.1

    duty = Sine(freq=[.1, .15]).range(0.25, 0.75)
    out = TB303(750, duty, 3500, 0.1, octave=[-4, -3]).out()
    out.ctrl()

    sc = Scope(out)

    s.gui(locals())

