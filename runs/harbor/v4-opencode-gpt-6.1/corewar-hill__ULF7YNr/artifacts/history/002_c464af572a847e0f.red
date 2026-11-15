;redcode-94
;name Reed Engine
;author OpenAI
;assert CORESIZE == 8000
org start
start spl 1
 spl 1
 spl 1
p1 spl @0, >4589
 mov.i }p1, >p1
 mov.i #1, <1
p2 spl @0, >5086
 mov.i }p2, >p2
 mov.i >3794, >3435
 mov.i {p2, <p3
p3 jmp @0, >1022
end start