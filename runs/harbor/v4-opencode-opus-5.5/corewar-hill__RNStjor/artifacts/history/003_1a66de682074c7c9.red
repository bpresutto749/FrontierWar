;redcode-94
;name Paper Pebble Spiral
;assert CORESIZE==8000
step    equ 7019
ist     equ 2667
start   spl    paper
        spl 1
        spl 1
        spl 1

tbst    spl    stone
        spl    1
        spl    1
        spl    2
        jmp    @0,    imp
        add    #ist,  -1
        dat    0,     0
stone   spl    #0,    0
lp      mov    sb,  *p
        mov    sb,  @p
        add.f  inc,   p
        djn.f  lp,    <-1000
p       dat    step,  step*2
inc     dat    step*2, step*2
sb      dat    >-1,   >1
imp     mov.i  #0,    ist
        dat 0,0
        dat 0,0
        dat 0,0
paper   spl 1, 0
        spl 1, 0
        spl 1, 0
s1      spl @0, <3728
        mov.i }-1, >-1
s2      spl @0, <5430
        mov.i }-1, >-1
s3      spl @0, <3423
        mov.i }-1, >-1
        mov.i bmb, }2667
        mov.i bmb, >764
        mov.i {-8, <1
        jmz.a @0, }-9
bmb     dat <2667, <5334
        end start
