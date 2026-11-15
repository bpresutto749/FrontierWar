;redcode-94
;name Oneshot B
;author anon
;strategy 0.5c jmz scan, then djn d-clear
S       equ   3048
        org   scan
gate    dat   0,     0
scan    add.ab #S,   gate
        jmz.f  scan, @gate
        sub.ab #12,  gate
clr     spl    #0,   0
mv      mov.i  bomb, >gate
        djn.f  mv,   >gate
bomb    dat    0,    bomb-gate
