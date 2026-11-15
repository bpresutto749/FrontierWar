;redcode-94
;name Lattice Wake
;author OpenAI
;strategy Sixteen-process replication, three bomb streams, and a mutating reverse-copy handoff
;assert CORESIZE == 8000
org start
start spl 1
      spl 1
      spl 1
      spl 1
p1    spl @0, 1739
      mov.i }p1, >p1
      mov.i venom, >1971
      mov.i venom, }-1431
p2    spl @0, 3067
      mov.i }p2, >p2
      mov.i venom, >4239
      mov.i {p2, <p3
p3    jmp @0, <4217
venom dat.f <2667, <5334
      dat.f 0, 0
      dat.f 0, 0
      dat.f 0, 0
      dat.f 0, 0
      dat.f 0, 0
      dat.f 0, 0
end start
