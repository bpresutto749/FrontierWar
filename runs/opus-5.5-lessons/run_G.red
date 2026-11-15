;redcode-94
;name Lynx Folding
;author anon
;strategy p-space switch between a pair scanner and a silk paper
;assert CORESIZE==8000
S       equ  3288
D       equ  2
PC      equ  37
gate    dat  0, inc+1-gate
ptr     dat  0, 4000
sbmb    spl  #0, 0
top     mov.i sbmb, >ptr
lp      add.f inc, sc
sc      seq.i S, S+D
        mov.ab sc, ptr
        jmn.a top, sc
clr     spl  #0, 0
        mov.i cbmb, >gate
        djn.f -1, >gate
cbmb    dat  <2667, inc+1-gate
inc     dat  S, S
        dat  0, 0
        dat  0, 0
        dat  0, 0
pap     spl  1, 0
        spl  1, 0
        spl  1, 0
s1      spl  @0, >2758
        mov.i }s1, >s1
s2      spl  1307, #0
        mov.i >s2, }s2
s3      spl  @0, >1704
        mov.i }s3, >s3
        mov.i <2667, <5334
        jmp  -1, <-2667
think   ldp.ab #0, res
        ldp.ab #37, st
        jmz.b  tog, res
        seq.ab #2, res
        jmp    ok
        jmz.b  ok, st
tog     add.ab #1, st
ok      mod.ab #2, st
        stp.b  st, #37
        jmz.b  lp, st
        jmp    pap
res     dat  0, 0
st      dat  0, 0
        end  think
