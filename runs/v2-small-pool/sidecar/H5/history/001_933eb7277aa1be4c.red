;redcode-94
;name Origami
;author Barthelemy Presutto
;strategy silk paper
;assert CORESIZE==8000
PS1     equ     3620
PS2     equ     2368
PS3     equ     5512
        org     start
start   spl     1
        spl     1
        spl     1
p1      spl     @0, }PS1
        mov.i   }p1, >p1
p2      spl     @0, }PS2
        mov.i   }p2, >p2
p3      spl     @0, }PS3
        mov.i   }p3, >p3
        mov.i   #1, <1
        djn.f   p1, <2667
        end
