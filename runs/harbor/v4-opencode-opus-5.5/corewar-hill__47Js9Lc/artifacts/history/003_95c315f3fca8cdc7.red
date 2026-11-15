;redcode-94
;name Folded Crane
;author me
;strategy three-layer silk paper with dat bombing
;assert CORESIZE==8000
        spl     1,      <300
        spl     1,      <400
        spl     1,      <500
p1      spl     @0,     >5619
        mov     }p1,    >p1
p2      spl     @0,     >2638
        mov     }p2,    >p2
p3      spl     @0,     >1032
        mov     }p3,    >p3
        mov.i   bmb,    }2167
        mov.i   bmb,    {2024
        jmp     p1,     >2846
bmb     dat     <5334,  <2667
