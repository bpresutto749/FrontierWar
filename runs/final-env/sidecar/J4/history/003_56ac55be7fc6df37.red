;redcode-94
;name P
;author me
;assert CORESIZE==8000
        org     start
start   spl     1
        spl     1
        spl     1
silk    spl     @0,     >5432
        mov.i   }silk,  >silk
silk2   spl     @0,     >2345
        mov.i   }silk2, >silk2
silk3   spl     @0,     >1234
        mov.i   }silk3, >silk3
        mov.i   pbomb,  <1001
        mov.i   pbomb,  <3003
        jmp     silk
pbomb   dat     <2667,  <5334
