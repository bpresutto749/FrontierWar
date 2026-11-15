;redcode-94
;name pb4
;author arena
;strategy three-stage silk replicator
        org start
start   spl    1
        spl    1
        spl    1
        spl    1
s1      spl    @0, 3620
        mov.i  }s1, >s1
s2      spl    @0, 5250
        mov.i  }s2, >s2
s3      spl    @0, 1820
        mov.i  }s3, >s3
        mov.i  bmb, }1777
        mov.i  bmb, >-2311
        mov.i  bmb, }3001
        djn.f  -3, <-1200
bmb     dat    <2667, <5334
