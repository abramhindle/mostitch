<CsoundSynthesizer>
<CsOptions>
; Select audio/midi flags here according to platform
; Audio out   Audio in    No messages
; -L stdin -odac           -iadc     -dm6    ;;;RT audio I/O
  -L stdin  -odac         -dm6  -+rtaudio=jack -+jack_client=csoundPart  -b 1024 -B 2048   ;;;RT audio I/O
; For Non-realtime ouput leave only the line below:
; -o grain3.wav -W ;;; for file output any platform
</CsOptions>
<CsInstruments>
sr	=  44100
;kr      =  100
ksmps   =  1
nchnls	=  1
gisize = 2097152

gkamp1 init 0
gkamp2 init 0
gkamp3 init 0
gkamp4 init 0

instr 1
	idur = p3
	iindex = p4
	iwhatever = p5
	printf_i "1Playing %f\n",1, iindex
	gkamp1 = 1
	gkamp2 = gkamp2 * 0.9
	gkamp3 = gkamp3 * 0.9
	gkamp4 = gkamp4 * 0.9
	turnoff
endin
instr 2
	idur = p3
	iindex = p4
	iwhatever = p5
	printf_i "2Playing %f\n",1, iindex
	gkamp2 = 1
	gkamp1 = gkamp1 * 0.9
	gkamp3 = gkamp3 * 0.9
	gkamp4 = gkamp4 * 0.9
	turnoff
endin
instr 3
	idur = p3
	iindex = p4
	iwhatever = p5
	printf_i "3Playing %f\n",1, iindex
	gkamp3 = 1
	gkamp1 = gkamp1 * 0.9
	gkamp2 = gkamp3 * 0.9
	gkamp4 = gkamp4 * 0.9
	turnoff
endin
instr 4
	idur = p3
	iindex = p4
	iwhatever = p5
	printf_i "4Playing %f\n",1, iindex
	gkamp4 = 1
	gkamp1 = gkamp1 * 0.9
	gkamp2 = gkamp3 * 0.9
	gkamp3 = gkamp4 * 0.9
	turnoff
endin
instr 666
      a1, a2 diskin2 "partition_exp/jack_capture_02.wav", 1, 0, 1
      ;;a1, a2 diskin2 "partition_exp/reversed-and-screwed.wav", 1, 0, 1
      ;; a3, a4 diskin2 "partition_exp/jack_capture_03.wav", 1, 0, 1
      a3  diskin2 "partition_exp/tones.wav", 1, 0, 1
      a5  diskin2 "partition_exp/reversed-and-screwed.wav", 1, 0, 1
      ;;a5, a6 diskin2 "partition_exp/jack_capture_04.wav", 1, 0, 1
      a7, a8 diskin2 "partition_exp/jack_capture_05.wav", 1, 0, 1
      aleft  = gkamp1 * a1 + gkamp2 * a3 + gkamp3 * a5 + gkamp4 * a7
      aright = gkamp1 * a2 + gkamp2 * a3 + gkamp3 * a5 + gkamp4 * a7
      outs aleft, aright
endin
</CsInstruments>
<CsScore>
t 0 60
i666 0 3600
i1 0 0.1 1 "A"
i2 5 0.1 2 "B"
i3 10 0.1 3 "C"
i4 15 0.1 4 "D"
i1 20 0.1 1 "A"
i2 25 0.1 2 "B"
i3 30 0.1 3 "C"
i4 35 0.1 4 "D"
</CsScore>
</CsoundSynthesizer>
