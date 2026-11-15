;redcode-94
;name Saffron Wake
;author OpenAI
;strategy Two migrating replication fronts with interleaved bombing.
;assert CORESIZE == 8000
org start
start spl 1
      spl 1
      spl 1
      spl 1
front spl @0, 1873
      mov.i }front, >front
      mov.i poison, }spray
      mov.i poison, >spray
rear  spl @0, 3251
      mov.i }rear, >rear
      mov.i poison, >trail
      mov.i {rear, <leap
leap  jmp @0, 5419
poison dat <2667, <5334
spray dat 3911, 6241
trail dat 0, 1187
      dat 0, 0
      dat 0, 0
      dat 0, 0
      dat 0, 0
end start
