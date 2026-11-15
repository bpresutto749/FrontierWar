;redcode-94
;name Seeker F
;author anon
;strategy 0.8c scanner into dat clear
;assert CORESIZE==8000
step    equ     2365
gap     equ     10
        org     loop
cptr    dat     #0,     #0
inc     dat     #step,  #step
p       dat     #gap,   #0
loop    add.f   inc,    p
        seq.i   *p,     @p
        jmp     found
        add.f   inc,    p
        seq.i   *p,     @p
        jmp     found
        jmp     loop
found   mov.b   p,      cptr
        add.b   #p-cptr, cptr
        slt.ab  #fin+1-cptr, cptr
        jmp     loop
cl      spl     #0,     0
        mov.i   dbomb,  >cptr
        djn.f   -1,     >cptr
fin
dbomb   dat     #0,     #fin+1-cptr
        end
