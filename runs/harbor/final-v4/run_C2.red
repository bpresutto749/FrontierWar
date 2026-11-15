;redcode-94
;name Folded Sheets
;author opencode
;strategy two silk papers launched together
;assert CORESIZE==8000
;params 210 [(1760, 2245, 2340, 'dat    <2667, <5334'), (4277, 1949, 2340, 'dat    <2667, <5334')]
        spl    q1
        spl    1
        spl    1
        spl    1
q0s     spl    @0, >1760
        mov    }-1, >-1
        mov    q0b, >2245
        mov    q0b, }2340
        mov    {q0s, <q0s
        jmz.a  @0, q0s
q0b     dat    <2667, <5334
q1      spl    1
        spl    1
        spl    1
q1s     spl    @0, >4277
        mov    }-1, >-1
        mov    q1b, >1949
        mov    q1b, }2340
        mov    {q1s, <q1s
        jmz.a  @0, q1s
q1b     dat    <2667, <5334
