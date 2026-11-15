;redcode-94
;name Flint2
;author anon
;assert CORESIZE==8000
step    equ 3044
        org stone
stone   spl  #0, <-30
loop    mov.i bmb, @ptr
ptr     add.ab #step, #step
        jmp  loop, <-40
bmb     dat  >-1, >1
