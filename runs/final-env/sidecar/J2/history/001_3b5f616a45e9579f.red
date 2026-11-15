;redcode-94
;name Silkworm A
;author anon
;strategy silk paper
;assert CORESIZE==8000
        org     start
start   spl     1,      0
        spl     1,      0
        spl     1,      0
s1      spl     @0,     }3620
        mov.i   }s1,    >s1
s2      spl     @0,     }1820
        mov.i   }s2,    >s2
        mov.i   bomb,   }2340
        mov.i   bomb,   }4140
        jmz.a   s1,     #0
bomb    dat     >2667,  >5334
        end
