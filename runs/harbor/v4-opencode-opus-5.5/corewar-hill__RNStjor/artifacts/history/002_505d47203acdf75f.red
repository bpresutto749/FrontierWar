;redcode-94
;name Pebble Spiral
;author opencode
;assert CORESIZE==8000
step    equ    3044
ist     equ    2667
        spl    stone
        spl    1
        spl    1
        spl    2
        jmp    @0,    imp
        add    #ist,  -1
        dat    0,     0
stone   spl    #0,    <-step
loop    mov    bomb,  @ptr
ptr     add    #step, #step
        djn.f  loop,  <-1000
bomb    dat    >-1,   >1
imp     mov.i  #0,    ist
        end
