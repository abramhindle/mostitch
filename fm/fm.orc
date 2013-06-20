       	sr = 44100
	kr = 441
	ksmps = 100
	nchnls = 1

gkamp 	init 1
gkfrq 	init 1
gkcar 	init 1
gkmod 	init 1
gkindx	init 1



        instr 1
        ;p3 = 2/44100.0
        gkamp = p4
        gkfrq = p5
        gkcar = p6
        gkmod = p7
        gkindx = p8
        turnoff
        endin

        instr 555
asig    foscili gkamp, gkfrq, gkcar, gkmod, gkindx, 1
        out asig
        endin
