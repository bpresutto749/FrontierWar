;redcode-94
;name Flint
;author anon
;strategy dat stone + imp spiral
;assert CORESIZE==8000
step    equ 3044
istep   equ 2667
        org boot
boot    spl  stone
        spl  1
        spl  1
        spl  1
        spl  2
pump    jmp  @vec, }0
        add.a #istep, vec
vec     jmp  imp, 0
imp     mov.i #0, istep
        for 10
        dat 0,0
        rof
stone   spl  #0, <-30
loop    mov.i bmb, @ptr
ptr     add.ab #step, #step
        jmp  loop, <-40
bmb     dat  >-1, >1
