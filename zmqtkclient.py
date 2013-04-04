import zmq
import time
from Tkinter import *
from pprint import pprint

URL="tcp://127.0.0.1:11119"

ctx = zmq.Context(1)
socket = ctx.socket(zmq.REQ)
socket.connect(URL)
cnt = 0
def send_change(state):
	socket.send_pyobj(state)
	res = socket.recv_pyobj()
        return res

initial_state = send_change({})
pprint(initial_state)

class App:     
    def _update(self):
        self.state = send_change(self.state)
    def dflcommand(self, statename, a1):
        self.state[statename] = float(a1)
        self._update()
    def boolcommand(self, statename, a1):
        self.state[statename] = bool(a1)
        self._update()
    def make_slider(self,name,statename,from_=0,to=1000,command=None,resolution=1):
        labelname = statename + "_label"
        self.widgets[labelname] = Label(self.frame,text=name)
        self.widgets[labelname].grid(row=self.curr_row,column=0,sticky=self.maxsticky)
        dflcommand = lambda(x): self.dflcommand(statename,x)
        if (command == None):
                command = dflcommand 
        self.widgets[statename] = Scale(
                self.frame, 
                from_=from_,
                to=to,
                command=dflcommand,
                resolution=resolution,
                orient=HORIZONTAL)
        self.widgets[statename].set(self.state[statename])
        self.widgets[statename].grid(row=self.curr_row,column=1,sticky=self.maxsticky)
        self.curr_row += 1

    def make_check(self,name,statename,command=None):
        labelname = statename + "_label"
        self.widgets[labelname] = Label(self.frame,text=name)
        self.widgets[labelname].grid(row=self.curr_row,column=0,sticky=self.maxsticky)
        ourcheck = IntVar()
        dflcommand = lambda: self.boolcommand(statename,ourcheck.get())
        if (command == None):
                command = dflcommand 
        self.widgets[statename] = Checkbutton(
                self.frame, 
                text=name,
                variable = ourcheck,
                command=command)
        self.widgets[statename].var = ourcheck
        if (bool(self.state.get(statename,False))):
                self.widgets[statename].select()
        else:
                self.widgets[statename].deselect()
        self.widgets[statename].grid(row=self.curr_row,column=1,sticky=self.maxsticky)
        self.curr_row += 1

  
    def __init__(self, master, initial_state):
        self.curr_row = 0
        self.widgets = {}
        self.maxsticky = N+S+E+W
        self.state = initial_state
        frame = Frame(master)
        self.frame = frame
        # resizing stuff
        frame.grid(sticky=self.maxsticky)
        top=master.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        # GUI Stuff
        self.make_slider("Min Grain", "mingrains")
        self.make_slider("Max Grain", "maxgrains")
        self.make_slider("Amp", "amp",from_=0,to=1,resolution=0.01)
        self.make_slider("Top N", "topn",from_=1,to=25)
        self.make_slider("Max Delay","delay",from_=1,to=10*44100)
        self.make_check("Learn","learning")

root = Tk()
app = App(root, initial_state)
root.mainloop()

