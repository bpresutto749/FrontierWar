;redcode-94
;name Folded Lantern
;author opencode
;strategy p-space switch between silk paper and scanner/clear
        org think
STORE   equ 211
think   ldp.ab #0, res
        ldp.ab #STORE, st
res     jmn.b keep, #0
        add #1, st
keep    mod #2, st
        stp.b st, #STORE
st      jmz.b pap, #0
        jmp scan
pap     spl 1
        spl 1
        spl 1
p1      spl @0, }3620
        mov.i }p1, >p1
p2      spl @0, }1545
        mov.i }p2, >p2
        mov.i bmb, }2234
p3      spl @0, }-2000
        mov.i }p3, >p3
        mov.i bmb, }p3+100
        jmp p1, <-50
bmb     dat <2667, <5334
        for 6
        dat 0,0
        rof
step    equ 3359
ptr     dat 0, 3000
scan    add #step, ptr
        jmz.f scan, @ptr
        mov.b ptr, gate
        add #-16, gate
        jmp clr
        for 4
        dat 0,0
        rof
gate    dat 0, 0
clr     spl #0, 0
cl      mov sbmb, >gate
        mov sbmb, >gate
        djn.f cl, >gate
        for 3
        dat 0,0
        rof
sbmb    dat >2667, >5334
