;redcode-94
;name Sickle Moon
;author anon
;strategy mod-20 0.5c scanner, spl carpet, d-clear; booted away from a spl decoy field
;assert CORESIZE==8000
step    equ 6740
away    equ 424
        org boot
ptr     dat.f  0, 5235
top     mov.i  inc, >ptr
scan    seq.i  2*step, 2*step+10
        mov.ab scan, ptr
        add.f  inc, scan
        jmn.b  top, ptr
inc     spl.i  #step, >step
        mov.i  db, >ptr
        djn.f  -1, >ptr
db      dat.f  <2667, db-ptr-1
boot    mov.i  {bsrc, <bdst
        mov.i  {bsrc, <bdst
        mov.i  {bsrc, <bdst
        mov.i  {bsrc, <bdst
        mov.i  {bsrc, <bdst
        mov.i  {bsrc, <bdst
        mov.i  {bsrc, <bdst
        mov.i  {bsrc, <bdst
        mov.i  {bsrc, <bdst
        mov.i  {bsrc, <bdst
        jmp    @bjmp, 0
bsrc    dat.f  ptr+10, 0
bdst    dat.f  0, inc+1+away
bjmp    dat.f  0, scan+away
        spl.b  #1, 1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.a  #1, *1
        spl.i  #1, #1
        spl.b  #1, 1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.a  #1, *1
        spl.i  #1, #1
        spl.b  #1, 1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.a  #1, *1
        spl.i  #1, #1
        spl.b  #1, 1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.a  #1, *1
        spl.i  #1, #1
        spl.b  #1, 1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.a  #1, *1
        spl.i  #1, #1
        spl.b  #1, 1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.a  #1, *1
        spl.i  #1, #1
        spl.b  #1, 1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.a  #1, *1
        spl.i  #1, #1
        spl.b  #1, 1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.a  #1, *1
        spl.i  #1, #1
        spl.b  #1, 1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.a  #1, *1
        spl.i  #1, #1
        spl.b  #1, 1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.a  #1, *1
        spl.i  #1, #1
        spl.b  #1, 1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.a  #1, *1
        spl.i  #1, #1
