;redcode-94
;name Lattice Wake 2
;author OpenAI
;strategy Sixteen-process silk lattice with mutating handoff and three bombing trails
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
      mov.i venom, >4223
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