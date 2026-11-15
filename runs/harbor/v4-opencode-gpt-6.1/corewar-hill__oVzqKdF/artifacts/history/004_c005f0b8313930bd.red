;redcode-94
;name Driftglass
;author OpenAI
;assert CORESIZE == 8000
org qstart
qstart
seq.i qstart+187, qstart+288
mov.ab #qstart+187-qptr, qptr
seq.i qstart+426, qstart+527
mov.ab #qstart+426-qptr, qptr
seq.i qstart+665, qstart+766
mov.ab #qstart+665-qptr, qptr
seq.i qstart+904, qstart+1005
mov.ab #qstart+904-qptr, qptr
seq.i qstart+1143, qstart+1244
mov.ab #qstart+1143-qptr, qptr
seq.i qstart+1382, qstart+1483
mov.ab #qstart+1382-qptr, qptr
seq.i qstart+1621, qstart+1722
mov.ab #qstart+1621-qptr, qptr
seq.i qstart+1860, qstart+1961
mov.ab #qstart+1860-qptr, qptr
jmn.b qhit, qptr
seq.i qstart+2099, qstart+2200
mov.ab #qstart+2099-qptr, qptr
seq.i qstart+2338, qstart+2439
mov.ab #qstart+2338-qptr, qptr
seq.i qstart+2577, qstart+2678
mov.ab #qstart+2577-qptr, qptr
seq.i qstart+2816, qstart+2917
mov.ab #qstart+2816-qptr, qptr
seq.i qstart+3055, qstart+3156
mov.ab #qstart+3055-qptr, qptr
seq.i qstart+3294, qstart+3395
mov.ab #qstart+3294-qptr, qptr
seq.i qstart+3533, qstart+3634
mov.ab #qstart+3533-qptr, qptr
seq.i qstart+3772, qstart+3873
mov.ab #qstart+3772-qptr, qptr
jmn.b qhit, qptr
seq.i qstart+4011, qstart+4112
mov.ab #qstart+4011-qptr, qptr
seq.i qstart+4250, qstart+4351
mov.ab #qstart+4250-qptr, qptr
seq.i qstart+4489, qstart+4590
mov.ab #qstart+4489-qptr, qptr
seq.i qstart+4728, qstart+4829
mov.ab #qstart+4728-qptr, qptr
seq.i qstart+4967, qstart+5068
mov.ab #qstart+4967-qptr, qptr
seq.i qstart+5206, qstart+5307
mov.ab #qstart+5206-qptr, qptr
seq.i qstart+5445, qstart+5546
mov.ab #qstart+5445-qptr, qptr
seq.i qstart+5684, qstart+5785
mov.ab #qstart+5684-qptr, qptr
jmn.b qhit, qptr
seq.i qstart+5923, qstart+6024
mov.ab #qstart+5923-qptr, qptr
seq.i qstart+6162, qstart+6263
mov.ab #qstart+6162-qptr, qptr
seq.i qstart+6401, qstart+6502
mov.ab #qstart+6401-qptr, qptr
seq.i qstart+6640, qstart+6741
mov.ab #qstart+6640-qptr, qptr
seq.i qstart+6879, qstart+6980
mov.ab #qstart+6879-qptr, qptr
seq.i qstart+7118, qstart+7219
mov.ab #qstart+7118-qptr, qptr
seq.i qstart+7357, qstart+7458
mov.ab #qstart+7357-qptr, qptr
seq.i qstart+7596, qstart+7697
mov.ab #qstart+7596-qptr, qptr
jmn.b qhit, qptr
jmp paper
qhit mov.ba qptr, qptr
add.ab #101, qptr
add.f qoffset, qptr
qbomb mov.i qdeath, *qptr
mov.i qdeath, @qptr
add.f qdelta, qptr
djn.b qbomb, #21
jmp paper
qdelta dat -11, -11
qoffset dat 11, 11
qptr dat 0, 0
qdeath dat <2667, <5334
paper spl 1
spl 1
spl 1
spl 1
seed spl @0, 1173
mov.i }seed, >seed
bud spl @0, 3581
mov.i }bud, >bud
mov.i sting, >3958
mov.i sting, }6439
      mov.i {bud, <root
root jmp @0, <4881
sting dat.f <2667, <5334
end
