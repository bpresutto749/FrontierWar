;redcode-94
;name Tri-Switch
;author anon
;strategy p-space: explore three strategies round-robin, then commit to the best scorer
;strategy strategies: booted forward-clear oneshot, booted backward-clear oneshot, silk paper
        org   sel
sel     ldp.ab  #0,   res
        ldp.ab  #1,   cnt
        ldp.ab  #2,   cur
        mov.b   cur,  idx
        add.ab  #3,   idx
        ldp.b   idx,  sc
        sne.ab  #1,   res
        add.ab  #3,   sc
        sne.ab  #2,   res
        add.ab  #1,   sc
        stp.b   sc,   idx
        add.ab  #1,   cnt
        stp.b   cnt,  #1
        slt.ab  #15,  cnt
        jmp     explr, 0
        ldp.ab  #3,   s0
        ldp.ab  #4,   s1
        ldp.ab  #5,   s2
        mov.ab  #0,   cur
        mov.b   s0,   bv
        slt.b   bv,   s1
        jmp     c2,   0
        mov.ab  #1,   cur
        mov.b   s1,   bv
c2      slt.b   bv,   s2
        jmp     go,   0
        mov.ab  #2,   cur
        jmp     go,   0
explr   mov.b   cnt,  cur
        sub.ab  #1,   cur
        mod.ab  #3,   cur
go      stp.b   cur,  #2
        jmz.b   boota, cur
        sne.ab  #1,   cur
        jmp     bootb, 0
        jmp     pgo,  0
res     dat     0,    0
cnt     dat     0,    0
cur     dat     0,    0
idx     dat     0,    0
sc      dat     0,    0
s0      dat     0,    0
s1      dat     0,    0
s2      dat     0,    0
bv      dat     0,    0
pgo     spl  1,     0
        spl  1,     0
        spl  1,     0
p1      spl  @0,    3620
        mov.i }p1,  >p1
p2      spl  @0,    -1850
        mov.i }p2,  >p2
        mov.i pbmb, >2667
        mov.i {p2,  <p2
        jmp   p1,   0
pbmb    dat   >2667, >5334
boota   mov.i  gatea+0, gatea+5353
        mov.i  gatea+1, gatea+5354
        mov.i  gatea+2, gatea+5355
        mov.i  gatea+3, gatea+5356
        mov.i  gatea+4, gatea+5357
        mov.i  gatea+5, gatea+5358
        mov.i  gatea+6, gatea+5359
        mov.i  gatea+7, gatea+5360
        jmp    scana+5353, 0
gatea   dat   0,     0
scana   add.ab #-2664,  gatea
        jmz.f  scana, @gatea
        sub.ab #12,  gatea
        spl    #0,   0
mva     mov.i  bomba, >gatea
        djn.f  mva,  >gatea
bomba   dat    0,    bomba-gatea
bootb   mov.i  scanb+0, scanb+2577
        mov.i  scanb+1, scanb+2578
        mov.i  scanb+2, scanb+2579
        mov.i  scanb+3, scanb+2580
        mov.i  scanb+4, scanb+2581
        mov.i  scanb+5, scanb+2582
        mov.i  scanb+6, scanb+2583
        mov.i  scanb+7, scanb+2584
        jmp    scanb+2577, 0
scanb   add.ab #2664,  gateb
        jmz.f  scanb, @gateb
        add.ab #13,  gateb
        spl    #0,   0
mvb     mov.i  bombb, <gateb
        djn.f  mvb,  <gateb
bombb   dat    0,    -8
gateb   dat    0,    0
