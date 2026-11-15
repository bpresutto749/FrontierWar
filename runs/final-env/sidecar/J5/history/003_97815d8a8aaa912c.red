;redcode-94
;name pa11
;author Bart
;assert CORESIZE==8000
        org start
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
bomb    dat }2667, }5334
