;redcode-94
;name Lantern
;author Bart
;strategy 0.5c seq scanner, spl carpet on hits, then self-skipping clear
;assert CORESIZE==8000
        org loop
p       dat    0, 12
loop    mov.i  sb, >p
s       seq.i  4260, 4271
        mov.ab s, p
        add.f  inc, s
        jmn.a  loop, s
cl      spl    #0, 0
        mov.i  db, >p
        djn.f  -1, >p
inc     dat    #4260, #4260
sb      spl    #0, 12
db      dat    0, 12
        end
