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

#PLOT = True
PLOT = False
#pyflann.set_distance_type('kl')
pyflann.set_distance_type('euclidean')
#pyflann.set_distance_type('manhattan')
flann = FLANN()
topn = 20
#buffsize = 2048
#buffsize = 1024
#learning = False#True#False
#csound = False

parser = argparse.ArgumentParser(description='Mostitch!')
parser.add_argument('--buffsize', default=1024, help='Buffer Size')
parser.add_argument('--csound', default=False, help='Print Csound Stuff')
parser.add_argument('--learn', default=False, help='Turn Learning on or Off')
parser.add_argument('file', help='Filename')
args = parser.parse_args()
buffsize = int(args.buffsize)
csound = args.csound
learning = args.learn
myfilename = args.file

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


def main():
    try:    
        filename_input = myfilename
    except:
        print "USAGE: ./mostitch.py input_filename.wav"
        exit(1)
    # read the slices    
    slices = read_in_file_with_stats( filename_input )
    #    print(len(slices))
    # get NN
    dataset = array([s.stats for s in slices])
    #window = triangle(buffsize)
    window = hann_window(buffsize)
    #window = flat(buffsize)
    #flat(buffsize)#saw(buffsize)#triangle(buffsize) #flat(buffsize) #triangle(buffsize)
    for slice in slices:
        slice.rv *= window
    #print ",".join([str(x) for x in slices[1000].rv])
    #params = flann.build_index(dataset, algorithm="autotuned", target_precision=0.9, log_level = "info")
    params = flann.build_index(dataset, algorithm="kdtree", target_precision=0.9, log_level = "info")
    output_net = make_output()
    slicecnt = 0
    for slice in slices:
        load_slice( output_net, slicecnt, slice )
        slicecnt += 1

    sme = StreamMetricExtractor()
    init_audio_out( output_net )
    schedule_control = output_net.getControl(
        grainuri + "/mrs_realvec/schedule")
    schedsize = 3 # size of a schedule
    nn = schedsize
    while sme.has_data():
        # tick is done here
        new_slice = sme.operate()
        results, dists = flann.nn_index(array([new_slice.stats]),topn, checks=params["checks"]);
        result = results[0]
        if (learning):
            slices.append(new_slice)
            flann.add_points(array([new_slice.stats]))
            slicecnt = len(slices)
            load_slice( output_net, slicecnt, new_slice )
        # here's the granular part
        ngrains = random.randint(10,1000)
        # ngrains = 1
        schedule = marsyas.realvec(schedsize * ngrains)
        for j in range(0,ngrains):
            # in the next 10th of a second
            schedule[j*schedsize + 0] = random.randint(0,buffsize*3)#44100/10)
            # beta is skewed, so it stays pretty low
            #c = random.randint(0,len(result)-1)#int((len(result)-2)*random.betavariate(1,3))
            #c = 0#int((len(result)-2)*random.betavariate(1,3))
            c = int((len(result)-1)*random.betavariate(1,3))
            #c = random.randint(0,len(result)-1)
            #if (random.choice([True,False])):
            choice = int(result[ c ]) 
            #else:
            #    choice = chooser(result)
            #print str(choice)
            schedule[j*schedsize + 1] = choice # choose the slice
            amp = random.random() * 0.2
            depth = 512*(choice-1)/44100.0
            schedule[j*schedsize + 2] = amp
            dur = buffsize/44100.0
            when = (schedule[j*schedsize + 0])/44100.0
            if (csound):
                print "i1 %f %f %f %f %d"%(when,dur,amp,depth,choice)
        #print new_slice.str()
        #print ",".join([str(x) for x in result])
        #print(choice)
        
        schedule_control = output_net.getControl(
            grainuri + "/mrs_realvec/schedule")
        schedule_control.setValue_realvec(schedule)
        output_net.updControl(grainuri + "/mrs_bool/schedcommit",
                              marsyas.MarControlPtr.from_bool(True))
        output_net.tick()

main()

