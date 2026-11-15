;redcode-94
;name pg3
;author Bart
;assert CORESIZE==8000
        org start
start   spl 1
        spl 1
        spl 1
s1      spl @0, }2381
        mov.i }s1, >s1
s2      spl @0, }6110
        mov.i }s2, >s2
s3      spl @0, }6768
        mov.i }s3, >s3
        mov.i bomb, >2074
        mov.i bomb, }5042
        jmp s1
bomb    dat >2667, >5334
