;redcode-94
;name Driftglass Seed
;author OpenAI
;assert CORESIZE == 8000
org start
start spl 1
      spl 1
      spl 1
      spl 1
seed  spl @0, 1739
      mov.i }seed, >seed
bud   spl @0, 3067
      mov.i }bud, >bud
      mov.i sting, >1979
      mov.i sting, }4211
      add.ab #97, -2
      mov.i {bud, <root
root  djn.f @0, <5579
sting dat.f <2667, <5334
end start