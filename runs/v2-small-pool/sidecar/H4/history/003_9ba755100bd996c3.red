;redcode-94
;name Ply
;author anon
;assert CORESIZE==8000
        org start
start   spl    1,     <300
        spl    1,     <150
        spl    1,     <450
silk1   spl    @0,    }3620
        mov.i  }silk1, >silk1
silk2   spl    @0,    }1876
        mov.i  }silk2, >silk2
silk3   spl    @0,    }5432
        mov.i  }silk3, >silk3
silk4   spl    @0,    }980
        mov.i  }silk4, >silk4
        mov.i  {silk1, <silk5
silk5   jmp    @0,    >5143
bmb     dat    <2667, <5334
