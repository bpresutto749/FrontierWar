;redcode-94
;name Folded Crane
;author opencode
;assert CORESIZE==8000
        spl 1
        spl 1
        spl 1
p1      spl @0, }7144
        mov }p1, >p1
p2      spl @0, }2528
        mov }p2, >p2
p3      spl @0, }1090
        mov }p3, >p3
        mov bmb, >6187
        mov bmb, }2825
        jmp p1, <-1
bmb     dat <2667, <5334
        end
