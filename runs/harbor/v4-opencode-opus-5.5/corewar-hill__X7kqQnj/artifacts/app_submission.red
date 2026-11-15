;redcode-94
;name Glance
;author me
;assert CORESIZE==8000
st      equ 32
d       equ 16
        org loop
gate    dat    0, 0
inc     dat    st, st
loop    add.f  inc, sc
sc      sne.i  100, 100+d
        djn    loop, #243
        mov.ab sc, gate
clr     spl    #0, 0
        mov    bmb, >gate
        djn.f  clr+1, >gate
bmb     dat    0, 11
