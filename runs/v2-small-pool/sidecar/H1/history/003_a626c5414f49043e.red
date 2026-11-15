;redcode-94
;name Origami
;author Barthelemy Presutto
;strategy silk paper
;assert CORESIZE==8000
        spl 1, <2347
        spl 1, <6196
        spl 1, <7648
p0      spl 5002, 0
        mov.i >p0, }p0
p1      spl 4953, 0
        mov.i >p1, }p1
p2      spl 1768, 0
        mov.i >p2, }p2
        mov.i bomb, @4212
        mov.i bomb, >1329
        jmp p2, <p2
bomb    dat >2667, >5334
        end
