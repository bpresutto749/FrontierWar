;redcode-94
;name Ply Eye Bandit
;author anon
;strategy p-space bandit: explore silk paper and oneshot scanner, then keep the better
;assert CORESIZE==8000
        org pstart
start   spl 1, <300
        spl 1, <150
        spl 1, <450
silk1   spl @0, }6596
        mov.i }silk1, >silk1
silk2   spl @0, }1625
        mov.i }silk2, >silk2
silk3   spl @0, }871
        mov.i }silk3, >silk3
silk4   spl @0, }3758
        mov.i }silk4, >silk4
silk5   spl @0, }2585
        mov.i }silk5, >silk5
silk6   spl @0, }1261
        mov.i }silk6, >silk6
        mov.i {silk1, <silkj
silkj   jmp @0, >842
bmb     dat <2667, <5334
pstart  ldp.ab #5,    ch
        jmn.b  decided, ch
        ldp.ab #0,    res
        ldp.ab #2,    cnt
        jmz.b  first, cnt
        mov.b  res,   tp
        add.ab #tbl-tp, tp
        mov.b  @tp,   pts
        mov.b  cnt,   arm
        mod.ab #2,    arm
        jmn.b  a1,    arm
        ldp.ab #3,    s0
        add.b  pts,   s0
st1     stp.b  s0,    #3
        jmp    first
a1      ldp.ab #4,    s1
        add.b  pts,   s1
st2     stp.b  s1,    #4
first   add.ab #1,    cnt
st3     stp.b  cnt,   #2
        slt.ab #8,   cnt
        jmp    explore
        ldp.ab #3,    s0
        ldp.ab #4,    s1
        mov.ab #1,    ch
        slt.b  s0,    s1
        jmp    sv
        mov.ab #2,    ch
sv
st4     stp.b  ch,    #5
decided mov.ab #0,    arm
        seq.ab #2,    ch
        jmp    launch
        mov.ab #1,    arm
        jmp    launch
explore mov.b  cnt,   arm
        mod.ab #2,    arm
launch  mov.i  zz,    st1
        mov.i  zz,    st2
        mov.i  zz,    st3
        mov.i  zz,    st4
        jmz.b  start, arm
        jmp    scan
zz      dat    #0, #0
ch      dat    #0, #0
res     dat    #0, #0
arm     dat    #0, #0
cnt     dat    #0, #0
s0      dat    #0, #0
s1      dat    #0, #0
tp      dat    #0, #0
pts     dat    #0, #0
tbl     dat    #0, #0
        dat    #0, #3
        dat    #0, #1
step    equ    10
n       equ    (last+1-scan)
scan    add.f  inc,   ptr
ptr     sne.i  n+4,   n+4004
        djn.b  scan,  #(4000-n-16)/step
found   mov.ab ptr,   cp
        add.ab #(ptr-cp)-4, cp
        mov.ab #(scan-cp), cnt2
        sub.b  cp,    cnt2
sp      mov.i  sbmb,  >cp
        djn.b  sp,    cnt2
        mov.ab #(last+2-cp), cp
dp      mov.i  dbmb,  >cp
        djn.b  dp,    #8000-n-3
        jmp    found
cp      dat    #0,    #0
cnt2    dat    #0,    #0
inc     dat    #step, #step
sbmb    spl    #0,    #0
last
dbmb    dat    #0,    #0
