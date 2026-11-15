;redcode-94
;name Silk Pebble
;author Bart
;assert CORESIZE==8000
        org go
go      spl stn
start   spl 1
        spl 1
        spl 1
s0      spl @0, }4267
        mov.i }s0, >s0
s1      spl @0, }860
        mov.i }s1, >s1
s2      spl @0, }1562
        mov.i }s2, >s2
        mov.i bomb, {3490
        mov.i bomb, <7436
        mov.i bomb, }6911
        jmp s0
bomb    spl #0, <2667
stn     add #3364, sptr
        mov sbmb, @sptr
        jmp stn
sptr    dat 0, 0
sbmb    dat >1, >1
