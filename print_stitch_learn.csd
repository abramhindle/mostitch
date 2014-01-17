<CsoundSynthesizer>
<CsOptions>
; Select audio/midi flags here according to platform
; Audio out   Audio in    No messages
; -L stdin -odac           -iadc     -dm6    ;;;RT audio I/O
  -odac           -+rtaudio=jack -+jack_client=csoundStitch  -b 1024 -B 2048   ;;;RT audio I/O
; For Non-realtime ouput leave only the line below:
; -o grain3.wav -W ;;; for file output any platform
</CsOptions>
<CsInstruments>
sr	=  44100
;kr      =  100
ksmps   =  1
nchnls	=  1
gisize = 2097152

gkamp init 1
gkamp1 init 1
gkamp2 init 1
gkhz1 init 1
gkhz2 init 1

gklearn init 0
gkplay init 1

gklearndex init 0

ilearninstr =  1
iuselearndex = -1




FLcolor	180,200,199
FLpanel 	"Learn Box",200,200
    gkamp,    iknob1 FLknob  "AMP", 0.001, 32000, -1,1, -1, 50, 0,0
    gkamp1,    giknobamp1 FLknob  "AMP 1", 0.001, 4, -1,1, -1, 50, 50,0
    gkamp2,    giknobamp2 FLknob  "AMP 2", 0.001, 4, -1,1, -1, 50, 100,0
    gkhz1,    giknobhz1 FLknob  "HZ 1", 0.001, 22000, -1,1, -1, 50, 0,75
    gkhz2,    giknobhz2 FLknob  "HZ 2", 0.001, 22000, -1,1, -1, 50, 50,75
    ;gkport,    iknobport FLknob  "Port", 0.01, 1, -1,1, -1, 50, 100,100
    ;                                      ionioffitype
    gklearndex,    giknolearndex FLknob  "LearnDex", 0, 20, 0,1, -1, 50, 125, 75
    gklearn,    iklearn FLbutton  "LEARN", 1, 0, 22, 66, 50, 0  ,150, -1
    gkplay,    ikplay FLbutton  "PLAY", 1, 0, 22, 66, 50, 66  ,150, -1
    gktrigger,    ikplay FLbutton  "Trigger", 0, 0, 1, 66, 50, 133  ,150, 0, ilearninstr, 0.001, 0.001, 0.001, iuselearndex


    FLsetVal_i   1.0, iknob1
    FLsetVal_i   1.0, giknobamp1
    FLsetVal_i   1.0, giknobamp2
    FLsetVal_i   1.0, giknobhz1
    FLsetVal_i   1.0, giknobhz2
    
FLpanel_end	;***** end of container

FLrun		;***** runs the widget thread 




/* f#  time  size  1  filcod  skiptime  format  channel */
; giImpulse01     ftgen   101, 0, gisize, 1, "1.harmonica.wav", 0, 0, 0	

/* Bartlett window */
itmp	ftgen 1, 0, 16384, 20, 3, 1
/* sawtooth wave */
itmp	ftgen 2, 0, 16384, 7, 1, 16384, -1
/* sine */
itmp	ftgen 4, 0, 16384, 10, 1


itmp	ftgen 201, 0, 16384, 7, 0.1, 16384, 0.1
itmp	ftgen 202, 0, 16384, 7, 0.1, 16384, 0.1
;itmp	ftgen 203, 0, 16384, 7, 1, 16384, 1
;itmp	ftgen 204, 0, 16384, 7, 1, 16384, 1
; exponentials
itemp ftgen 201, 0, 16384, -21, 4, 4
itemp ftgen 202, 0, 16384, -21, 4, 0.5
itemp ftgen 203, 0, 16384, -21, 4, 1000
itemp ftgen 204, 0, 16384, -21, 4, 17
;itmp	ftgen 203, 0, 16384, -25, 0, 1000, 16384, 40
;itmp	ftgen 204, 0, 16384, -25, 0, 200, 16384, 0.1
;itmp	ftgen 203, 0, 4096, -9,    1, 1, 0,        2, 0.5, 0,     4, 0.25, 0,   8, 0.125, 0,  16, 0.0625, 0,  32, 0.3125, 0,   64, 0.015625, 0
;itmp	ftgen 204, 0, 4096, 9,    1, 1, 0,        2, 0.5, 0,     4, 0.25, 0,   8, 0.125, 0,  16, 0.0625, 0,  32, 0.3125, 0,   64, 0.015625, 0

gisintbl = 101
girisetbl = 102
gisheptbl = 103
gisquaretbl = 104
gisawtbl = 105

; plain old sine wave
itmp ftgen gisintbl, 0, 4096, 10,   1

; sinusoidal rise shape for granular synthesis
itmp ftgen girisetbl, 0, 1024, 19,   0.5, 0.5, 270, 0.5

; Shepardesque tone:  octaves with exponential dropoff
itmp ftgen gisheptbl, 0, 4096, 9,    1, 1, 0,        2, 1/2, 0,     4, 1/4, 0,   8, 1/8, 0, 16, 1/16, 0,  32, 1/32, 0,   64, 1/64, 0

; square wave (rise/fall limited a little)
itmp ftgen gisquaretbl, 0, 1024, 7,   0, 10, 1, 492, 1, 20, -1, 492, -1, 10, 0

; nice sharp sawtooth
itmp ftgen gisawtbl, 0, 1024, 7,   -1, 1024, 1

instr 1
      idur = p3
      iamp = p4
      iindex = (p5 < 0 ? i(gklearndex) : p5)
      if (gklearn > 0) then
            printf "GKLEARN %d %d\n",1, iindex, gklearn
            tabw i(gkamp1), iindex, 201 
            tabw i(gkamp2), iindex, 202
            tabw i(gkhz1), iindex, 203 
            tabw i(gkhz2), iindex, 204
            ;tableiw 
            ;            tableiw i(gkamp2), iindex, 202 ,0 ,0 ,0
            ;tableiw i(gkhz1), iindex, 203 ,0 ,0 ,0
            ;tableiw i(gkhz2), iindex, 204 ,0 ,0 ,0
      endif
      if (gkplay > 0) then
            printf "GKPLAY %d %d\n",1, iindex, gkplay
            kamp1 tab iindex, 201
            kamp2 tab iindex, 202
            khz1 tab iindex, 203
            khz2 tab iindex, 204
            gkamp1 = kamp1
            gkamp2 = kamp2
            gkhz1 = khz1
            gkhz2 = khz2
            printf "GKPLAY %d %f %f %f %f\n",1, iindex, gkamp1, gkamp2, gkhz1, gkhz2
            FLsetVal_i i(gkamp1), giknobamp1
            FLsetVal_i i(gkamp2), giknobamp2
            FLsetVal_i i(gkhz1), giknobhz1
            FLsetVal_i i(gkhz2), giknobhz2
      endif
      turnoff
endin

instr 3
aa01     oscili gkamp1, gkhz1, 2
aa02     oscili gkamp2, gkhz2, 4
aout     = aa01 * aa02 - 0.01 * aa01 - 0.01 * aa02 
         out aout * gkamp
endin

instr Pad

a1 oscili gkamp1,gkhz1,gisawtbl,rnd(1)
a3 oscili gkamp2*0.20,32768/gkhz1,gisquaretbl,rnd(1)
a2 lowpass2 a1+a3,gkhz2,2
out gkamp*10000*a2

endin

instr Volume
      idur = p3
      iamp = p4
      gkamp = k(iamp)
      turnoff
endin

instr Learn
      idur = p3
      ilearn = p4
      gklearn = k(ilearn)
      turnoff
endin

instr Play
      idur = p3
      ilearn = p4
      gkplay = k(ilearn)
      turnoff
endin


instr Setter
      idur = p3
      igkamp1 = p4
      igkamp2 = p5
      igkhz1 = p6
      igkhz2 = p7
      gkamp1 = igkamp1
      gkamp2 = igkamp2
      gkhz1 = igkhz1
      gkhz2 = igkhz2
      printf_i "Setter %f %f %f %f\n",1, i(gkamp1), i(gkamp2), i(gkhz1), i(gkhz2)
      turnoff
endin
      
instr Print
      itab = p4
      iindex = p5
      iout tab_i iindex, itab
      printf_i "Table %d Index %d Value %f\n",1, itab, iindex, iout
endin


</CsInstruments>
<CsScore>
 
t 0 60
;f 0 3600
;i3 0 38
;i3 0 3600
i"Pad" 0 3600

;i"Play" 0 1 0
;i"Learn" 0 1 1
;i"Volume" 0 1 10000
;i"Setter" 0 0.1 1 1 111 31
;i1 0.1 0.1 1 1
;i"Setter" 0.2 0.1 1 1 32 222
;i1 0.3 0.1 1 2
;i"Setter" 0.4 0.1 1 1 33 333
;i1 0.5 0.1 1 3
;i"Print" 0.55 0.01 201 1
;i"Print" 0.55 0.01 202 1
;i"Print" 0.55 0.01 203 1
;i"Print" 0.55 0.01 204 1
;i"Print" 0.55 0.01 201 2
;i"Print" 0.55 0.01 202 2
;i"Print" 0.55 0.01 203 2
;i"Print" 0.55 0.01 204 2
;i"Print" 0.55 0.01 201 3
;i"Print" 0.55 0.01 202 3
;i"Print" 0.55 0.01 203 3
;i"Print" 0.55 0.01 204 3
;i"Learn" 0.6 0.1 0
;i"Play" 0.7 1 1
;i1 1.0 1 1 1
;i1 4.0 1 1 2
;i1 7.0 1 1 3
;i1 10.0 1 1 1
;i1 13.0 1 1 2
;i1 16.0 1 1 3
;i1 19.0 1 1 1
;i1 22.0 1 1 2
;i1 25.0 1 1 3
;i1 28.0 1 1 1
;i1 31.0 1 1 2
;i1 34.0 1 1 3




</CsScore>
</CsoundSynthesizer>
