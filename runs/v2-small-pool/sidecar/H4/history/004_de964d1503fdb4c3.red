;redcode-94
;name Ply
;author anon
;strategy silk paper
;assert CORESIZE==8000
        org start
start   spl 1, <300
        spl 1, <150
        spl 1, <450
silk1   spl @0, }284
        mov.i }silk1, >silk1
silk2   spl @0, }7805
        mov.i }silk2, >silk2
silk3   spl @0, }3882
        mov.i }silk3, >silk3
silk4   spl @0, }3011
        mov.i }silk4, >silk4
silk5   spl @0, }1476
        mov.i }silk5, >silk5
        mov.i {silk1, <silkj
silkj   jmp @0, >5104
bmb     dat <2667, <5334
