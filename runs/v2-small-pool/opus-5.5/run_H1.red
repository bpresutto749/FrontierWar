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
p2      spl 2410, 0
        mov.i >p2, }p2
        mov.i bomb1, {6260
        jmp p2, <p2
bomb0   dat >2667, >5334
bomb1   dat }1, >1
        end
