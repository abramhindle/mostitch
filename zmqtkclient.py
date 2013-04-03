import zmq
import time
from Tkinter import *

URL="tcp://127.0.0.1:11119"

ctx = zmq.Context(1)
socket = ctx.socket(zmq.REQ)
socket.connect(URL)
cnt = 0
def send_change(state):
	socket.send_pyobj(state)
	res = socket.recv_pyobj()
        return res


class App:     
    def _update(self):
        self.state = send_change(self.state)
    def minchange(self,a1):
	self.state["mingrains"] = int(a1)
	self.__correct_grains()
        self._update()
        return 1
    def __correct_grains(self):
	mingrains = min(self.state["mingrains"], self.state["maxgrains"])
	maxgrains = max(self.state["mingrains"], self.state["maxgrains"])
	self.state["mingrains"] = mingrains
	self.state["maxgrains"] = maxgrains
    def maxchange(self,a1):
	self.state["maxgrains"] = int(a1)
	self.__correct_grains()
        self._update()
        return 1
    def ampchange(self,a1):
	self.state["amp"] = int(a1)/1000.0
        self._update()
    def topnchange(self,a1):
	self.state["topn"] = int(a1)
        self._update()
    def delaychange(self,a1):
	self.state["delay"] = int(a1)
        self._update()
    def __init__(self, master):
	maxsticky = N+S+E+W
        frame = Frame(master)
        frame.grid(sticky=maxsticky)
        top=master.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        #top.rowconfigure(1, weight=1)
        #top.rowconfigure(2, weight=1)
        top.columnconfigure(0, weight=1)
        #top.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
	self.state = {
		"maxgrains":100,
		"mingrains":10,
		"amp":20,
                "delay":1024*3
	}
	
        self.minlabel = Label(frame,text="Min Grain")
	self.minlabel.grid(row=0,column=0,sticky=maxsticky)
        self.min = Scale(frame, to=1000,command=self.minchange,orient=HORIZONTAL)
        self.min.grid(row=0,column=1,sticky=maxsticky)
	
        self.maxlabel = Label(frame,text="Max Grain")
	self.maxlabel.grid(row=1,column=0,sticky=maxsticky)
        self.max = Scale(frame, to=1000,command=self.maxchange,orient=HORIZONTAL)
        self.max.grid(row=1,column=1,sticky=maxsticky)
	
        self.label = Label(frame,text="Amp")
	self.label.grid(row=2,column=0,sticky=maxsticky)
        self.amp = Scale(frame, to=1000,command=self.ampchange,orient=HORIZONTAL)
        self.amp.grid(row=2,column=1,sticky=maxsticky)
        self.label = Label(frame,text="Top N")
	self.label.grid(row=3,column=0,sticky=maxsticky)
        self.topn = Scale(frame, from_=1, to=25,command=self.topnchange,orient=HORIZONTAL)
        self.topn.grid(row=3,column=1,sticky=maxsticky)
        self.delaylabel = Label(frame,text="Max Delay")
	self.delaylabel.grid(row=4,column=0,sticky=maxsticky)
        self.delay = Scale(frame, from_=1, to=44100,command=self.delaychange,orient=HORIZONTAL)
        self.delay.grid(row=4,column=1,sticky=maxsticky)
        
        
	self.frame = frame



root = Tk()
app = App(root)
root.mainloop()

