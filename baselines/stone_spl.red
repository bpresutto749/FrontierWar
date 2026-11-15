;redcode-94
;name SimpleStone
;assert CORESIZE==8000
step    equ 3044
        spl #0, #0
loop    add.ab #step, bomb
        mov.i bomb, @bomb
        jmp loop
bomb    dat #0, #0
