;redcode-94
;name H7
;author me
;assert CORESIZE==8000
        org     start
start   spl     1
        spl     1
        spl     1
silk0   spl     @0,     >5432
        mov.i   }silk0, >silk0
silk1   spl     @0,     >2345
        mov.i   }silk1, >silk1
silk2   spl     @0,     >1234
        mov.i   }silk2, >silk2
        mov.i   pbomb,  <1001
        mov.i   pbomb,  <3003
pbomb   dat     <2667,  <5334
