;redcode-94
;name J3
;author me
;assert CORESIZE==8000
        org     go
go      spl     loop
        jmp     pstart
pstart  spl     1
        spl     1
        spl     1
silk0   spl     @0,     >5432
        mov.i   }silk0, >silk0
silk1   spl     @0,     >2345
        mov.i   }silk1, >silk1
silk2   spl     @0,     >1234
        mov.i   }silk2, >silk2
        mov.i   pbomb,  <1001
        mov.i   pbomb,  <3003
pbomb   dat     <2667,  <5334
loop    add.f   inc,    sptr
        mov.i   bomb,   @sptr
        mov.i   bomb,   *sptr
        jmp     loop,   <-50
sptr    dat     #3044,  #3044*2
inc     dat     #3044*2,#3044*2
bomb    dat     >1,     >1
