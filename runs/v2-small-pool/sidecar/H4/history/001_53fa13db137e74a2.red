;redcode-94
;name Granite
;author anon
;strategy mod-4 stone, spl+dat bombs, then dat clear
;assert CORESIZE==8000
step    equ    3044
        org    loop
loop    add.f  incr,  ptr
        mov.i  sbomb, *ptr
        mov.i  dbomb, @ptr
        djn.b  loop,  #1000
clr     mov.i  dbomb, >ptr
        djn.f  clr,   >ptr
ptr     dat    #step-2, #2*step-2
incr    dat    #2*step, #2*step
sbomb   spl    #0,    #0
dbomb   dat    #0,    #0
