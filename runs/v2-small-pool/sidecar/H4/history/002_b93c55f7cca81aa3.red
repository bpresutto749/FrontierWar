;redcode-94
;name Ply
;author anon
;strategy silk paper
;assert CORESIZE==8000
        org    start
start   spl    1,     <300
        spl    1,     <150
        spl    1,     <450
silk1   spl    @0,    }3620
        mov.i  }silk1, >silk1
silk2   spl    @0,    }1876
        mov.i  }silk2, >silk2
        mov.i  bmb,   }2367
        mov.i  bmb,   }-1033
        mov.i  {silk1, <silk3
silk3   jmp    @0,    >5143
bmb     dat    <2667, <5334
