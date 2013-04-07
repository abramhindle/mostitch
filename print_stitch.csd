<CsoundSynthesizer>
<CsOptions>
; Select audio/midi flags here according to platform
; Audio out   Audio in    No messages
; -L stdin -odac           -iadc     -dm6    ;;;RT audio I/O
 -odac         -dm6  -+rtaudio=jack -+jack_client=csoundStitch  -b 1024 -B 2048   ;;;RT audio I/O
; For Non-realtime ouput leave only the line below:
; -o grain3.wav -W ;;; for file output any platform
</CsOptions>
<CsInstruments>
sr	=  44100
;kr      =  100
ksmps   =  1
nchnls	=  1
gisize = 2097152
/* f#  time  size  1  filcod  skiptime  format  channel */
; giImpulse01     ftgen   101, 0, gisize, 1, "1.harmonica.wav", 0, 0, 0	

/* Bartlett window */
itmp	ftgen 1, 0, 16384, 20, 3, 1
/* sawtooth wave */
itmp	ftgen 2, 0, 16384, 7, 1, 16384, -1
/* sine */
itmp	ftgen 4, 0, 1024, 10, 1

instr 1
      idur = p3
      iamp = p4
      ipitch = p5
      itab = 101
aenv    oscili iamp, 1/idur, 1        
aa01     poscil 1, ipitch, 2
      out 1000*aenv * aa01
endin

</CsInstruments>
<CsScore>

t 0 60
f 0 3600





</CsScore>
</CsoundSynthesizer>
