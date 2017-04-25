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

class OscSync(PyoObject):
    """
    A soft sync oscillator which is reset according to a master frequency.

    Oscillator sync is a feature in some synthesizers with two or more
    oscillators. One oscillator (the master) will restart the period of another
    oscillator (the slave), so that they will have the same base frequency.
    This can produce a sound rich with harmonics. The timbre can be altered
    by varying the slave frequency. This object implement the overlap sync
    method to produce a soft sync oscillator. The `xfade` argument control
    the crossfade time between the two overlap. To produce a hard sync
    oscillator, set the `xfade` argument to 0. 

    :Parent: :py:class:`PyoObject`

    :Args:

        table: PyoTableObject
            The table to use as the oscillator waveform.
        master: float or PyoObject, optional
            Master frequency in cycles per second. Defaults to 100.
        slave: float or PyoObject, optional
            Slave frequency in cycles per second. Defaults to 110.
        xfade: float or PyoObject, optional
            Crossfade time in milliseconds, between 0 and 5. Defaults to 0.5.
        
    >>> s = Server().boot()
    >>> s.start()
    >>> from pyotools import *
    >>> table = HarmTable([1, .5, .33, .25, .2, .167, .143, .125, .111, .1])
    >>> master = Sig([80, 80], mul=Randi(min=0.99, max=1.01, freq=[1.3, 1.2]))
    >>> slave = Sine([0.1, 0.15], mul=master, add=master*2)
    >>> sosc = OscSync(table, master, slave, xfade=0.5, mul=0.3).out()
    
    """
    def __init__(self, table, master=100, slave=110, xfade=0.5, mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        # Raw arguments so that we can retrieve them with the attribute syntax.
        self._table = table
        self._master = master
        self._slave = slave
        self._xfade = xfade
        # Audio conversion to facilitate the computation of the crossfade time.
        self._axfade = Sig(xfade)
        # The master running phase.
        self._phase = Phasor(master)
        # Output a trigger at the beginning of the cycle.
        self._trig = Select(self._phase < Delay1(self._phase), 1)
        # Overlap number (0 or 1)
        self._olap = Counter(self._trig, max=2)
        # Create a ramp from the overlap number.
        self._rtime = Clip(self._axfade, 0, 5, mul=0.001)
        self._ramp = SigTo(self._olap, time=self._rtime)
        # Amplitudes for the crossfade
        self._amp1 = Sig(1 - self._ramp, mul=0.5)
        self._amp2 = Sig(self._ramp, mul=0.5)
        # Triggers used to reset the oscillators
        self._trig1 = Select(self._olap, value = 0)
        self._trig2 = Select(self._olap, value = 1)
        # Two oscillators with independant reset and envelope
        self._osc1 = OscTrig(table, self._trig1, slave, interp=4, mul=self._amp1)
        self._osc2 = OscTrig(table, self._trig2, slave, interp=4, mul=self._amp2)
        # A Sig is the best way to properly handle "mul" and "add" arguments.        
        self._output = DCBlock(self._osc1 + self._osc2, mul, add)
        # Create the "_base_objs" attribute. This is the object's audio output.
        self._base_objs = self._output.getBaseObjects()

    def setTable(self, x):
        """
        Replace the `table` attribute.

        :Args:

            x: PyoTableObject
                New `table` attribute.

        """
        self._table = x
        self._osc1.table = x
        self._osc2.table = x

    def setMaster(self, x):
        """
        Replace the `master` attribute.

        :Args:

            x: float or PyoObject
                New `master` attribute.

        """
        self._master = x
        self._phase.freq = x

    def setSlave(self, x):
        """
        Replace the `slave` attribute.

        :Args:

            x: float or PyoObject
                New `slave` attribute.

        """
        self._slave = x
        self._osc1.freq = x
        self._osc2.freq = x

    def setXfade(self, x):
        """
        Replace the `xfade` attribute.

        :Args:

            x: float or PyoObject
                New `xfade` attribute.

        """
        self._xfade = x
        self._axfade.value = x

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
        self._map_list = [SLMap(20, 5000, "log", "master", self._master),
                          SLMap(20, 5000, "log", "slave", self._slave),
                          SLMap(0, 5, "lin", "xfade", self._xfade),
                          SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def table(self):
        """PyoTableObject. The table to use as the oscillator waveform.""" 
        return self._table
    @table.setter
    def table(self, x): self.setTable(x)

    @property
    def master(self):
        """float or PyoObject. Master frequency in cycles per second.""" 
        return self._master
    @master.setter
    def master(self, x): self.setMaster(x)

    @property
    def slave(self):
        """float or PyoObject. Slave frequency in cycles per second.""" 
        return self._slave
    @slave.setter
    def slave(self, x): self.setSlave(x)

    @property
    def xfade(self):
        """float or PyoObject. Crossfade time in milliseconds, between 0 and 5.""" 
        return self._xfade
    @xfade.setter
    def xfade(self, x): self.setXfade(x)

if __name__ == "__main__":
    # Test case...
    s = Server().boot()

    table = HarmTable([1, 0.5, 0.33, 0.25, 0.2, 0.167, 0.143, 0.125, 0.111, 0.1])
    master = Sig([80, 80], mul=Randi(min=0.99, max=1.01, freq=[1.3, 1.2]))
    slave = Sine([0.1, 0.15], mul=master, add=master*2)
    sosc = OscSync(table, master=master, slave=slave, xfade=0.5, mul=0.3).out()

    sc = Scope(sosc)

    s.gui(locals())
