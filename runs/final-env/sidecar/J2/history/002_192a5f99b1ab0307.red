;redcode-94
;name Seeker C
;author anon
;strategy 0.66c scanner into dat clear
;assert CORESIZE==8000
step    equ     2823
gap     equ     4
        org     loop
cptr    dat     #0,     #0
inc     dat     #step,  #step
loop    add.f   inc,    ptr
ptr     sne.i   step+gap, step
        jmp     loop
        mov.ab  ptr,    cptr
        add.b   #ptr-cptr, cptr
        slt.ab  #13,    cptr
        jmp     loop
cl      spl     #0,     0
        mov.i   dbomb,  >cptr
        djn.f   -1,     >cptr
dbomb   dat     #0,     #13
        end
