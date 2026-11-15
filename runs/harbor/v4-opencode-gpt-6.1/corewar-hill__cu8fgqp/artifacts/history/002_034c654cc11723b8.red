;redcode-94
;name Saffron Prism
;author OpenAI
;assert CORESIZE == 8000
org qscan
qscan
 seq.i qptr+3670, qptr+3757
 jmp qd0, {qd0
 seq.i qptr+5505, qptr+5592
 jmp qd0, 0
 seq.i qptr+7340, qptr+7427
 jmp qd0, }qd0
 seq.i qptr+430, qptr+517
 jmp qd1, {qd1
 seq.i qptr+1835, qptr+1922
 jmp qd1, 0
 seq.i qptr+3240, qptr+3327
 jmp qd1, }qd1
 seq.i qptr+550, qptr+637
 jmp qd2, {qd2
 seq.i qptr+1405, qptr+1492
 jmp qd2, 0
 seq.i qptr+2260, qptr+2347
 jmp qd2, }qd2
 seq.i qptr+2020, qptr+2107
 jmp qd3, {qd3
 seq.i qptr+855, qptr+942
 jmp qd3, 0
 seq.i qptr+7690, qptr+7777
 jmp qd3, }qd3
 seq.i qptr+4080, qptr+4167
 jmp qd4, {qd4
 seq.i qptr+6835, qptr+6922
 jmp qd4, 0
 seq.i qptr+1590, qptr+1677
 jmp qd4, }qd4
 seq.i qptr+2610, qptr+2697
 jmp qd5, {qd5
 seq.i qptr+2755, qptr+2842
 jmp qd5, 0
 seq.i qptr+2900, qptr+2987
 jmp qd5, }qd5
 jmp start
qd0 mul.ab #3, qptr
qd1 mul.ab #7, qptr
qd2 mul.ab #11, qptr
qd3 mul.ab #13, qptr
qd4 mul.ab #17, qptr
qd5 mul.ab #19, qptr
 mov.ba qptr,qptr
 add.a #87,qptr
 add.f qshift,qptr
qhit mov.i qbomb,@qptr
 mov.i qbomb,*qptr
 add.f qdrift,qptr
 djn.b qhit,#12
 jmp start
qbomb dat <2667,<5334
qdrift dat -7,-7
qshift dat 7,7
qptr dat 0,145
start spl 1
 mov.i -1,0
 mov.i -1,0
 mov.i -1,0
front spl @0,1807
 mov.i }front,>front
 sub.f poison,}3911
rear spl @0,3659
 mov.i }rear,>rear
 mov.i poison,>6241
 mov.i {rear,<leap
leap jmp @0,5213
poison dat <2667,<5334

end qscan
