;redcode-94
;name St
;assert CORESIZE==8000
        org  stone
step    equ  3044
stone   spl  #0,     <-100
loop    mov.i bomb,  @ptr
ptr     add.ab #step, #step
        djn.f loop,  <-200
bomb    dat  >-1,    >1
        end
