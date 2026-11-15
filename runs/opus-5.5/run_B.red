;redcode-94
;name Lattice Sweeper
;author anon
;strategy booted 0.5c scanner, spl carpet, spl/dat clear, decoy
;assert CORESIZE==8000
        org boot
boot
        mov.i  gate+0, gate+0+5396
        mov.i  gate+1, gate+1+5396
        mov.i  gate+2, gate+2+5396
        mov.i  gate+3, gate+3+5396
        mov.i  gate+4, gate+4+5396
        mov.i  gate+5, gate+5+5396
        mov.i  gate+6, gate+6+5396
        mov.i  gate+7, gate+7+5396
        mov.i  gate+8, gate+8+5396
        mov.i  gate+9, gate+9+5396
        mov.i  gate+10, gate+10+5396
        mov.i  gate+11, gate+11+5396
        jmp    gate+1+5396
gate    dat   sbomb-gate, 100
sstart  mov.i  sbomb, >gate
        add.f  inc, sc
sc      seq.i  2, 14
        mov.ab sc, gate
        djn.b  sstart, #477
clear   spl    #0, 0
cl      mov    *gate, >gate
        djn.f  cl, >gate
sbomb   spl    #dbomb-gate, 12
dbomb   dat #dbomb-gate, 12
inc     dat    3364, 3364
        spl.f $2090, $4059
        jmz.ba {6462, <769
        jmz.a {3546, #5701
        jmz.ab <4843, $7385
        mov.a #209, #7694
        jmz.x <7939, {5947
        dat.f <6257, }7694
        jmz.f <2832, <5545
        spl.i }7801, >7590
        dat.ba $1523, >991
        mov.x {4160, <2486
        mov.f }6933, {4826
        dat.ba <6093, {3395
        spl.ab *709, }5438
        sne.a @4268, {3036
        jmz.x #3845, #2528
        sne.f {5302, @1382
        sne.b #6313, <4421
        sne.b {4209, *7803
        sne.ab }7453, >5401
        sne.f #3144, @4250
        sne.b {7781, #3942
        mov.f <7709, {3973
        mov.ba *13, *3754
        sne.a <5205, @4512
        sne.b $6541, >266
        dat.a #3711, #6178
        mov.b >897, @2822
        mov.a @1308, >4321
        spl.x >5311, >3725
        mov.ba }936, #2556
        jmz.ab {6523, <2117
        dat.ab <7910, {6694
        dat.b #3255, @290
        spl.ba {4463, <7993
        sne.ba <4292, #3236
        sne.i *5406, {482
        mov.b <7173, #2510
        dat.i $2543, >6094
        spl.ba >1069, #4594
end
