;redcode-94
;name Thistledown 0
;author OpenAI
;assert CORESIZE == 8000
org start
start spl 1
      spl 1
      spl 2
      spl 1
p1    spl @0, >1907
      mov.i }p1, >p1
p2    spl @0, >4133
      mov.i }p2, >p2
      mov.i venom, >raid
      mov.i venom, }raid
      add.f stride, raid
      mov.i {p2, <p3
p3    jmp @0, >5699
raid  dat 117, 3901
stride dat 2171, 2387
venom dat <2667, <5334
end start