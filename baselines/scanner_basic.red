;redcode-94
;name BasicScanner
;assert CORESIZE==8000
step    equ 3364
scan    add.f inc, ptr
ptr     sne.i 100, 104
        jmp scan
        mov.i bomb, @ptr
        mov.i bomb, *ptr
        jmp scan
inc     dat #step, #step
bomb    dat #0, #0
