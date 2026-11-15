;redcode-94
;name Mulberry
;author anon
;assert CORESIZE==8000
        spl 1, <-200
        spl 1, <-300
        spl 1, <-400
s1      spl @0, }1817
        mov }s1, >s1
s2      spl @0, }3757
        mov }s2, >s2
s3      spl @0, }-1213
        mov }s3, >s3
        mov.i #1, {2267
        mov s3+1, <-1400
        jmp s3, <-2667
