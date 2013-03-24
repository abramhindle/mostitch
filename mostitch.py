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
from pyflann import *
from numpy import *
from numpy.random import *

#PLOT = True
PLOT = False
flann = FLANN()
topn = 20
buffsize = 1024

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
    # and this was the old code!
    series = ["Series/input", ["SoundFileSource/src", detectors]]
    this_net = marsyas_util.create( series )
    this_net.updControl(
        "SoundFileSource/src/mrs_string/filename",
        filename_input)
    input_net = this_net
    notempty = input_net.getControl("SoundFileSource/src/mrs_bool/hasData")
    input_net_end_control = input_net.getControl("SoundFileSource/src/mrs_realvec/processedData")
    metrics_control = input_net.getControl("mrs_realvec/processedData")
    input_net.tick()
    # is this a copy
    input_net_end = input_net_end_control.to_realvec()
    slices = []
    while notempty.to_bool():
        input_net.tick()
        input_net_end = input_net_end_control.to_realvec()
        stats = metrics_control.to_realvec()
	print stats[0]
        #pdb.set_trace()
	stats = [x for x in stats]
	rv = input_net_end.getSubVector(0,len(input_net_end))
        slices.append( Slice( rv, stats ) )
    return slices  

def make_input():
    series = ["Series/input", ["AudioSource/src",detectors]]
    this_net = marsyas_util.create(series)
    return this_net

def make_output():
    series = ["Series/output", ["RealvecSource/real_src",
        "AudioSink/dest"]]
    this_net = marsyas_util.create(series)
    this_net.updControl("mrs_natural/inSamples", buffsize)
    this_net.updControl("mrs_real/israte", 44100.0)
    return this_net



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
    #pdb.set_trace()
    dataset = array([s.stats for s in slices])
    params = flann.build_index(dataset, algorithm="autotuned", target_precision=0.9, log_level = "info")
    i = 0
    for slice in slices:
        testset = [slice.stats]
        results, dists = flann.nn_index(array(testset),topn, checks=params["checks"]);
        for result in results:
	    print str(i) + "\t" + ",".join( [str(r) for r in result] )
        i = i + 1
    #output series and tick
    output_net = make_output()
    output_net_begin_control = output_net.getControl(
        "RealvecSource/real_src/mrs_realvec/data")
    output_net_begin = marsyas.realvec(buffsize)
    sme = StreamMetricExtractor()
    while sme.has_data():
        new_slice = sme.operate()
        results, dists = flann.nn_index(array([new_slice.stats]),topn, checks=params["checks"]);
        result = results[0]
        first = r[1]
        play_slice = slices[first]        
        output_net_begin_control.setValue_realvec(play_slice.rv)
        output_net.tick()

#        for slice in slices:
#        print len(slice.rv)

def oldmain():
    try:    
        filename_input = sys.argv[1]
        filename_output = sys.argv[2]
    except:
        print "USAGE: ./in_out.py input_filename.wav output_filename.wav"
        exit(1)
    
    input_net = make_input(filename_input)
    output_net = make_output(filename_output)

    notempty = input_net.getControl("SoundFileSource/src/mrs_bool/hasData")
    input_net_end_control = input_net.getControl("mrs_realvec/processedData")
    output_net_begin_control = output_net.getControl(
        "RealvecSource/real_src/mrs_realvec/data")
    output_net_begin = marsyas.realvec(buffsize)
    while notempty.to_bool():
        ### get input data
        input_net.tick()
        input_net_end = input_net_end_control.to_realvec()

        ### do something with it
	print input_net_end.getSize()
        for i in range(input_net_end.getSize()):
            output_net_begin[i] = 0.5*input_net_end[i]
	print ",".join([str(input_net_end) for x in input_net_end])
        output_net_begin_control.setValue_realvec(output_net_begin)
        if PLOT:
            pylab.plot(input_net_end, label="input")
            pylab.plot(output_net_begin, label="output")
            pylab.legend()
            pylab.show()

        ### set output data
        output_net.tick()


main()

