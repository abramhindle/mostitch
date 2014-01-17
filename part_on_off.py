from mostitch import *
import partfun
class PrintStitch(Mostitch):
    def __init__(self, buffsize = 1024, state = {}):
        super(PrintStitch,self).__init__(buffsize, state)        
        self.last = 'Z'
	self.d = {}
	self.d["A"] = "i1 0 0.1 1 \"A\""
	self.d["B"] = "i2 0 0.1 2 \"B\""
	self.d["C"] = "i3 0 0.1 3 \"C\""
	self.d["D"] = "i4 0 0.1 4 \"D\""
    # disable playing audio
    def init_output_network(self):
        self.output_net = None
    def schedule_and_play(self,schedule):
        None
    def init_audio(self):
        None
    def post_schedule_grain(self, delay, choice, amp ):
        None
    def load_slice(self, slice):
        None
    # hook into the results
    def post_result_hook(self, results, dists):
        #print " ".join([str(x) for x in results])
        #print " ".join([str(x) for x in dists])
        #if (results[1] > 30):
        #out = "i1 0 0.2 1 %s" % str(results[1])
        #warn(out)
        #print(out)
        out = partfun.partfun(results[0], results[1])
        #out = "i1 %f 0.2 1 %s" % (time,s)
	#if (not (out == self.last)):
        warn(self.d[out])
        print(self.d[out])
	self.last = out


class PrintStitchFromFile(PrintStitch):
    def __init__(self, inputfile, buffsize = 1024, state = {}):
        self.inputfile = inputfile
        self.t = 0
        super(PrintStitchFromFile, self).__init__(buffsize, state)
    def make_zmq(self):
        None
    def process_zmq(self):
        None
    def init_input_network(self):
        self.sme = FileMetricExtractor(self.inputfile)
    def post_result_hook(self, results, dists):
        time = self.t * 1024 / 44100.0
        self.t += 1
        s = " ".join([str(res) for res in results])
	out = partfun.partfun(results[0], results[1])
        #out = "i1 %f 0.2 1 %s" % (time,s)
        print(out)


unbuffered_stdout()

def add_args(parser):
    parser.add_argument('--input', default=None, help='Input File as audio stream')

def add_settings(args,state,settings):
    settings["input"] = args.input

settings = parse_args(add_args, add_settings)
# settings["state"]["learning"] = True

def make_print_stitch(settings):
    if (settings["input"] == None):
        return PrintStitch( settings["buffsize"], settings["state"])
    else:
        return PrintStitchFromFile( settings["input"], settings["buffsize"], settings["state"])

mostitch = make_print_stitch(settings)
mostitch.mostitch_main( settings["files"], settings["window_name"] )


