;redcode-94
;name Driftglass
;author OpenAI
;assert CORESIZE == 8000
org qstart
qstart
seq.i qstart+260, qstart+347
jmp decode0
seq.i qstart+889, qstart+976
jmp decode1
seq.i qstart+1518, qstart+1605
jmp decode2
seq.i qstart+2147, qstart+2234
jmp decode3
seq.i qstart+2776, qstart+2863
jmp decode4
seq.i qstart+3405, qstart+3492
jmp decode5
seq.i qstart+4034, qstart+4121
jmp decode6
seq.i qstart+4663, qstart+4750
jmp decode7
seq.i qstart+5292, qstart+5379
jmp decode8
seq.i qstart+5921, qstart+6008
jmp decode9
seq.i qstart+6550, qstart+6637
jmp decode10
seq.i qstart+7179, qstart+7266
jmp decode11
jmp paper
decode0 mov.ab #qstart+260-qptr, qptr
jmp qhit
decode1 mov.ab #qstart+889-qptr, qptr
jmp qhit
decode2 mov.ab #qstart+1518-qptr, qptr
jmp qhit
decode3 mov.ab #qstart+2147-qptr, qptr
jmp qhit
decode4 mov.ab #qstart+2776-qptr, qptr
jmp qhit
decode5 mov.ab #qstart+3405-qptr, qptr
jmp qhit
decode6 mov.ab #qstart+4034-qptr, qptr
jmp qhit
decode7 mov.ab #qstart+4663-qptr, qptr
jmp qhit
decode8 mov.ab #qstart+5292-qptr, qptr
jmp qhit
decode9 mov.ab #qstart+5921-qptr, qptr
jmp qhit
decode10 mov.ab #qstart+6550-qptr, qptr
jmp qhit
decode11 mov.ab #qstart+7179-qptr, qptr
jmp qhit
qhit mov.ba qptr, qptr
add.ab #87, qptr
add.f qoffset, qptr
qbomb mov.i qdeath, *qptr
mov.i qdeath, @qptr
add.f qdelta, qptr
djn.b qbomb, #21
jmp paper
qdelta dat -7, -7
qoffset dat 0, 0
qptr dat 0,0
qdeath dat <2667,<5334
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
