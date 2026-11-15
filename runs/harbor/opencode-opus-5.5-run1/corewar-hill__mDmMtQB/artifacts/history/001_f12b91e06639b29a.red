;redcode-94
;name Folded Silk
;author opencode
;strategy silk paper with bombing
;assert CORESIZE==8000
        org start
start   spl 1
        spl 1
        spl 1
        spl 1
p1      spl @0, }3620
        mov.i }-1, >-1
p2      spl @0, }1872
        mov.i }-1, >-1
        mov.i #1, <1
        mov.i bmb, {2667
        jmp -3, <-1400
bmb     dat <2667, <1
