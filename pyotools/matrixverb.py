#!/usr/bin/env python
# encoding: utf-8
from __future__ import division
from pyo import *
from math import sqrt, exp, e
from random import randint

def primes(mini=512, maxi=8192):
    """
    Prime number generator. Returns the list of primes
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
    l = len(values)
    step = l // num
    v = []
    for i in range(num):
        index = step*i
        if index < 0:
            index = 0
        elif index >= l:
            index = l - 1
        v.append(values[index])
    return v

def linmax(values, num):
    l = len(values)
    step = l // num
    last = l - 1
    v = []
    for i in range(num):
        index = last-step*i
        if index < 0:
            index = 0
        elif index >= l:
            index = l - 1
        v.append(values[index])
    return v

def expmin(values, num):
    l = len(values)
    v = []
    for i in range(num):
        index = int((exp(i / num) - 1.0) / (e - 1.0) * l)
        if index < 0:
            index = 0
        elif index >= l:
            index = l - 1
        v.append(values[index])
    return v

def expmax(values, num):
    l = len(values)
    last = l - 1
    v = []
    for i in range(num):
        index = last - int((exp(i / num) - 1.0) / (e - 1.0) * l)
        if index < 0:
            index = 0
        elif index >= l:
            index = l - 1
        v.append(values[index])
    return v

def powmin(values, num):
    l = len(values)
    v = []
    for i in range(num):
        index = int((pow(10.0, i / num) - 1.0) / 9.0 * l)
        if index < 0:
            index = 0
        elif index >= l:
            index = l - 1
        v.append(values[index])
    return v

def powmax(values, num):
    l = len(values)
    last = l - 1
    v = []
    for i in range(num):
        index = last - int((pow(10.0, i / num) - 1.0) / 9.0 * l)
        if index < 0:
            index = 0
        elif index >= l:
            index = l - 1
        v.append(values[index])
    return v
    
def sqrtmin(values, num):
    l = len(values)
    step = 1.0 / num
    v = []
    for i in range(num):
        index = int(sqrt(step*i) * l)
        if index < 0:
            index = 0
        elif index >= l:
            index = l - 1
        v.append(values[index])
    return v

def sqrtmax(values, num):
    l = len(values)
    step = 1.0 / num
    last = l - 1
    v = []
    for i in range(num):
        index = last - int(sqrt(step*i) * l)
        if index < 0:
            index = 0
        elif index >= l:
            index = l - 1
        v.append(values[index])
    return v

def rand(values, num):
    l = len(values)
    v = []
    for i in range(num):
        index = randint(0, l-1)
        v.append(values[index])
    return v
 
def get_spacing_algorithm(algoname):
    dict = {"linmin": linmin, "linmax": linmax, "expmin": expmin, "expmax": expmax, 
    "sqrtmin": sqrtmin, "sqrtmax": sqrtmax, "powmin": powmin, "powmax": powmax, "rand": rand} 
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
    def __init__(self, input, freq, damp, order):
        self._order = order
        if order < 4:
            self.lp = ButLP(input, freq)
            self.sig = Sig(self.lp - input, mul=damp, add=input)
        else:
            self.sig = input

    def setFreq(self, x):
        if self._order < 4:
            self.lp.freq = x
        
    def setDamp(self, x):
        if self._order < 4:
            self.sig.mul = x

class MatrixVerb(PyoObject):
    def __init__(self, input, liveness=0.7, depth=0.7, crossover=3500, highdamp=0.8, balance=0.25,
                numechoes=8, quality=3, echoesrange=[0.03, 0.1], echoesmode="linmax", 
                matrixrange=[0.05, 0.15], matrixmode="linmin", mul=1, add=0):
        PyoObject.__init__(self, mul, add)
        # attributes
        self._input = input
        self._liveness = liveness
        self._depth = depth
        self._crossover = crossover
        self._highdamp = highdamp
        self._balance = balance

        # get current sampling rate
        sampleRate = Sig(0).getSamplingRate()

        # normalization gain and number of delays for the rotation matrices
        if quality < 1: quality = 1
        elif quality > 4: quality = 4
        num_delays = 2 ** quality
        gain = -3.01 * quality

        # computes early reflections delay times
        er_primes = primes(int(echoesrange[0] * sampleRate), int(echoesrange[1] * sampleRate))
        samps = get_spacing_algorithm(echoesmode)(er_primes, numechoes)
        self._er_delays = [x / sampleRate for x in samps]

        # computes delay line lengths
        dl_primes = primes(int(matrixrange[0] * sampleRate), int(matrixrange[1] * sampleRate))
        samps = get_spacing_algorithm(matrixmode)(dl_primes, num_delays)
        self._delays = [x / sampleRate for x in samps]

        # feedback based on liveness parameter and number of stages
        self._feedback = Sig(liveness)
        self._clippedfeed = Clip(self._feedback, min=0, max=1, mul=pow(10, gain * 0.05))

        # input crossfader and pre lowpass filtering
        self._in_fader = InputFader(input)
        self._prefilter = Tone(Denorm(self._in_fader.mix(1)), freq=self._crossover)

        # early reflexions as a sequence of ERotate objects 
        self._earlyrefs = [ERotate(self._prefilter, Sig(0), self._er_delays.pop(0))]
        for t in self._er_delays:
            self._earlyrefs.append(ERotate(self._earlyrefs[-1].re, self._earlyrefs[-1].im, t))

        # first "buffersize" delay lines input signal (will be replaced by the matrices's outputs)  
        self._matrixin = [self._earlyrefs[-1].re, self._earlyrefs[-1].im]
        self._matrixin.extend([Sig(0) for i in range(num_delays-2)])

        # delay lines
        self._dlines = [SDelay(self._matrixin[i], delay=self._delays[i]) for i in range(num_delays)]
        # lowpass filters
        self._lopass = [LoP(self._dlines[i], self._crossover, self._highdamp, i) for i in range(num_delays)]
        # delay lines feedback + input 
        self._torotate = [self._lopass[i].sig * self._clippedfeed + self._matrixin[i] for i in range(num_delays)]

        # select and apply the rotation matrix
        self._matrix = {2: Rotate2, 4: Rotate4, 8: Rotate8, 16: Rotate16}[num_delays](self._torotate)

        # feed the delay lines with the output of the rotation matrix
        [self._dlines[i].setInput(self._matrix.sig[i]) for i in range(num_delays)]

        # balance between early reflections and reverberation tail, stereo mixing
        self._left = Interp(self._matrixin[0]*2+self._matrix.sig[-2]*0.1, self._matrixin[0]*0.5+self._matrix.sig[-2], self._depth)
        self._right = Interp(self._matrixin[1]*2+self._matrix.sig[-1]*0.1, self._matrixin[1]*0.5+self._matrix.sig[-1], self._depth)
        self._stereo = Mix([self._left, self._right], voices=2, mul=0.25)

        # balance between dry and wet signals and output audio streams
        self._out = Interp(self._in_fader.mix(2), self._stereo, self._balance)
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
        self._liveness = x
        self._feedback.value = x

    def setDepth(self, x):
        self._depth = x
        self._left.interp = x
        self._right.interp = x

    def setCrossover(self, x):
        self._crossover = x
        self._prefilter.freq = x
        [obj.setFreq(x) for obj in self._lopass]

    def setHighdamp(self, x):
        self._highdamp = x
        [obj.setDamp(x) for obj in self._lopass]

    def setBalance(self, x):
        self._balance = x
        self._out.interp = x

    def ctrl(self, map_list=None, title=None, wxnoserver=False):
        self._map_list = [SLMap(0, 1, "lin", "liveness", self._liveness),
                          SLMap(0, 1, "lin", "depth", self._depth),
                          SLMap(100, 15000, "log", "crossover", self._crossover),
                          SLMap(0, 1, "lin", "highdamp", self._highdamp),
                          SLMap(0, 1, "lin", "balance", self._balance),
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
        """float or PyoObject. Balance between early reflections and reverberation tail."""
        return self._depth
    @depth.setter
    def depth(self, x): 
        self.setDepth(x)

    @property
    def crossover(self): 
        """float or PyoObject. Lowpass cutoff frequency."""
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


if __name__ == "__main__":
    s = Server().boot()
    TEST = 0
    if TEST == 0:
        i3 = SfPlayer(SNDS_PATH+"/transparent.aif", loop=True, mul=0.5)
        a = MatrixVerb(i3, liveness=0.9, depth=0.7, crossover=3500, highdamp=0.7, balance=0.35,
                       numechoes=8, quality=4, echoesrange=[0.02, 0.06], echoesmode="expmin",
                       matrixrange=[0.04, 0.09], matrixmode="expmax").out()
        a.ctrl()
    elif TEST == 1: # Compare echoesmode and matrixmode
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

    s.gui(locals())
