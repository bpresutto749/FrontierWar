;redcode-94
;name SW2
;author me
;assert CORESIZE==8000
PC      equ     37
step    equ     3364
sstep   equ     3364
        org     think
think   ldp.ab  #0,     res
        ldp.ab  #PC,    sel
        jmn.b   keep,   res
        add.ab  #1,     sel
keep    mod.ab  #2,     sel
        stp.b   sel,    #PC
        add.b   sel,    jptr
        jmp     @jptr
res     dat     0,      0
sel     dat     0,      0
jptr    dat     0,      tab
tab     jmp     pstart
        jmp     loop

pstart  spl     1
        spl     1
        spl     1
silk    spl     @0,     >3620
        mov.i   }silk,  >silk
silk2   spl     @0,     >1240
        mov.i   }silk2, >silk2
        mov.i   pbomb,  >2000
        mov.i   pbomb,  >2000
        jmp     silk
pbomb   dat     >2667,  >5334

loop    add.f   inc,    sptr
        mov.i   bomb,   @sptr
        mov.i   bomb,   *sptr
        jmp     loop,   <-50
sptr    dat     #sstep, #sstep*2
inc     dat     #sstep*2,#sstep*2
bomb    dat     >1,     >1
