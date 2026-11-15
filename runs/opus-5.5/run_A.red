;redcode-94
;name Carpet Weaver
;author anon
;strategy 0.5c seq scanner laying a spl carpet from each hit, then backward dat clear
;assert CORESIZE==8000

step    equ     5870
gap     equ     5

incr    dat     step,   step
ptr     dat     0,      -3000
sb      spl     #0,     0
top     mov.i   sb,     >ptr
scan    seq.i   step,   step+gap
        mov.ab  scan,   ptr
        add.f   incr,   scan
        jmn.a   top,    scan
clr     spl     #0,     0
cl      mov.i   cb,     <gate
        jmp     cl
        dat     0,      0
gate    dat     0,      incr-gate
cb      dat     <2667,  incr-gate
end top
