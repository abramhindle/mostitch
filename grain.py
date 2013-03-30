#!/usr/bin/env python
import sys
import numpy
import math
from marsyas import * 
import marsyas
import marsyas_util
import random
import math

mars = MarSystemManager()
buffsize=512
series = ["Series/output", ["RealvecGrainSource/real_src", "AudioSink/dest"]]
print "Make Network"
this_net = marsyas_util.create(series)
print "Set InSamples"
this_net.updControl("mrs_natural/inSamples", buffsize)
print "Set Rate"
this_net.updControl("mrs_real/israte", 44100.0)
print "Make grains"
grain1 = marsyas.realvec(buffsize)
grain2 = marsyas.realvec(buffsize)
grain3 = marsyas.realvec(buffsize)
grain4 = marsyas.realvec(3*buffsize)
for i in range(0, buffsize):
    grain1[i] = 2.0 if (i%10==0) else -0.5
    grain2[i] = 0.33 * (i % 2)
    grain3[i] = -1
    grain4[i] = -2.0 if (i%20==0) else 0.0




data_uri = "RealvecGrainSource/real_src/mrs_realvec/data"

#grains = [[1,grain1],[2,grain2],[3,grain3],[4,grain4]]
grains = [[1,grain1],[2,grain2],[3,grain3]]

def hann( n, N ):
    return 0.5 * (1 - math.cos( (2 * math.pi * n) / (N - 1)))

def hann_window( size ):
    v = marsyas.realvec( size )
    for i in range(0,size):
        v[i] = hann( i, size)
    return v



window = hann_window(buffsize)
for g in grains:
    g[1] *= window

grains.append( [4,grain4] )

#grains = [[4,grain4]]
n = len(grains)
for graint in grains:
    grain_id = graint[0]
    grain = graint[1]
    print ("Loading grain %d" % grain_id)
    print "Set Index"
    myindex = this_net.getControl("RealvecGrainSource/real_src/mrs_natural/index")
    myindex.setValue_natural( grain_id)
    #this_net.updControl("RealvecGrainSource/real_src/mrs_natural/index", grain_id)
    control = this_net.getControl(data_uri)
    print "Set Grain"
    control.setValue_realvec(grain)
    print "Commit"
    this_net.updControl("RealvecGrainSource/real_src/mrs_bool/commit",marsyas.MarControlPtr.from_bool(True))


output_net_begin_control = this_net.getControl("RealvecGrainSource/real_src/mrs_realvec/schedule")

this_net.updControl("AudioSink/dest/mrs_bool/initAudio",marsyas.MarControlPtr.from_bool(True))


print "Starting Loop"
t = 0
i = 0
c = 1



while 1:
    size = n+1
    if (i % 100 == 0):
        c = c + 1
    nn = 3
    schedule = marsyas.realvec(nn * size)
    schedule[0] = 0
    schedule[1] = 1
    schedule[2] = 0.25    
    for j in range(1,size):
        #schedule[j*nn + 0] = 0#random.randint(0,44100) # in how many samples should be play it
        schedule[j*nn + 0] = random.randint(0,buffsize) # in how many samples should be play it
        schedule[j*nn + 1] = (j % n) + 1
        schedule[j*nn + 2] = 0.25
    # this sets a schedule
    output_net_begin_control = this_net.getControl("RealvecGrainSource/real_src/mrs_realvec/schedule")
    output_net_begin_control.setValue_realvec(schedule)
    # this commits the schedule
    this_net.updControl("RealvecGrainSource/real_src/mrs_bool/schedcommit",marsyas.MarControlPtr.from_bool(True))
    this_net.tick()
    t = t + buffsize
    i = i + 1
