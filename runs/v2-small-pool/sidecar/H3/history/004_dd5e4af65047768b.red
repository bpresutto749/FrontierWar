;redcode-94
;name Tri-Switch II
;author anon
;strategy p-space: explore three strategies round-robin, then commit to the best scorer
;strategy strategies: booted forward-clear oneshot, booted spl-stun scanner, silk paper
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
        sne.ab  #0,   res
        sub.ab  #0,  sc
        slt.ab  #4000, sc
        jmp     okk,  0
        mov.ab  #0,   sc
okk     stp.b   sc,   idx
        add.ab  #1,   cnt
        stp.b   cnt,  #1
        slt.ab  #30,  cnt
        jmp     explr, 0
        ldp.ab  #3,   s0
        ldp.ab  #4,   s1
        ldp.ab  #5,   s2
        mov.ab  #0,   cur
        slt.b   s0,   s1
        jmp     c2,   0
        mov.ab  #1,   cur
        mov.b   s1,   s0
c2      slt.b   s0,   s2
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
boota   mov.i  }bpa, >bpa
        djn.b  boota, #8
        jmp    scana+5354, 0
bpa     dat    gatea-bpa, gatea+5354-bpa
gatea   dat   0,     0
scana   add.ab #-2664,  gatea
        jmz.f  scana, @gatea
        sub.ab #24,  gatea
        spl    #0,   0
mva     mov.i  bomba, >gatea
        djn.f  mva,  >gatea
bomba   dat    0,    bomba-gatea
bootb   mov.i  }bpb, >bpb
        djn.b  bootb, #14
        jmp    scanb+2590, 0
bpb     dat    gateb-bpb, gateb+2590-bpb
gateb   dat    0,     0
scanb   add.ab #2664,  gateb
        jmz.f  scanb,  @gateb
        mov.i  sbombb, >gateb
        mov.i  sbombb, >gateb
        mov.i  sbombb, @gateb
        sub.ab #2,    gateb
        djn.b  scanb,  #16
        sub.ab #12,   gateb
        spl    #0,    0
mvb     mov.i  dbombb, >gateb
        djn.f  mvb,    >gateb
dbombb  dat    0,     dbombb-gateb+1
sbombb  spl    #0,    0
