;redcode-94
;name Toggle2
;author anon
;strategy p-space bandit: stone vs paper, pick lower decayed loss estimate
;assert CORESIZE==8000
step    equ 3044
BD      equ 4000
        org think
think   ldp.ab  #0, res
        ldp.ab  #1, cur
        ldp.ab  #2, b0
        ldp.ab  #3, b1
res     jmz.b   lost, #0
        seq.ab  #2, res
        jmp     upd
        mov.ab  #16, pen
        jmp     upd
lost    mov.ab  #24, pen
upd     mov.b   cur, cur
cur     jmz.b   upd0, #0
        mov.b   b1, tmp
        div.ab  #4, tmp
        sub.b   tmp, b1
        add.b   pen, b1
        jmp     choose
upd0    mov.b   b0, tmp
        div.ab  #4, tmp
        sub.b   tmp, b0
        add.b   pen, b0
choose  stp.b   b0, #2
        stp.b   b1, #3
        slt.b   b1, b0
        jmp     gost
        stp.ab  #1, #1
        jmp     paper
gost    stp.ab  #0, #1
        mov.i   stone, stone+BD
        mov.i   stone+1, stone+BD+1
        mov.i   stone+2, stone+BD+2
        mov.i   stone+3, stone+BD+3
        mov.i   stone+4, stone+BD+4
        jmp     stone+BD
b0      dat     0, 0
b1      dat     0, 0
tmp     dat     0, 0
pen     dat     0, 0
        for 4
        dat 0,0
        rof
stone   spl  #0, <-30
loop    mov.i bmb, @ptr
ptr     add.ab #step, #step
        jmp  loop, <-40
bmb     dat  >-1, >1
        for 6
        dat 0,0
        rof
paper   spl  1
        spl  1
        spl  1
        spl  1
s1      spl  @0, }3620
        mov.i }-1, >-1
s2      spl  @0, }2512
        mov.i }-1, >-1
        mov.i pbmb, >1234
        mov.i pbmb, >3333
        jmp  s1
pbmb    dat  <2667, <5334
