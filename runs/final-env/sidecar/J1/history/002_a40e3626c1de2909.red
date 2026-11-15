;redcode-94
;name Ribbon3
;author arena
;strategy three-stage silk replicator, 16 processes

d1      equ 3913
d2      equ 2667
d3      equ 1471
        org start
start   spl    1
        spl    1
        spl    1
        spl    1
s1      spl    @0, d1
        mov.i  }s1, >s1
s2      spl    @0, d2
        mov.i  }s2, >s2
s3      spl    @0, d3
        mov.i  }s3, >s3
        mov.i  bmb, }1777
        mov.i  bmb, >-2311
        mov.i  bmb, }3001
        djn.f  -3, <-1200
bmb     dat    <2667, <5334
