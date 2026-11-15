;redcode-94
;name Lantern Crane
;author opencode
;strategy saturating p-space counter chooses between a silk paper and a oneshot scanner
;assert CORESIZE==8000
        org     start
start   ldp.ab  #0,     r
        ldp.ab  #1,     v
        slt.ab  #2,     v
        jmp     d0
        mov.ab  #1,     dir
d0      seq.ab  #1,     r
        jmp     nw
        add.b   dir,    v
nw      sne.ab  #0,     r
        sub.b   dir,    v
        sne.ab  #7999,  v
        mov.ab  #0,     v
        sne.ab  #6,     v
        mov.ab  #5,     v
st      stp.b   v,      #1
        mov.i   dir+1,    st
        slt.ab  #2,     v
        jmp     p0
        jmp     top
r       dat     0,      0
v       dat     0,      0
dir     dat     0,      -1
        dat     0,      0
step    equ     3082
half    equ     34
gate    dat     0,      0
top     add.f   inc,    ptr
ptr     seq.i   step+20,  step+20+half
        jmp     found
        jmp     top
found   mov.ab  ptr,    gate
        add.ab  #-6,    gate
clr     spl     #0,     0
        mov     bmb,    >gate
        djn.f   -1,     >gate
bmb     dat     <2667,  12
inc     dat     step,   step
p0      spl     1
        spl     1
        spl     1
p1      spl     @0,     }495
        mov.i   }p1,    >p1
p2      spl     @0,     }2736
        mov.i   }p2,    >p2
        mov.i   pb,    >259
        mov.i   pb,    }830
        mov.i   {p2,    <p3
p3      jmp     @0,     >1085
pb      dat     <2667,  <5334
        end

