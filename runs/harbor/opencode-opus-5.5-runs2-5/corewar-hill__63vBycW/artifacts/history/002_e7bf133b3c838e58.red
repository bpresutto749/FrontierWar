;redcode-94
;name Origami Fleet
;author opencode
;strategy silk paper, 3 stages
        org start
start   spl 1
        spl 1
        spl 1
        spl 1
p1      spl @0, }5310
        mov.i }p1, >p1
p2      spl @0, }2200
        mov.i }p2, >p2
        mov.i bmb, }3456
p3      spl @0, }-777
        mov.i }p3, >p3
        mov.i bmb, }p3+100
        jmp p1, <-50
bmb     dat <2667, <5334
