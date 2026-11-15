;redcode-94
;name Sieve Lantern
;author anon
;strategy half-speed pair scanner, spl carpet, then forward dat clear
;strategy booted away from a decoy block
;assert CORESIZE==8000

SS equ 3210
BD equ 3800

wptr    dat.f   0,      SS+5
        dat.f   0,      0
        dat.f   0,      0
        dat.f   0,      0
sbomb   spl.i   #0,     0
lay     mov.i   sbomb,  >wptr
scan    seq.i   2*SS,   }2*SS+5
        mov.b   scan,   wptr
        add.f   inc,    scan
        jmn.a   lay,    scan
inc     spl.a   #SS,    >SS
clr     mov.i   dbomb,  >wptr
        djn.f   clr,    >wptr
dbomb   dat.f   <2667,  dbomb-wptr+2
bptr    dat.f   0,      BD
boot    mov.i   {bptr,  <bptr
    for 14
        mov.i   {bptr,  <bptr
    rof
        jmp     lay+BD
        spl.b  #1,  1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.i  #1, #1
        spl.a  #1, *1
        spl.f  #2,  1
        spl.x  #1, @2
        spl.ab #2, }1
        spl.b  #1,  1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.i  #1, #1
        spl.a  #1, *1
        spl.f  #2,  1
        spl.x  #1, @2
        spl.ab #2, }1
        spl.b  #1,  1
        spl.ab #1, @1
        spl.ba #1, *1
        spl.i  #1, #1
        end     boot
