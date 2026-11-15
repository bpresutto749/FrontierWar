;redcode-94
;name Windlass
;author OpenAI
;assert CORESIZE == 8000
org qs
qs
 sne.i qs+413, qs+520
 seq.i qs+4413, qs+4520
 jmp qd0
 sne.i qs+995, qs+1102
 seq.i qs+4995, qs+5102
 jmp qd1
 sne.i qs+1577, qs+1684
 seq.i qs+5577, qs+5684
 jmp qd2
 sne.i qs+2159, qs+2266
 seq.i qs+6159, qs+6266
 jmp qd3
 sne.i qs+2741, qs+2848
 seq.i qs+6741, qs+6848
 jmp qd4
 sne.i qs+3323, qs+3430
 seq.i qs+7323, qs+7430
 jmp qd5
 jmp start
qd5 add.f qstep,qp
qd4 add.f qstep,qp
qd3 add.f qstep,qp
qd2 add.f qstep,qp
qd1 add.f qstep,qp
qd0 sne.i *qp,@qp
 add.f qhalf,qp
 jmn.f qaim,*qp
 mov.ba qp,qp
qaim mov.ab qp,qp
 add.ab #5,qp
qloop mov.i qb,*qp
 mov.i qb,@qp
 add.f qdec,qp
 djn.b qloop,#8
 jmp start
qp dat 413-(qp-qs),520-(qp-qs)
qstep dat 582,582
qhalf dat 4000,4000
qdec dat -11,-11
qb dat <2667,<5334
start spl 1
 spl 1
 spl 1
p1 spl @0, >4485
 mov.i }p1, >p1
p2 spl @0, >5148
 mov.i }p2, >p2
 mov.i #1, <1
 mov.i <5022, }4261
 mov.i {p2, <p3
p3 djn.f @0, >5916


end qs
