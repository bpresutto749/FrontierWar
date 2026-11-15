;redcode-94
;name Folded Crane
;author opencode
;strategy silk-style replicating paper with bombing
;assert CORESIZE==8000
        spl     1
        spl     1
        spl     1
p1      spl     @0,     }3359
        mov.i   }p1,    >p1
p2      spl     @0,     }5243
        mov.i   }p2,    >p2
        mov.i   bmb,    >1617
        mov.i   bmb,    }2711
        mov.i   {p2,    <p3
p3      jmp     @0,     >1003
bmb     dat     <2667,  <5334
        end
