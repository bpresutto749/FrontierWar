;redcode-94
;name Folded Crane
;author me
;strategy silk paper plus a small stone
;assert CORESIZE==8000
step    equ     1124
        org     start
start   spl     stone
        spl     1,      <300
        spl     1,      <400
        spl     1,      <500
p1      spl     @0,     >3118
        mov     }p1,    >p1
p2      spl     @0,     >290
        mov     }p2,    >p2
p3      spl     @0,     >1368
        mov     }p3,    >p3
        mov.i   bmb,    }6170
        mov.i   bmb,    {6797
        jmp     p1,     >824
bmb     spl     #1,     {1
stone   mov.i   sbm,    @sp
        mov.i   sbm,    *sp
        add.f   sinc,   sp
        jmp     stone
sp      dat     step,   2*step
sinc    dat     2*step, 2*step
sbm     dat     >1,     >1
