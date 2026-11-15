;redcode-94
;name Pebble
;author me
;assert CORESIZE==8000
step    equ 2791
        org loop
gate    dat    0, 9
loop    add.ab #step, ptr
ptr     mov    sbomb, 200
        djn    loop, #1600
clr     spl    #0, 0
        mov    bmb, >gate
        djn.f  clr+1, >gate
bmb     dat    0, 9
sbomb   spl    #0, 0
