;redcode-94
;name Lantern
;author opencode
;strategy oneshot scanner into d-clear
;assert CORESIZE==8000
step    equ     3082
half    equ     200
        org     top
gate    dat     0,      0
top     add.f   inc,    ptr
ptr     seq.i   3102,  3102+half
        jmp     found
        jmp     top
found   mov.ab  ptr,    gate
        add.ab  #-6,    gate
clr     spl     #0,     0
        mov     bmb,    >gate
        djn.f   -1,     >gate
bmb     dat     <2667,  12
inc     dat     step,   step
        end
