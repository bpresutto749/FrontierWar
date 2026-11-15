;redcode-94
;name Windlass
;author OpenAI
;assert CORESIZE == 8000
org qs
qs
 sne.i qs+359, qs+582
 seq.i qs+4359, qs+4582
 jmp qd0
 sne.i qs+966, qs+1189
 seq.i qs+4966, qs+5189
 jmp qd1
 sne.i qs+1573, qs+1796
 seq.i qs+5573, qs+5796
 jmp qd2
 sne.i qs+2180, qs+2403
 seq.i qs+6180, qs+6403
 jmp qd3
 sne.i qs+2787, qs+3010
 seq.i qs+6787, qs+7010
 jmp qd4
 sne.i qs+3394, qs+3617
 seq.i qs+7394, qs+7617
 jmp qd5
 jmp start
qd5 add.f qstep,qp
qd4 add.f qstep,qp
qd3 add.f qstep,qp
qd2 add.f qstep,qp
qd1 add.f qstep,qp
qd0 sne.i *qp,@qp
 add.f qhalf,qp
qloop mov.i qb,*qp
 mov.i qb,@qp
 add.f qdec,qp
 djn.b qloop,#8
 jmp start
qp dat 359-(qp-qs),582-(qp-qs)
qstep dat 607,607
qhalf dat 4000,4000
qdec dat -11,-11
qb dat <2667,<5334
start spl 1
 spl 1
 spl 1
p1 spl @0, >1638
 mov.i }p1, >p1
 mov.i #1, <1
p2 spl @0, >3497
 mov.i }p2, >p2
 mov.i >2060, >6770
 mov.i {p2, <p3
p3 djn.f @0, >1330


end qs
