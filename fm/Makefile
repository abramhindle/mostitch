
fmout.sco: fm.pl
	perl fm.pl > fmout.sco

fmout.wav: fm.orc fmout.sco fm.pl
	csound -dm6 -o fmout.wav fm.orc fmout.sco 
