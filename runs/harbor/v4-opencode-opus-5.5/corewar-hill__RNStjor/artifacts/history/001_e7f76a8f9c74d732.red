;redcode-94
;name Pebble Imp
;author opencode
;assert CORESIZE==8000
step    equ    3044
        spl    imp,   0
stone   spl    #0,    <-step
loop    mov    bomb,  @ptr
ptr     add    #step, #step
        djn.f  loop,  <-1000
bomb    dat    >-1,   >1
imp     mov.i  #1,    2667
        end
