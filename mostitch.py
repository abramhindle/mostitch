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
#import pylab
from marsyas import * 
import marsyas
import marsyas_util
import pdb
import pyflann
from pyflann import *
from numpy import *
#from numpy.random import *
import cPickle
import random
import argparse
import zmq


#PLOT = True
PLOT = False
#pyflann.set_distance_type('kl')

#pyflann.set_distance_type('manhattan')
#buffsize = 2048
#buffsize = 1024
#learning = False#True#False
#csound = False

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
flann = FLANN()
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
    def __init__(self, filename):
        self.filename_input = filename
        self.slices = []
        self.setup()

    def get_source(self):
        return "SoundFileSource/src"

    def post_network_setup( self ):
        self.input_net.updControl(
            "SoundFileSource/src/mrs_string/filename",
            self.filename_input)
        self.input_net.updControl("mrs_natural/inSamples", buffsize)

    def callback( self, input_net_end, stats):
	stats = [x for x in stats]
	rv = input_net_end.getSubVector(0,len(input_net_end))
        self.slices.append( Slice( rv, stats ) )

    def get_slices( self ):
        return self.slices

class StreamMetricExtractor(MetricExtractor):
    def __init__(self):
        self.slices = []
        self.setup()

    def get_source(self):
        return "AudioSource/src"

    def post_network_setup(self):
        self.input_net.updControl("mrs_natural/inSamples", buffsize)
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
    
def read_in_file_with_stats(filename_input):
    fm = FileMetricExtractor( filename_input )
    fm.readeverything()
    return fm.get_slices()

def make_output():
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


URL="tcp://127.0.0.1:11119"
ctx = zmq.Context(1)
socket = ctx.socket(zmq.REP)
socket.bind(URL)
poller = zmq.Poller()
poller.register(socket, zmq.POLLIN|zmq.POLLOUT)

def process_zmq():
    events = poller.poll(timeout=0)
    for x in events:
        if (zmq.POLLIN == x[1]):
            newstate = socket.recv_pyobj()
            for key in newstate:
                state[key] = newstate[key]
                warn("%s updated to %s" % (str(key), str(state[key])))
            socket.send_pyobj(state, flags=zmq.NOBLOCK)
                
def main():
    # read the slices    
    slices = []
    for filename_input in myfiles:
        warn("Opening "+filename_input)
        newslices = read_in_file_with_stats( filename_input ) 
        slices = slices + newslices
    # get NN
    dataset = array([s.stats for s in slices])
    window = make_window( window_name, buffsize)
    for slice in slices:
        slice.rv *= window
    params = flann.build_index(dataset, algorithm="kdtree", target_precision=0.9, log_level = "info")
    output_net = make_output()
    slicecnt = 0
    for slice in slices:
        load_slice( output_net, slicecnt, slice )
        slicecnt += 1
    sme = StreamMetricExtractor()
    init_audio_out( output_net )
    schedule_control = output_net.getControl(grainuri + "/mrs_realvec/schedule")
    schedsize = 3 # size of a schedule
    nn = schedsize
    while sme.has_data():
        # tick is done here
        new_slice = sme.operate()
        results, dists = flann.nn_index(array([new_slice.stats]),topn, checks=params["checks"]);
        result = results[0]
        if (state["learning"]):
            slices.append(new_slice)
            flann.add_points(array([new_slice.stats]))
            slicecnt = len(slices)
            load_slice( output_net, slicecnt, new_slice )
        # here's the granular part
        ngrains = random.randint(state["mingrains"],state["maxgrains"])
        schedule = marsyas.realvec(schedsize * ngrains)
        for j in range(0,ngrains):
            # in the next 10th of a second
            schedule[j*schedsize + 0] = random.randint(0,state["delay"])#44100/10)
            # beta is skewed, so it stays pretty low
            c = int((len(result)-1)*random.betavariate(1,3))
            choice = int(result[ c ]) 
            schedule[j*schedsize + 1] = choice # choose the slice
            amp = random.random() * state["amp"]
            depth = 512*(choice-1)/44100.0
            schedule[j*schedsize + 2] = amp
            dur = buffsize/44100.0
            when = (schedule[j*schedsize + 0])/44100.0
            if (csound):
                print "i1 %f %f %f %f %d"%(when,dur,amp,depth,choice)
        schedule_control = output_net.getControl(grainuri + "/mrs_realvec/schedule")
        schedule_control.setValue_realvec(schedule)
        output_net.updControl(grainuri + "/mrs_bool/schedcommit",
                              marsyas.MarControlPtr.from_bool(True))        
        output_net.tick()
	process_zmq()

main()

