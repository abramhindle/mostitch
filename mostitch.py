#!/usr/bin/env python
"""
Mostitch is Marsyas Ostitch. 

Ostitch was an audio collager. An audio collager takes input source
audio and produces output source audio which is composed of chunks of
the input. The output is usually is meant to mimic another signal
(like a song or speech).

   Originally from bextract.py
   Originally from in_out.py
   (C) 2013 Graham Percival
   a quick hack to demonstrate getting data between python and
   marsyas. 

Copyright (C) 2013 Abram Hindle, Marsyas authors for in_out.py

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import sys
import numpy
from marsyas import * 
import marsyas
import marsyas_util
import pdb
import pyflann
from pyflann import *
from numpy import *
import cPickle
import random
import argparse
import zmq

def parse_args():
    parser = argparse.ArgumentParser(description='Mostitch!')
    parser.add_argument('--buffsize', default=1024, help='Buffer Size')
    parser.add_argument('--csound', default=False, help='Print Csound Stuff')
    parser.add_argument('--distance', default='euclidean', help='What Distance type to use: euclidean kl manhattan minkowski hik hellinger cs')
    parser.add_argument('--learn', default=False, help='Turn Learning on or Off')
    parser.add_argument('--window', default="hann", help='Which window function to use: hann saw flat triangle')
    parser.add_argument('--mingrains', default=10, help='Minimum number of grains')
    parser.add_argument('--maxgrains', default=100, help='Maximum number of grains')
    parser.add_argument('--topn', default=20, help='Top N from NN')
    parser.add_argument('files', help='Filenames',nargs='+')
    args = parser.parse_args()
    buffsize = int(args.buffsize)
    csound = args.csound
    learning = args.learn
    myfiles = args.files
    pyflann.set_distance_type(args.distance)
    topn = int(args.topn)
    window_name = args.window
    maxgrains = int(args.maxgrains)
    mingrains = int(args.mingrains)
    state = {
	"maxgrains":maxgrains,
	"mingrains":mingrains,
	"amp":0.2,
	"topn":topn,
        "delay":3*buffsize,
        "learning":learning
        }
    settings = {
       "files":myfiles,
       "window_name":window_name,
       "csound":csound,
       "state":state,
       "buffsize":buffsize
       }
    return settings

def dfl_state():
    state = {
	"maxgrains":100,
	"mingrains":10,
	"amp":0.2,
	"topn":25,
        "delay":4096,
        "learning":False
        }
    return state

    
#texture = ["Rms/rms", "AubioYin/pitcher","ZeroCrossings/zcrs" ,"Series/lspbranch" ,"Series/lpccbranch" ,"MFCC/mfcc" ,"SCF/scf" ,"Rolloff/rf" ,"Flux/flux" ,"Centroid/cntrd" ,"Series/chromaPrSeries"]
# texture = ["Rms/rms", "AubioYin/pitcher","ZeroCrossings/zcrs" ,"Rolloff/rf" ,"Flux/flux" ,"Centroid/cntrd","AbsMax/abs","Energy/energy","MeanAbsoluteDeviation/mad","TimbreFeatures/featExtractor"]
#texture = ["TimbreFeatures/featExtractor"]


#"AimGammatone/aimgamma"]
# detectors = ["Fanout/detectors", texture]
detectors = ["TimbreFeatures/featExtractor","TextureStats/tStats"]

grainuri = "RealvecGrainSource/real_src"

def setup_timbre( net ):
    net.updControl("TimbreFeatures/featExtractor/mrs_string/enableTDChild",
        marsyas.MarControlPtr.from_string("ZeroCrossings/zcrs"))
    net.updControl("TimbreFeatures/featExtractor/mrs_string/enableLPCChild",
        marsyas.MarControlPtr.from_string("Series/lspbranch"))
    net.updControl("TimbreFeatures/featExtractor/mrs_string/enableLPCChild",
        marsyas.MarControlPtr.from_string("Series/lpccbranch"))
    net.updControl("TimbreFeatures/featExtractor/mrs_string/enableSPChild",
        marsyas.MarControlPtr.from_string("MFCC/mfcc"))
    net.updControl("TimbreFeatures/featExtractor/mrs_string/enableSPChild",
        marsyas.MarControlPtr.from_string("SCF/scf"))
    net.updControl("TimbreFeatures/featExtractor/mrs_string/enableSPChild",
        marsyas.MarControlPtr.from_string("Rolloff/rf"))
    net.updControl("TimbreFeatures/featExtractor/mrs_string/enableSPChild",
        marsyas.MarControlPtr.from_string("Flux/flux"))
    net.updControl("TimbreFeatures/featExtractor/mrs_string/enableSPChild",
        marsyas.MarControlPtr.from_string("Centroid/cntrd"))
    net.updControl("TimbreFeatures/featExtractor/mrs_string/enableSPChild",
        marsyas.MarControlPtr.from_string("Series/chromaPrSeries"))




class Slice:
    stats = []
    rv = 0
    def __init__(self, rv, stats):
        self.stats = stats
        self.rv = rv
    def stats(self):
        return self.stats
    def rv(self):
        return self.rv
    def str(self):
        return "Slice:"+",".join([str(x) for x in self.stats])
    
class MetricExtractor:
    # override this with your source
    def get_source(self):
        return "SoundFileSource/src"

    # override this with your filename setup
    def post_network_setup(self):
        return 0

    #override this
    def callback( self, input_net_end, stats):
        return 0

    def setup( self ):
        series = ["Series/input", [self.get_source()] + detectors]
        self.input_net = marsyas_util.create( series )
        setup_timbre( self.input_net )
        # override
        self.post_network_setup()
        self.notempty = self.input_net.getControl(self.get_source() + "/mrs_bool/hasData")
        self.input_net_end_control = self.input_net.getControl(self.get_source() + "/mrs_realvec/processedData")
        self.metrics_control = self.input_net.getControl("mrs_realvec/processedData")

    def has_data(self):
        return self.notempty.to_bool()

    def operate(self):
        self.input_net.tick()
        input_net_end = self.input_net_end_control.to_realvec()
        stats = self.metrics_control.to_realvec()
        return self.callback( input_net_end, stats )

    def readeverything(self):
        while self.has_data():
            self.operate()

class FileMetricExtractor(MetricExtractor):
    def __init__(self, filename,buffsize=1024):
        self.filename_input = filename
        self.slices = []
        self.buffsize = buffsize
        self.setup()        

    def get_source(self):
        return "SoundFileSource/src"

    def post_network_setup( self ):
        self.input_net.updControl(
            "SoundFileSource/src/mrs_string/filename",
            self.filename_input)
        self.input_net.updControl("mrs_natural/inSamples", self.buffsize)

    def callback( self, input_net_end, stats):
	stats = [x for x in stats]
	rv = input_net_end.getSubVector(0,len(input_net_end))
        self.slices.append( Slice( rv, stats ) )

    def get_slices( self ):
        return self.slices

class StreamMetricExtractor(MetricExtractor):
    def __init__(self,buffsize=1024):
        self.slices = []
        self.buffsize = buffsize
        self.setup()

    def get_source(self):
        return "AudioSource/src"

    def post_network_setup(self):
        self.input_net.updControl("mrs_natural/inSamples", self.buffsize)
        self.input_net.updControl("mrs_real/israte", 44100.0)
	self.input_net.updControl(self.get_source() + "/mrs_bool/initAudio", marsyas.MarControlPtr.from_bool(True));

    def callback( self, input_net_end, stats):
	stats = [x for x in stats]
	rv = input_net_end.getSubVector(0,len(input_net_end))
        s = Slice( rv, stats )
        #self.slices.append( s )
        return s
        
    #def get_slices( self ):
    #    return self.slices
    
def read_in_file_with_stats(filename_input, buffsize=1024):
    fm = FileMetricExtractor( filename_input, buffsize )
    fm.readeverything()
    return fm.get_slices()

def make_output(buffsize=1024):
    series = ["Series/output", 
              ["RealvecGrainSource/real_src",
               "AudioSink/dest"]]
    #           "SoundFileSink/dest"]]
    this_net = marsyas_util.create(series)
    this_net.updControl("mrs_natural/inSamples", buffsize)
    this_net.updControl("mrs_real/israte", 44100.0)
    #this_net.updControl(
    #    "SoundFileSink/dest/mrs_string/filename",
    #    "out.wav")
    #
    return this_net

def init_audio_out( this_net ):
    this_net.updControl("AudioSink/dest/mrs_bool/initAudio",marsyas.MarControlPtr.from_bool(True))

def play_slices(slices, output_net_begin_control, output_net):
    for play_slice in slices:
        output_net_begin_control.setValue_realvec(play_slice.rv)
        output_net.tick()

def load_slice( net, id, slice ):
    net.updControl(grainuri + "/mrs_natural/index", id)
    net.updControl(grainuri + "/mrs_natural/index", id)
    data_uri = grainuri + "/mrs_realvec/data"
    control = net.getControl(data_uri)
    control.setValue_realvec(slice.rv)
    net.updControl(grainuri + "/mrs_bool/commit",
                   marsyas.MarControlPtr.from_bool(True))

def hann( n, N ):
    return 0.5 * (1 - cos( (2 * math.pi * n) / (N - 1)))

def hann_window( size ):
    v = marsyas.realvec( size )
    for i in range(0,size):
        v[i] = hann( i, size)
    return v

def triangle( size ):
    v = marsyas.realvec( size )
    half = size/2
    for i in range(0,size):
        v[i] = 1.0 - abs(half - i)/half
    return v

def saw(size):
    v = marsyas.realvec( size )
    for i in range(0,size):
        v[i] = i/(size)
    return v

def flat(size):
    v = marsyas.realvec( size )
    for i in range(0,size):
        v[i] = 1
    return v

def make_window(name , size):
    name = name.lower()
    if (name == "triangle"):
        return triangle(size)
    elif (name == "saw"):
        return saw(size)
    elif (name=="hann" or name=="hanning"):
        return hann_window(size)
    else:
        return flat(size)

def printlist( l ):
    print ",".join([str(x) for x in l])

choices = {}
def chooser( results ):
    l = len(results)
    ramp = [1 - 1.0*i/l for i in (range(0,l))]
    printlist(ramp)
    framp = [1/(1.0+choices.get(int(x),0)) for x in results]
    printlist(framp)
    cramp = [ramp[i] * framp[i] for i in range(0,l)]
    printlist(cramp)
    cramp[int((l-1)*random.betavariate(1,3))] *= 100
    cramp[int((l-1)*random.betavariate(1,3))] *= 100
    cramp[int((l-1)*random.betavariate(1,3))] *= 100
    myi = cramp.index(max(cramp))
    choice = int(results[myi])
    choices[choice] = choices.get(choice,0) + 1
    print "Choice:%d Myi:%d" % (choice, myi)
    return choice

def warn(mystr):
    print >> sys.stderr, mystr

class ZMQCommunicator:
    def __init__(self, URL="tcp://127.0.0.1:11119", ctx=None):
        if (ctx == None):
            ctx = zmq.Context(1)
        socket = ctx.socket(zmq.REP)
        self.socket = socket
        socket.bind(URL)
        poller = zmq.Poller()
        self.poller = poller 
        poller.register(self.socket, zmq.POLLIN)#|zmq.POLLOUT)
        
    # mutates state
    def process_zmq(self, state):        
        print "Process_zmq"
        print str(state)
        events = self.poller.poll(timeout=0)
        socket = self.socket
        for x in events:
            print str(x)
            if (zmq.POLLIN == x[1]):
                newstate = socket.recv_pyobj()
                for key in newstate:
                    state[key] = newstate[key]
                    warn("%s updated to %s" % (str(key), str(state[key])))
                socket.send_pyobj(state)#, flags=zmq.NOBLOCK)
            elif (zmq.POLLOUT == x[1]):
                warn("Why did we get a POLLOUT?")
                #self.socket.send_pyobj(state, flags=zmq.NOBLOCK)
                    

    
schedsize = 3

class Delayer:
    def delay(self, max_delay):
        return random.randint(0,max_delay)    

class Chooser:
    # choose returns an int, which is a slice ID from a list of results
    def choose(self, result):
        return int(result[0])

class BetaChooser:
    def choose(self, result):
        c = int((len(result)-1)*random.betavariate(1,3))
        choice = int(result[ c ]) 
        return choice

class Mostitch:
    def __init__(self, buffsize = 1024, state = {}):
        self.buffsize = buffsize
        self.slices = []
        self.window = None
        self.params = None
        self.state = state
        self.flann = FLANN()
        # state pattern
        self.set_chooser( BetaChooser() )
        self.set_delayer( Delayer() )
        self.zmq = ZMQCommunicator()

    def set_chooser(self, chooser ):
        self.chooser = chooser

    def set_delayer(self, delayer ):
        self.delayer = delayer

    def load_file(self, filename_input ):
        warn("Opening "+filename_input)
        newslices = read_in_file_with_stats( filename_input, self.buffsize ) 
        self.slices += newslices
        self.slicecnt = len(self.slices)
        
    def load_files(self, filenames ):
        for filename_input in filenames:
            self.load_file(filename_input)

    def set_window( self, window_name ):
        self.window = make_window( window_name, self.buffsize )
        
    def apply_window_to_slice(self, slice, window):
        slice.rv *= window

    def apply_window_to_slices( self ):
        if (self.window != None):
            for slice in self.slices:
                self.apply_window_to_slice( slice, self.window )
    
    def train_on_slices( self ):
        dataset = array([s.stats for s in self.slices])
        params = self.flann.build_index(dataset, algorithm="kdtree", target_precision=0.9, log_level = "info")
        self.params = params
    
    def init_output_network(self):
        output_net = make_output(self.buffsize)
        slicecnt = 0
        for slice in self.slices:
            load_slice( output_net, slicecnt, slice )
            slicecnt += 1
        self.schedule_control = output_net.getControl(grainuri + "/mrs_realvec/schedule")
        self.output_net = output_net
        
    def init_input_network(self):
        self.sme = StreamMetricExtractor()

    def init_audio(self):
        init_audio_out( self.output_net )
        
    def has_input(self):
        return self.sme.has_data()

    def learn(self, slice):
        self.slices.append(new_slice)
        self.flann.add_points(array([new_slice.stats]))
        self.slicecnt = len(slices)
        load_slice( output_net, slicecnt, new_slice )

    def cond_learn(self, slice):
        if (self.state["learning"]):
            self.learn( slice )

    # state pattern
    def choose( self, result ):
        return self.chooser.choose(result)

    # state pattern
    def generate_delay( self ):
        return self.delayer.delay(self.state["delay"])


    def post_schedule_grain(self, delay, choice, amp ):
        return None

    def process_zmq(self):
        self.zmq.process_zmq(self.state)

    # override to change how the number of ngrains are chosen
    def generate_ngrains(self):
        state = self.state
        ngrains = random.randint(
            min(state["mingrains"],state["maxgrains"]),
            max(state["mingrains"],state["maxgrains"]))
        return ngrains
        
    # override to change how the amplitude of a grain is chosen
    def generate_amp(self):
        amp = random.random() * self.state["amp"]
        return amp

    def step(self):
        state = self.state
        new_slice = self.sme.operate()
        results, dists = self.flann.nn_index(array([new_slice.stats]),state["topn"], checks=self.params["checks"]);
        result = results[0]
        self.cond_learn( new_slice )
        # here's the granular part
        ngrains = self.generate_ngrains()
        # this is a bad smell, we could make this an object!
        schedule = marsyas.realvec(schedsize * ngrains)        
        for j in range(0,ngrains):
            # in the next ___ of a second
            delay = self.generate_delay()
            schedule[j*schedsize + 0] = self.generate_delay()
            choice = self.choose( result )
            schedule[j*schedsize + 1] = choice # choose the slice
            amp = self.generate_amp()
            schedule[j*schedsize + 2] = amp
            self.post_schedule_grain( delay, choice, amp )
        schedule_control = self.output_net.getControl(grainuri + "/mrs_realvec/schedule")
        schedule_control.setValue_realvec(schedule)
        self.output_net.updControl(grainuri + "/mrs_bool/schedcommit",
                              marsyas.MarControlPtr.from_bool(True))        
        self.output_net.tick()
	self.process_zmq()


    # run this if you are lazy
    def mostitch_main(self, myfiles, window_name ="hann"):
        mostitch = self
        mostitch.load_files( myfiles )
        mostitch.set_window( window_name )
        mostitch.apply_window_to_slices()
        mostitch.train_on_slices()
        mostitch.init_output_network()
        mostitch.init_input_network()
        mostitch.init_audio()
        while (mostitch.has_input()):
            mostitch.step()
            

class CsoundMostich(Mostitch):
    def post_schedule_grain(self, delay, choice, amp ):
        depth = 512*(choice-1)/44100.0
        schedule[j*schedsize + 2] = amp
        dur = self.buffsize/44100.0
        when = (schedule[j*schedsize + 0])/44100.0
        print "i1 %f %f %f %f %d"%(when,dur,amp,depth,choice)

def zmq_test():
    zmq = ZMQCommunicator()
    state = dfl_state()    
    while 1:
        zmq.process_zmq(state)

def main():
    settings = parse_args()
    mostitch = None
    if (settings["csound"]):
        mostitch = CsoundMostitch( settings["buffsize"], settings["state"] )
    else:
        mostitch = Mostitch( settings["buffsize"], settings["state"] )
    mostitch.mostitch_main( settings["files"], settings["window_name"] )

if __name__ == "__main__":
    main()
