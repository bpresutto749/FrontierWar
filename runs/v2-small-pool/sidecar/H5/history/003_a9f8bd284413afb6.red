;redcode-94
;name Origami Switch
;author Barthelemy Presutto
;strategy p-space switch between silk paper and stone
;assert CORESIZE==8000
        org     think
res     dat     0, 0
st      dat     0, 0
think   ldp.ab  #0, res
        ldp.ab  #37, st
        jmn.b   nosw, res
        add.ab  #1, st
nosw    stp.b   st, #37
        mov.i   res, nosw
        mod.ab  #2, st
        jmz.b   start, st
        mov.i   loop, loop+4000
        mov.i   loop+1, loop+4000+1
        mov.i   loop+2, loop+4000+2
        mov.i   loop+3, loop+4000+3
        jmp     loop+4000
start   spl     1
        spl     1
        spl     1
p1      spl     @0, }3620
        mov.i   }p1, >p1
p2      spl     @0, }2368
        mov.i   }p2, >p2
p3      spl     @0, }5512
        mov.i   }p3, >p3
p4      spl     @0, }1440
        mov.i   }p4, >p4
        mov.i   #1, <1
        djn.f   p1, <2667
loop    add.ab  #3364, ptr
        mov.i   bmb, @ptr
ptr     jmp     loop, #0
bmb     dat     >-1, >1
        end

