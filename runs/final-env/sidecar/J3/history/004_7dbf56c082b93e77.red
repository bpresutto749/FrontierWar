;redcode-94
;name Flint5
;author anon
;assert CORESIZE==8000
step    equ 3044
BD      equ 5900
        org boot
boot    mov.i   stone, stone+BD
        mov.i   stone+1, stone+BD+1
        mov.i   stone+2, stone+BD+2
        mov.i   stone+3, stone+BD+3
        mov.i   stone+4, stone+BD+4
        jmp     stone+BD
stone   spl  #0, <-30
loop    mov.i bmb, @ptr
ptr     add.ab #step, #step
        jmp  loop, <-40
bmb     dat  >-1, >1
