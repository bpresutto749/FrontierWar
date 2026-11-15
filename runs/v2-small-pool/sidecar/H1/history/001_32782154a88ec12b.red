;redcode-94
;name Gravel
;author Barthelemy Presutto
;strategy mod-4 spl/dat stone with core clear
;assert CORESIZE==8000
step    equ     3044
gate    equ     (start-2)
start   mov.i   sbomb,  @ptr
ptr     mov.i   dbomb,  *step+1
        add.ab  #step,  ptr
        djn.f   start,  <gate
        dat     0,      0
sbomb   spl     #0,     0
dbomb   dat     >-1,    >1
        end     start
