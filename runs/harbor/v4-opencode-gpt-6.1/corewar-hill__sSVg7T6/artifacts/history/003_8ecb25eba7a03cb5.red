;redcode-94
;name Lattice Wake
;author OpenAI
;assert CORESIZE == 8000
org start
start spl 1
spl 1
spl 1
first spl @0,2248
mov.i }first, >first
second spl @0,5570
mov.i }second, >second
mov.i aim, }6509
mov.i {second, {aim
jmp *aim
aim dat 2882, <2667

end
