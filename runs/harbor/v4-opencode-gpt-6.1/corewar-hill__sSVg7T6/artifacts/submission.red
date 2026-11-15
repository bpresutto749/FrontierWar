;redcode-94
;name Lattice Wake
;author OpenAI
;strategy Paired-probe opening, symmetric bombing, A-pointer replication.
;assert CORESIZE == 8000

org scan
qptr   dat 0, 0
qbomb  dat <2667, <5334
qdelta dat -5, 5

; Remember the last unequal pair; equal empty pairs cost one cycle.
scan   seq.i 485, 522
       mov.ab #485+scan+0-qptr, qptr
       seq.i 1133, 1170
       mov.ab #1133+scan+2-qptr, qptr
       seq.i 1781, 1818
       mov.ab #1781+scan+4-qptr, qptr
       seq.i 2429, 2466
       mov.ab #2429+scan+6-qptr, qptr
       seq.i 3077, 3114
       mov.ab #3077+scan+8-qptr, qptr
       seq.i 3725, 3762
       mov.ab #3725+scan+10-qptr, qptr
       seq.i 4373, 4410
       mov.ab #4373+scan+12-qptr, qptr
       seq.i 5021, 5058
       mov.ab #5021+scan+14-qptr, qptr
       seq.i 5669, 5706
       mov.ab #5669+scan+16-qptr, qptr
       seq.i 6317, 6354
       mov.ab #6317+scan+18-qptr, qptr
       seq.i 6965, 7002
       mov.ab #6965+scan+20-qptr, qptr
       seq.i 7613, 7650
       mov.ab #7613+scan+22-qptr, qptr
       jmz.b start, qptr
       jmn.f strike, @qptr
       add.ab #37, qptr
strike mov.ba qptr, qptr
       add.a #1, qptr
qloop  mov.i qbomb, *qptr
       mov.i qbomb, @qptr
       add.f qdelta, qptr
       djn.b qloop, #16
       jmp start

; Eight-process copies carry their next reverse-copy destination as a bomb.
start  spl 1
       spl 1
       spl 1
first  spl @0, 2248
       mov.i }first, >first
second spl @0, 5570
       mov.i }second, >second
       mov.i aim, }6509
       mov.i {second, {aim
       jmp *aim
aim    dat 2882, <2667

end
