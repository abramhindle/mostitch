#!/usr/bin/env python
"""
Mostitch is Marsyas Ostitch. 

Ostitch was an audio collager. An audio collager takes input source
audio and produces output source audio which is composed of chunks of
the input. The output is usually is meant to mimic another signal
(like a song or speech).

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
import marsyas
import marsyas_util
import pdb
import pyflann
from pyflann import *
from numpy import *
#from numpy.random import *
import cPickle
import random

#PLOT = True
PLOT = False
pyflann.set_distance_type('kl')
flann = FLANN()
topn = 20
buffsize = 512

#texture = ["Rms/rms", "AubioYin/pitcher","ZeroCrossings/zcrs" ,"Series/lspbranch" ,"Series/lpccbranch" ,"MFCC/mfcc" ,"SCF/scf" ,"Rolloff/rf" ,"Flux/flux" ,"Centroid/cntrd" ,"Series/chromaPrSeries"]
texture = ["Rms/rms", "AubioYin/pitcher","ZeroCrossings/zcrs" ,"Rolloff/rf" ,"Flux/flux" ,"Centroid/cntrd","AbsMax/abs","Energy/energy"]

#"AimGammatone/aimgamma"]
detectors = ["Fanout/detectors", texture]

grainuri = "RealvecGrainSource/real_src"


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
        series = ["Series/input", [self.get_source(), detectors]]
        self.input_net = marsyas_util.create( series )
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
    this_net = marsyas_util.create(series)
    this_net.updControl("mrs_natural/inSamples", buffsize)
    this_net.updControl("mrs_real/israte", 44100.0)    
    return this_net

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

def main():
    try:    
        filename_input = sys.argv[1]
    except:
        print "USAGE: ./mostitch.py input_filename.wav"
        exit(1)
    # read the slices    
    slices = read_in_file_with_stats( filename_input )
    print(len(slices))
    # get NN
    dataset = array([s.stats for s in slices])
    #window = triangle(buffsize)
    window = hann_window(buffsize)
    #window = flat(buffsize)
    #flat(buffsize)#saw(buffsize)#triangle(buffsize) #flat(buffsize) #triangle(buffsize)
    for slice in slices:
        slice.rv *= window
    #params = flann.build_index(dataset, algorithm="autotuned", target_precision=0.9, log_level = "info")
    params = flann.build_index(dataset, algorithm="kdtree", target_precision=0.9, log_level = "info")
    output_net = make_output()
    this_net = output_net
    slicecnt = 0
    for slice in slices:
        load_slice( output_net, slicecnt, slice )
        slicecnt += 1

    sme = StreamMetricExtractor()
    schedule_control = output_net.getControl(
        grainuri + "/mrs_realvec/schedule")
    schedsize = 3 # size of a schedule
    nn = schedsize
    i = 0

    this_net.updControl("AudioSink/dest/mrs_bool/initAudio",marsyas.MarControlPtr.from_bool(True))
    while 1:
        schedule = marsyas.realvec(nn * buffsize)
        for j in range(0,buffsize):
            schedule[j*nn+0] = j
            schedule[j*nn+1] = j + (i % slicecnt)
            schedule[j*nn+2] = 0.25
        # this sets a schedule
        output_net_begin_control = this_net.getControl("RealvecGrainSource/real_src/mrs_realvec/schedule")
        output_net_begin_control.setValue_realvec(schedule)
        # this commits the schedule
        this_net.updControl("RealvecGrainSource/real_src/mrs_bool/schedcommit",marsyas.MarControlPtr.from_bool(True))
        print "\t".join([str(x) for x in schedule])
        this_net.tick()
        i = i + 1


#    while sme.has_data():
#        # tick is done here
#        new_slice = sme.operate()
#        ngrains = 512
#        schedule = marsyas.realvec(nn * ngrains)
#        for j in range(0,ngrains):
#            schedule[j*nn + 0] = j#random.randint(0,buffsize) # in how many samples should be play it
#            schedule[j*nn + 1] = random.randint(1,slicecnt)
#            schedule[j*nn + 2] = 0.1
#            print str(schedule[j*nn + 1])
#        output_net_begin_control = output_net.getControl("RealvecGrainSource/real_src/mrs_realvec/schedule")
#        output_net_begin_control.setValue_realvec(schedule)
#        output_net.updControl("RealvecGrainSource/real_src/mrs_bool/schedcommit",marsyas.MarControlPtr.from_bool(True))
#        output_net.tick()
main()

