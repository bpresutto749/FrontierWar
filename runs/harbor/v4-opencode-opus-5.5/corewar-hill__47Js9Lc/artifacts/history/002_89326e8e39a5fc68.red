;redcode-94
;name Folded Crane
;author me
;strategy three-layer silk paper with dat bombing
;assert CORESIZE==8000
        spl     1,      <300
        spl     1,      <400
        spl     1,      <500
p1      spl     @0,     >3620
        mov     }p1,    >p1
p2      spl     @0,     >1290
        mov     }p2,    >p2
p3      spl     @0,     >5010
        mov     }p3,    >p3
        mov.i   bmb,    }2341
        mov.i   bmb,    {-777
        jmp     p1,     <-1433
bmb     dat     <2667,  <5334
