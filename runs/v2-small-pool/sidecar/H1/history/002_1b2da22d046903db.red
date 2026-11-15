;redcode-94
;name Origami
;author Barthelemy Presutto
;strategy silk paper
;assert CORESIZE==8000
        spl 1, <2034
        spl 1, <1989
        spl 1, <295
p0      spl 1647, 0
        mov.i >p0, }p0
p1      spl 2863, 0
        mov.i >p1, }p1
p2      spl 1622, 0
        mov.i >p2, }p2
        mov.i bomb, @1319
        mov.i bomb, <4379
        jmp p2, <p2
bomb    dat >2667, >5334
        end
