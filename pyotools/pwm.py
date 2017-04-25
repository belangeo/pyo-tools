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

class PWM(PyoObject):
    """
    Pulse-Width-Modulation oscillator with optional linear-phase lowpass filter.

    This generator will oscillate between 1 and -1 according to its frequency,
    phase and duty cycle arguments, producing an idealized square wave. The
    term duty cycle describes the proportion of 'on' time to the regular
    interval or 'period' of time, that is the time spent on the positive value
    inside a single cycle.

    :Parent: :py:class:`PyoObject`

    :Args:

        freq: float or PyoObject, optional
            Frequency in cycles per second. Defaults to 100.
        phase: float or PyoObject, optional
            Phase of sampling, expressed as a fraction of a cycle (0 to 1).
            Defaults to 0.
        duty: float or PyoObject, optional
            Duty cycle, ie. the fraction of the whole period, between 0 and 1
            spent on the positive value. Defaults to 0.5.
        damp: int, optional
            Length, in samples, of the filter kernel used for lowpass filtering.
            The actual kernel length will be twice this value. Defaults to 0.
        
    >>> s = Server().boot()
    >>> s.start()
    >>> from pyotools import *
    >>> duty = Sine(freq=[.1, .15]).range(0.25, 0.75)
    >>> pwm = PWM(freq=100, phase=0, duty=duty, damp=6, mul=0.3).out()
    
    """
    def __init__(self, freq=100, phase=0, duty=0.5, damp=0, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        # Raw arguments so that we can retrieve them with the attribute syntax.
        self._freq = freq
        self._phase = phase
        self._duty = duty
        self._damp = damp
        # Audio conversion to declare the comparison only once.
        self._aduty = Sig(self._duty)
        # Cycle running phase.
        self._cycle = Phasor(freq, phase)
        # Split the cycle in two parts, 0 and 1.
        self._sqr = self._cycle < self._aduty
        # Convert to bipolar waveform.
        self._square = Sig(self._sqr, mul=2, add=-1)
        # Apply the lowpass filter.
        self._filter = IRWinSinc(self._square, freq=0, order=damp*2)
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
        self._cycle.freq = x

    def setPhase(self, x):
        """
        Replace the `phase` attribute.

        :Args:

            x: float or PyoObject
                New `phase` attribute.

        """
        self._phase = x
        self._cycle.phase = x

    def setDuty(self, x):
        """
        Replace the `duty` attribute.

        :Args:

            x: float or PyoObject
                New `duty` attribute.

        """
        self._duty = x
        self._aduty.value = x

    def setDamp(self, x):
        """
        Replace the `damp` attribute.

        :Args:

            x: int
                New `damp` attribute.

        """
        if x == self._damp:
            return
        self._damp = x
        self._filter = IRWinSinc(self._square, freq=0, order=x*2)
        self._output.value = self._filter

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
                          SLMapPhase(self._phase),
                          SLMap(0, 1, "lin", "duty", self._duty),
                          SLMap(0, 32, "lin", "damp", self._damp, res="int", dataOnly=True),
                          SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def freq(self):
        """float or PyoObject. Fundamental frequency in cycles per second.""" 
        return self._freq
    @freq.setter
    def freq(self, x): self.setFreq(x)

    @property
    def phase(self):
        """float or PyoObject. Phase of sampling between 0 and 1.""" 
        return self._phase
    @phase.setter
    def phase(self, x): self.setPhase(x)

    @property
    def duty(self):
        """float or PyoObject. Duty cycle between 0 and 1.""" 
        return self._duty
    @duty.setter
    def duty(self, x): self.setDuty(x)

    @property
    def damp(self):
        """int. High frequencies damping factor, in samples.""" 
        return self._damp
    @damp.setter
    def damp(self, x): self.setDamp(x)

if __name__ == "__main__":
    # Test case...
    s = Server().boot()
    duty = Sine([.1, .15]).range(0.25, 0.75)

    pwm = PWM(100, 0, duty, 6, 0.3).out()
    pwm.ctrl()

    sc = Scope(pwm)
    sp = Spectrum(pwm)

    s.gui(locals())