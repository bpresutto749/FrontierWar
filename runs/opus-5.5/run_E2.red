;redcode-94
;name Lattice
;author Anonymous
;strategy 8-process silk paper: four spawn pairs per copy, each copy replicates at four distances
;assert CORESIZE==8000
S1 equ 5431
S2 equ 1838
S3 equ 2172
S4 equ 1610
        spl  1, <300
        spl  1, <400
        spl  1, <500
silk    spl  @0, >S1
        mov.i }silk, >silk
silk2   spl  @0, >S2
        mov.i }silk2, >silk2
silk3   spl  @0, >S3
        mov.i }silk3, >silk3
        spl  @0, >S4
        mov.i }-1, >-1
bomb    dat 0,0
