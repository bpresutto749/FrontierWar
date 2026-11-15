;redcode-94
;name Pebble
;author arena
;strategy simple mod-4 stone with spl/dat bombing

step    equ 3044
        org start
start   mov.i  bomb, @ptr
        mov.i  bomb, *ptr
        add.f  inc, ptr
        jmp    start
ptr     dat    #step, #step*2
inc     dat    #step*2, #step*2
bomb    dat    #0, #0
