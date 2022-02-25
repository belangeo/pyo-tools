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

from __future__ import division
from pyo import *
from math import sqrt, exp, e
from random import sample

def clipint(value, maxi):
    """Clip an integer value between 0 and maxi (maxi not included)."""
    if value < 0:
        value = 0
    elif value >= maxi:
        value = maxi - 1
    return value

def primes(mini=512, maxi=8192):
    """
    Prime number generator. Returns the list of prime numbers
    between `mini` and `maxi`.
    """
    ps, pp = [2, 3], 3
    while pp < maxi:
        pp += 2
        test = True
        sqrtpp = sqrt(pp)
        for a in ps:
            if a > sqrtpp: 
                break
            if pp % a == 0:
                test = False
                break
        if test: 
            ps.append(pp)
    return [x for x in ps if x > mini]

def linmin(values, num):
    """
    Return a list of `num` linearly distributed numbers from the
    list `values`, starting at the lowest one.
    """
    l = len(values)
    step = l // num
    v = []
    for i in range(num):
        index = clipint(step * i, l)
        v.append(values[index])
    return v

def linmax(values, num):
    """
    Return a list of `num` linearly distributed numbers from the
    list `values`, starting at the highest one.
    """
    l = len(values)
    step = l // num
    last = l - 1
    v = []
    for i in range(num):
        index = clipint(last - step * i, l)
        v.append(values[index])
    return v

def expmin(values, num):
    """
    Return a list of `num` exponentially distributed numbers from the
    list `values`, starting at the lowest one. The base is the constant `e`.
    """
    l = len(values)
    v = []
    for i in range(num):
        index = int((exp(i / num) - 1.0) / (e - 1.0) * l)
        index = clipint(index, l)
        v.append(values[index])
    return v

def expmax(values, num):
    """
    Return a list of `num` exponentially distributed numbers from the
    list `values`, starting at the highest one. The base is the constant `e`.
    """
    l = len(values)
    last = l - 1
    v = []
    for i in range(num):
        index = last - int((exp(i / num) - 1.0) / (e - 1.0) * l)
        index = clipint(index, l)
        v.append(values[index])
    return v

def powmin(values, num):
    """
    Return a list of `num` exponentially distributed numbers from the
    list `values`, starting at the lowest one. The base is 10.
    """
    l = len(values)
    v = []
    for i in range(num):
        index = int((pow(10.0, i / num) - 1.0) / 9.0 * l)
        index = clipint(index, l)
        v.append(values[index])
    return v

def powmax(values, num):
    """
    Return a list of `num` exponentially distributed numbers from the
    list `values`, starting at the highest one. The base is 10.
    """
    l = len(values)
    last = l - 1
    v = []
    for i in range(num):
        index = last - int((pow(10.0, i / num) - 1.0) / 9.0 * l)
        index = clipint(index, l)
        v.append(values[index])
    return v
    
def sqrtmin(values, num):
    """
    Return a list of `num` logarithmically distributed numbers from the
    list `values`, starting at the lowest one. This algorithm takes the
    square-root of the index, normalized between 0 and 1.
    """
    l = len(values)
    step = 1.0 / num
    v = []
    for i in range(num):
        index = int(sqrt(step*i) * l)
        index = clipint(index, l)
        v.append(values[index])
    return v

def sqrtmax(values, num):
    """
    Return a list of `num` logarithmically distributed numbers from the
    list `values`, starting at the highest one. This algorithm takes the
    square-root of the index, normalized between 0 and 1.
    """
    l = len(values)
    step = 1.0 / num
    last = l - 1
    v = []
    for i in range(num):
        index = last - int(sqrt(step*i) * l)
        index = clipint(index, l)
        v.append(values[index])
    return v

def rand(values, num):
    """
    Return a list of `num` randomly distributed numbers from the list `values`.
    """
    return sample(values, num)
 
def get_spacing_algorithm(algoname):
    """
    Return a reference to a generation function from its name as a string.
    """
    dict = {"linmin": linmin, "linmax": linmax, "expmin": expmin,
            "expmax": expmax, "sqrtmin": sqrtmin, "sqrtmax": sqrtmax,
            "powmin": powmin, "powmax": powmax, "rand": rand} 
    if algoname in dict.keys():
        return dict[algoname]
    else:
        return dict["linmin"]

class ERotate:
    """
    Rotation matrix with delayed imaginary part. Used for early reflections.
    """
    def __init__(self, in1, in2, delay=0):
        self.in1, self.in2 = in1, in2
        self.re = (self.in1 + self.in2) * 0.7071
        self.im = SDelay(self.in1-self.in2, delay=delay, mul=0.7071)
    
    def setDelay(self, x):
        self.im.delay = x

class Rotate2:
    """
    Rotation matrix (without gain compensation, which is included 
    in feedback calculation) for a two-signals input.
    """
    def __init__(self, input):
        self.sig = [input[0] + input[1], input[0] - input[1]]

class Rotate4:
    """
    Rotation matrix (without gain compensation, which is included 
    in feedback calculation) for a four-signals input.
    """
    def __init__(self, input):
        self.h1, self.h2 = Rotate2(input[:2]), Rotate2(input[2:])
        self.r1, self.i1 = self.h1.sig[0] + self.h2.sig[0], self.h1.sig[0] - self.h2.sig[0]
        self.r2, self.i2 = self.h1.sig[1] + self.h2.sig[1], self.h1.sig[1] - self.h2.sig[1]
        self.sig = [self.r1, self.r2, self.i1, self.i2]

class Rotate8:
    """
    Rotation matrix (without gain compensation, which is included 
    in feedback calculation) for a eight-signals input.
    """
    def __init__(self, input):
        self.h1, self.h2 = Rotate4(input[:4]), Rotate4(input[4:])
        self.r1, self.i1 = self.h1.sig[0] + self.h2.sig[0], self.h1.sig[0] - self.h2.sig[0]
        self.r2, self.i2 = self.h1.sig[1] + self.h2.sig[1], self.h1.sig[1] - self.h2.sig[1]
        self.r3, self.i3 = self.h1.sig[2] + self.h2.sig[2], self.h1.sig[2] - self.h2.sig[2]
        self.r4, self.i4 = self.h1.sig[3] + self.h2.sig[3], self.h1.sig[3] - self.h2.sig[3]
        self.sig = [self.r1, self.r2, self.r3, self.r4, self.i1, self.i2, self.i3, self.i4]

class Rotate16:
    """
    Rotation matrix (without gain compensation, which is included 
    in feedback calculation) for a sixteen-signals input.
    """
    def __init__(self, input):
        self.h1, self.h2 = Rotate8(input[:8]), Rotate8(input[8:])
        self.r1, self.i1 = self.h1.sig[0] + self.h2.sig[0], self.h1.sig[0] - self.h2.sig[0]
        self.r2, self.i2 = self.h1.sig[1] + self.h2.sig[1], self.h1.sig[1] - self.h2.sig[1]
        self.r3, self.i3 = self.h1.sig[2] + self.h2.sig[2], self.h1.sig[2] - self.h2.sig[2]
        self.r4, self.i4 = self.h1.sig[3] + self.h2.sig[3], self.h1.sig[3] - self.h2.sig[3]
        self.r5, self.i5 = self.h1.sig[4] + self.h2.sig[4], self.h1.sig[4] - self.h2.sig[4]
        self.r6, self.i6 = self.h1.sig[5] + self.h2.sig[5], self.h1.sig[5] - self.h2.sig[5]
        self.r7, self.i7 = self.h1.sig[6] + self.h2.sig[6], self.h1.sig[6] - self.h2.sig[6]
        self.r8, self.i8 = self.h1.sig[7] + self.h2.sig[7], self.h1.sig[7] - self.h2.sig[7]
        self.sig = [self.r1, self.r2, self.r3, self.r4, self.r5, self.r6, self.r7, self.r8,
                    self.i1, self.i2, self.i3, self.i4, self.i5, self.i6, self.i7, self.i8]
        
class LoP:
    """
    Lowpass filter with distinct cutoff frequency and damping factor. 
    Only the first four inputs are filtered, all others are unfiltered.
    """
    def __init__(self, input, freq, damp, which, order=2):
        self._which = which
        if order not in [1, 2, 4]:
            order = 2
        if which < 4:
            self.lp = {1: Tone, 2: ButLP, 4: MoogLP}[order](input, freq)
            self.sig = Sig(self.lp - input, mul=damp, add=input)
        else:
            self.sig = input

    def setFreq(self, x):
        if self._which < 4:
            self.lp.freq = x
        
    def setDamp(self, x):
        if self._which < 4:
            self.sig.mul = x

class MatrixVerb(PyoObject):
    """
    Delay-line rotating-matrix reverb inspired by Miller Puckette's rev3~ object.

    This reverb uses a delay line network with a rotating matrix to create a
    dense reverberation tail. Time range for early reflexions and reverberation
    delays can be specified as well as the kind of algorithm to use to distribute
    values inside the given ranges. This leaves room for lot of explorations. 
    This object is a kind of reverberator laboratory, play with the many
    arguments to hear the different reverb colors you can create with it! 

    :Parent: :py:class:`PyoObject`

    :Args:

        input: PyoObject
            The audio signal to reverberate. This signal will mixed to one
            channel before being fed to the reverb and mixed to two channels
            before the dry/wet balance to give a stereo output.
        liveness: float or PyoObject, optional
            Internal feedback value of the delay network, between 0 and 1.
            A value of 1 produces an infinite reverb. Defaults to 0.7.
        depth: float or PyoObject, optional
            Balance, in the range 0 to 1, between early reflexions and reverb
            tail. Values around 0.4 give small rooms while higher values give
            larger rooms. Defaults to 0.7.
        crossover: float or PyoObject, optional
            Crossover frequency in Hz. Frequencies above the crossover will be
            attenuated according to the `highdamp` argument. Defaults to 3500.
        highdamp: float or PyoObject, optional
            High frequencies damping factor between 0 and 1. A value of 0 means
            equal reverb time at all frequencies and a value of 1 means almost
            nothing above the crossover frequency gets through. Defaults to 0.75.
        balance: float or PyoObject, optional
            Balance, in the range 0 to 1, between the dry (input) and the wet
            (reverberated) signals. Defaults to 0.25.
        moddepth: float or PyoObject, optional
            Depth of the modulators applied to the matrix delays. Defaults to 0.03.
        modspeed: float or PyoObject, optional
            Speed of the modulators, in Hz, applied to the matrix delays. Defaults to 1.
        numechoes: int, optional
            The number of early reflexions. Available at initialization time
            only. Defaults to 8.
        quality: int {1, 2, 3, 4}, optional
            Defines the reverb tail density. The rotating matrix will contain
            `2 ** quality` delay lines. The higher the better reverb quality
            (and also more expensive). Available at initialization time only.
            Defaults to 4.
        filtorder: int {1, 2, 4}, optional
            The order of the IIR lowpass filter used in the feedback network. 
            It can be 1 for a 6dB/oct (Tone), 2 for a 12db/oct (ButLP) or 4
            for a 24dB/oct (MoogLP). Available at initialization time only.
            Defaults to 2.
        echoesrange: list of two floats, optional
            The minimum and maximum delay times, in seconds, used to compute
            the early reflexions. Available at initialization time only.
            Defaults to [0.03, 0.08].
        echoesmode: string, optional
            The distribution algorithm used to compute the early reflexions
            delay times. The algorithm choose the delay times in a list of
            prime numbers generated according to the `echoesrange` values.
            Available at initialization time only. Possible choices are:
            "linmin", "linmax", "expmin", "expmax", "sqrtmin", "sqrtmax",
            "powmin", "powmax" and "rand". Defaults to "linmin".
        matrixrange: list of two floats, optional
            The minimum and maximum delay times, in seconds, used to compute
            the reverberation tail. Available at initialization time only.
            Defaults to [0.05, 0.15].
        matrixmode: string, optional
            The distribution algorithm used to compute the reverberation tail
            delay times. The algorithm choose the delay times in a list of
            prime numbers generated according to the `matrixrange` values.
            Available at initialization time only. Possible choices are:
            "linmin", "linmax", "expmin", "expmax", "sqrtmin", "sqrtmax",
            "powmin", "powmax" and "rand". Defaults to "linmin".

    >>> s = Server().boot()
    >>> s.start()
    >>> from pyotools import *
    >>> t = SndTable(SNDS_PATH + '/transparent.aif')
    >>> src = Looper(t, dur=t.getDur()+2, xfade=0)
    >>> rev = MatrixVerb(src, liveness=0.85, balance=0.4).out()

    """ 
    def __init__(self, input, liveness=0.7, depth=0.7, crossover=3500,
                 highdamp=0.75, balance=0.25, moddepth=0.03, modspeed=1,
                 numechoes=8, quality=4, filtorder=2, echoesrange=[0.03, 0.08],
                 echoesmode="linmin", matrixrange=[0.05, 0.15],
                 matrixmode="linmin", mul=1, add=0):
        PyoObject.__init__(self, mul, add)

        # Raw arguments so that we can retrieve them with the attribute syntax.
        self._input = input
        self._liveness = liveness   # reverb time.
        self._depth = depth         # balance early reflexions / reverb tail.
        self._crossover = crossover # lowpass cutoff frequency.
        self._highdamp = highdamp   # high frequencies damping.
        self._balance = balance     # balance dry / wet.
        self._moddepth = moddepth   # delay line modulation depth
        self._modspeed = modspeed   # delay line modulation speed

        # Get current sampling rate.
        sampleRate = Sig(0).getSamplingRate()

        # Normalization gain and number of delays for the rotating matrix.
        if quality < 1: quality = 1
        elif quality > 4: quality = 4
        num_delays = 2 ** quality
        # Compensation for the 4-order lowpass filter at high cutoff frequency.
        if filtorder == 4:
            gain = pow(10, -4.01 * quality * 0.05)
        else:
            gain = pow(10, -3.01 * quality * 0.05)

        # Computes early reflections delay times (ensure there is enough
        # prime numbers to satisfy numechoes).
        er_primes = primes(int(echoesrange[0] * sampleRate),
                           int(echoesrange[1] * sampleRate))
        extend = 0.005
        while len(er_primes) < numechoes:
            er_primes = primes(int(echoesrange[0] * sampleRate),
                               int((echoesrange[1] + extend) * sampleRate))
            extend += 0.005
        samps = get_spacing_algorithm(echoesmode)(er_primes, numechoes)
        self._er_delays = [x / sampleRate for x in samps]

        # Computes delay line lengths (ensure there is enough prime numbers
        # to satisfy num_delays).
        dl_primes = primes(int(matrixrange[0] * sampleRate),
                           int(matrixrange[1] * sampleRate))
        extend = 0.005
        while len(dl_primes) < num_delays:
            dl_primes = primes(int(matrixrange[0] * sampleRate),
                               int((matrixrange[1] + extend) * sampleRate))
            extend += 0.005
        samps = get_spacing_algorithm(matrixmode)(dl_primes, num_delays)
        self._delays = [x / sampleRate for x in samps]

        # Feedback based on liveness parameter and number of stages.
        self._feedback = Sig(liveness)
        self._clippedfeed = Clip(self._feedback, min=0, max=1, mul=gain)

        # Input crossfader and pre-lowpass filtering.
        self._in_fader = InputFader(input)
        self._prefilter = Tone(Denorm(self._in_fader.mix(1)), self._crossover)

        # Early reflexions as a sequence of ERotate objects. 
        self._earlyrefs = [ERotate(self._prefilter, Sig(0), self._er_delays.pop(0))]
        for t in self._er_delays:
            self._earlyrefs.append(ERotate(self._earlyrefs[-1].re, self._earlyrefs[-1].im, t))

        # First "buffersize" delay lines input signal (will be replaced by the matrix outputs).  
        self._matrixin = [self._earlyrefs[-1].re, self._earlyrefs[-1].im]
        self._matrixin.extend([Sig(0) for i in range(num_delays-2)])

        # Reverberation tail delay line modulators.
        self._modulators_speed = Sig(self._modspeed)
        self._modulators = [Randi(1 - self._moddepth, 1 + self._moddepth, freq=self._modulators_speed*random.uniform(0.5, 2)) for i in range(num_delays)]
        # Reverberation tail delay lines.
        self._dlines = [SDelay(self._matrixin[i], delay=self._delays[i] * self._modulators[i]) for i in range(num_delays)]
        # Lowpass filtering.
        self._lopass = [LoP(self._dlines[i], self._crossover, self._highdamp, i, filtorder) for i in range(num_delays)]
        # Delay lines feedback + input. 
        self._torotate = [self._lopass[i].sig * self._clippedfeed + self._matrixin[i] for i in range(num_delays)]

        # Select and apply the rotating matrix.
        self._matrix = {2: Rotate2, 4: Rotate4, 8: Rotate8, 16: Rotate16}[num_delays](self._torotate)

        # Feed the delay lines with the output of the rotation matrix.
        [self._dlines[i].setInput(self._matrix.sig[i]) for i in range(num_delays)]

        # Early reflections / reverberation tail balance and stereo mixing.
        self._left = Interp(self._matrixin[0] * 2 + self._matrix.sig[-2] * 0.1,
                            self._matrixin[0] * 0.5 + self._matrix.sig[-2], self._depth)
        self._right = Interp(self._matrixin[1] * 2 + self._matrix.sig[-1] * 0.1,
                             self._matrixin[1] * 0.5 + self._matrix.sig[-1], self._depth)
        self._stereo = Mix([self._left, self._right], voices=2, mul=0.25)

        # Dry / wet balance and output audio streams.
        self._out = Interp(self._in_fader.mix(2), self._stereo, self._balance)
        # Create the "_base_objs" attribute. This is the object's audio output.
        self._base_objs = self._out.getBaseObjects()

    def setInput(self, x, fadetime=0.05):
        """
        Replace the `input` attribute.

        :Args:

            x : PyoObject
                New signal to process.
            fadetime : float, optional
                Crossfade time between old and new input. Defaults to 0.05.

        """
        self._input = x
        self._in_fader.setInput(x, fadetime)

    def setLiveness(self, x):
        """
        Replace the `liveness` attribute.

        :Args:

            x: float or PyoObject
                New `liveness` attribute.

        """
        self._liveness = x
        self._feedback.value = x

    def setDepth(self, x):
        """
        Replace the `depth` attribute.

        :Args:

            x: float or PyoObject
                New `depth` attribute.

        """
        self._depth = x
        self._left.interp = x
        self._right.interp = x

    def setCrossover(self, x):
        """
        Replace the `crossover` attribute.

        :Args:

            x: float or PyoObject
                New `crossover` attribute.

        """
        self._crossover = x
        self._prefilter.freq = x
        [obj.setFreq(x) for obj in self._lopass]

    def setHighdamp(self, x):
        """
        Replace the `highdamp` attribute.

        :Args:

            x: float or PyoObject
                New `highdamp` attribute.

        """
        self._highdamp = x
        [obj.setDamp(x) for obj in self._lopass]

    def setBalance(self, x):
        """
        Replace the `balance` attribute.

        :Args:

            x: float or PyoObject
                New `balance` attribute.

        """
        self._balance = x
        self._out.interp = x

    def setModdepth(self, x):
        """
        Replace the `moddepth` attribute.

        :Args:

            x: float or PyoObject
                New `moddepth` attribute.

        """
        self._moddepth = x
        [obj.setMin(1 - x) for obj in self._modulators]
        [obj.setMax(1 + x) for obj in self._modulators]

    def setModspeed(self, x):
        """
        Replace the `modspeed` attribute.

        :Args:

            x: float or PyoObject
                New `modspeed` attribute.

        """
        self._modspeed = x
        [obj.setFreq(x * random.uniform(0.5, 2)) for obj in self._modulators]

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0, 1, "lin", "liveness", self._liveness),
                          SLMap(0, 1, "lin", "depth", self._depth),
                          SLMap(100, 15000, "log", "crossover", self._crossover),
                          SLMap(0, 1, "lin", "highdamp", self._highdamp),
                          SLMap(0, 1, "lin", "balance", self._balance),
                          SLMap(0.001, 0.95, "log", "moddepth", self._moddepth),
                          SLMap(0.1, 5, "log", "modspeed", self._modspeed),
                          SLMapMul(self._mul)]
        PyoObject.ctrl(self, map_list, title, wxnoserver)

    @property
    def input(self): 
        """PyoObject. Input signal to process."""
        return self._input
    @input.setter
    def input(self, x): 
        self.setInput(x)

    @property
    def liveness(self): 
        """float or PyoObject. Delay lines feedback, Acts on the reverb time."""
        return self._liveness
    @liveness.setter
    def liveness(self, x): 
        self.setLiveness(x)

    @property
    def depth(self): 
        """float or PyoObject. Early refs / reverberation tail balance."""
        return self._depth
    @depth.setter
    def depth(self, x): 
        self.setDepth(x)

    @property
    def crossover(self): 
        """float or PyoObject. Crossover frequency in Hz."""
        return self._crossover
    @crossover.setter
    def crossover(self, x): 
        self.setCrossover(x)

    @property
    def highdamp(self): 
        """float or PyoObject. High frequencies damping."""
        return self._highdamp
    @highdamp.setter
    def highdamp(self, x): 
        self.setHighdamp(x)

    @property
    def balance(self): 
        """float or PyoObject. Dry / Wet balance."""
        return self._balance
    @balance.setter
    def balance(self, x): 
        self.setBalance(x)

    @property
    def moddepth(self):
        """float or PyoObject. Average modulation depth."""
        return self._moddepth
    @moddepth.setter
    def moddepth(self, x):
        self.setModdepth(x)

    @property
    def modspeed(self):
        """float or PyoObject. Average modulation speed."""
        return self._modspeed
    @modspeed.setter
    def modspeed(self, x):
        self.setModspeed(x)


if __name__ == "__main__":
    s = Server().boot()

    f = Fader(fadein=0.1).play()
    t = SndTable(SNDS_PATH + "/transparent.aif")
    src = Looper(t, pitch=1, start=0, dur=t.getDur()+2, xfade=0, mode=1, mul=f)

    TEST = 0
    if TEST == 0: # Compare echoesmode and matrixmode
        m = Metro(1).play()
        i3 = TrigEnv(m, table=SndTable(SNDS_PATH+"/transparent.aif", stop=0.05), dur=0.05)
        a = MatrixVerb(i3, liveness=0.9, depth=0.7, crossover=3500, highdamp=0.7, balance=1,
                       numechoes=8, quality=4, echoesrange=[0.02, 0.06], echoesmode="expmin",
                       matrixrange=[0.04, 0.09], matrixmode="expmax")
        b = MatrixVerb(i3, liveness=0.9, depth=0.7, crossover=3500, highdamp=0.7, balance=1,
                       numechoes=16, quality=4, echoesrange=[0.02, 0.1], echoesmode="linmin",
                       matrixrange=[0.04, 0.14], matrixmode="linmax")
        c = MatrixVerb(i3, liveness=0.9, depth=0.7, crossover=3500, highdamp=0.7, balance=1,
                       numechoes=8, quality=4, echoesrange=[0.02, 0.06], echoesmode="rand",
                       matrixrange=[0.04, 0.09], matrixmode="rand")
        d = Selector([a,b,c]).out()
        d.ctrl()
    elif TEST == 1: # controls
        rev = MatrixVerb(src, liveness=0.9, depth=0.7, crossover=3500, highdamp=0.7,
                         balance=0.35, numechoes=8, quality=4, filtorder=4, 
                         echoesrange=[0.02, 0.06], echoesmode="expmin",
                         matrixrange=[0.04, 0.09], matrixmode="expmax").out()
        rev.ctrl()
    elif TEST == 2: # small box
        rev = MatrixVerb(src, liveness=0.65, depth=0.4, crossover=3500, highdamp=0.9,
                         balance=0.5, numechoes=8, quality=4, echoesrange=[0.005, 0.006],
                         echoesmode="rand", matrixrange=[0.025, 0.0251], matrixmode="rand",
                         mul=f).out()
    elif TEST == 3: # large hall
        rev = MatrixVerb(src, liveness=0.85, depth=0.7, crossover=3500, highdamp=0.8,
                         balance=0.4, numechoes=12, filtorder=2, quality=4,
                         echoesrange=[0.025, 0.06], echoesmode="linmin",
                         matrixrange=[0.05, 0.12], matrixmode="linmax").out()

    s.gui(locals())
