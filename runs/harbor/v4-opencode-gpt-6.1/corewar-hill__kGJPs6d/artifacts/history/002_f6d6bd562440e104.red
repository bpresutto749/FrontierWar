;redcode-94
;name Lattice Wake 1
;author OpenAI
;strategy Twelve-process replication with three independently moving bomb streams
;assert CORESIZE == 8000
org start
start spl 1
      mov.i -1, 0
      spl 1
      spl 1
p1    spl @0, 1739
      mov.i }p1, >p1
      mov.i venom, >1971
p2    spl @0, 3067
      mov.i }p2, >p2
      mov.i venom, }-1431
      mov.i venom, >4223
      mov.i {p2, <p3
p3    jmp @0, 4217
venom dat.f <2667, <5334
      dat.f 0, 0
      dat.f 0, 0
end start