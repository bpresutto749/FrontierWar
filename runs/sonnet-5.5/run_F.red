;redcode-94
;name Comb
;author x
;assert CORESIZE==8000
org top
top   mov.i  zap, @aim
      add.ab #15, aim
      jmp    top
aim   dat    0, 40
zap   dat    0, 0
