;redcode-94
;name Stone1
;author Bart
;assert CORESIZE==8000
step    equ 3044
        org start
start   add #step, ptr
        mov bomb, @ptr
        jmp start
ptr     dat 0, 0
bomb    dat >1, >1
