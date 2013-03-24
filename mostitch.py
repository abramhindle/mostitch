#!/usr/bin/env python
"""Originally from in_out.pya
   Assume GPL2
"""
"""a quick hack to demonstrate getting data between python and
   marsyas. """

import sys
import numpy
import pylab
import marsyas
import marsyas_util
import pdb
import pyflann
from pyflann import *
from numpy import *
from numpy.random import *
import cPickle
import random

#PLOT = True
PLOT = False
pyflann.set_distance_type('kl')
flann = FLANN()
topn = 20
buffsize = 512

texture = ["Rms/rms", "AubioYin/pitcher","ZeroCrossings/zcrs" ,"Series/lspbranch" ,"Series/lpccbranch" ,"MFCC/mfcc" ,"SCF/scf" ,"Rolloff/rf" ,"Flux/flux" ,"Centroid/cntrd" ,"Series/chromaPrSeries"]
detectors = ["Fanout/detectors", texture]

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
        self.slices.append( s )
        return s
        
    def get_slices( self ):
        return self.slices
    
def read_in_file_with_stats(filename_input):
    fm = FileMetricExtractor( filename_input )
    fm.readeverything()
    return fm.get_slices()

def make_output():
    series = ["Series/output", ["RealvecSource/real_src",
        "AudioSink/dest"]]
    this_net = marsyas_util.create(series)
    this_net.updControl("mrs_natural/inSamples", buffsize)
    this_net.updControl("mrs_real/israte", 44100.0)
    this_net.updControl("AudioSink/dest/mrs_bool/initAudio",marsyas.MarControlPtr.from_bool(True))
    return this_net

def play_slices(slices, output_net_begin_control, output_net):
    for play_slice in slices:
        output_net_begin_control.setValue_realvec(play_slice.rv)
        output_net.tick()

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
    #params = flann.build_index(dataset, algorithm="autotuned", target_precision=0.9, log_level = "info")
    params = flann.build_index(dataset, algorithm="kdtree", target_precision=0.9, log_level = "info")
    output_net = make_output()
    output_net_begin_control = output_net.getControl(
        "RealvecSource/real_src/mrs_realvec/data")
    output_net_begin = marsyas.realvec(buffsize)
    sme = StreamMetricExtractor()
    while sme.has_data():
        # tick is done here
        new_slice = sme.operate()
        results, dists = flann.nn_index(array([new_slice.stats]),topn, checks=params["checks"]);
        result = results[0]
        # beta is skewed, so it stays pretty low
        c = 1+int((len(result)-2)*random.betavariate(1,3))
        choice = result[ c ] #random.randint(1,len(result)-1)]
        print new_slice.str()
        print ",".join([str(x) for x in result])
        print(choice)
        play_slice = slices[choice]        
        output_net_begin_control.setValue_realvec(play_slice.rv)
        output_net.tick()

main()

