from mostitch import *

class PrintStitch(Mostitch):
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
        print " ".join([str(x) for x in results])
        
settings = parse_args()
# settings["state"]["learning"] = True
mostitch = PrintStitch( settings["buffsize"], settings["state"])
mostitch.mostitch_main( settings["files"], settings["window_name"] )


