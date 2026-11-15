;redcode-94
;name Lamplighter
;author anon
;strategy .66c scan, then spl/dat two-pass self-skipping clear
;assert CORESIZE==8000
        org  loop
step    equ  3364
gap     equ  2
loop    add.f  inc,   scan
scan    sne.i  0,     gap
        jmp    loop
found   mov.ab scan,  scan
cl1     mov.i  sb,    >scan
        djn    cl1,   #7990
cl2     mov.i  db,    >scan
        jmp    cl2
sb      spl    #0,    11
        dat    0,     0
db      dat    0,     11
inc     dat    step,  step
        end
