;redcode-94
;name Lamplighter Fold
;author anon
;strategy p-space scored choice between a .66c oneshot scanner and a silk paper
;assert CORESIZE==8000
        org  think
PS      equ  211
step    equ  3364
gap     equ  2
res     dat     0,      0
st      dat     0,      0
v0      dat     0,      0
v1      dat     0,      0
v2      dat     0,      0
ch      dat     0,      0
tp      dat     0,      tbl-tp
vp      dat     0,      v0-vp
pc      dat     0,      0
        dat     0,      0
tbl     dat     0,      -1
        dat     0,      2
        dat     0,      0
think   ldp.ab  #0,     res
        ldp.ab  #PS,    st
        ldp.ab  #PS+1,  v0
        ldp.ab  #PS+2,  v1
        ldp.ab  #PS+3,  v2
        add.b   res,    tp
        add.b   st,     vp
        add.b   @tp,    @vp
        stp.b   v0,     #PS+1
        stp.b   v1,     #PS+2
        stp.b   v2,     #PS+3
        add.ab  #4000,  v0
        add.ab  #4000,  v1
        add.ab  #4000,  v2
        mov.b   st,     ch
        mov.b   st,     pc
        add.ab  #v0-pc, pc
        slt.b   @pc,    v0
        jmp     n1
        mov.ab  #0,     ch
        mov.ab  #v0-pc, pc
n1      slt.b   @pc,    v1
        jmp     n2
        mov.ab  #1,     ch
        mov.ab  #v1-pc, pc
n2      slt.b   @pc,    v2
        jmp     n3
        mov.ab  #2,     ch
n3      stp.b   ch,     #PS
        jmz.b   loop,   ch
        djn.b   stone,  ch
        jmp     start
start   spl  1,      <-200
        spl  1,      <-300
        spl  1,      <-400
s1      spl  @0,     <1830
        mov.i }-1,   >-1
s2      spl  @0,     <3740
        mov.i }-1,   >-1
s3      spl  @0,     <5420
        mov.i }-1,   >-1
        mov.i pbmb,  >2341
pbmb    dat  >2667,  >5334
stone   mov.i   }sbs,   >sbd
        djn     stone,  #5
        jmp     stn+3000
sbs     dat     stn-sbs, 0
sbd     dat     0,      stn+3000-sbd
stn     spl  #0,     <-100
sloop   mov.i sbmb,  @sptr
sptr    add.ab #3044, #3044
        djn.f sloop,  <-200
sbmb    dat  >-1,    >1
loop    add.f  inc,   scan
scan    sne.i  0,     gap
        jmp    loop
found   mov.a  scan,  tmp
        add.a  #69,   tmp
        slt.a  #85,   tmp
        jmp    loop
        mov.ab scan,  scan
cl1     mov.i  sb,    >scan
        mov.i  sb,    >scan
        djn    cl1,   #3992
cl2     mov.i  db,    >scan
        mov.i  db,    >scan
        jmp    cl2
sb      spl    #0,    17
db      dat    0,     17
inc     dat    step,  step
tmp     dat    0,     0
        end
