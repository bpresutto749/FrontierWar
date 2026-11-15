#!/usr/bin/env python3
"""Checks the visualiser's simulator (mars.py) against pMARS: for three warrior pairs and 30
random start positions each, the round winner must be the same. The scores in the task never
use mars.py; it only draws the game shown in the demo."""
import os, random, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from arena import core
import mars

P = str(core.PMARS)
R = lambda *p: os.path.join(ROOT, *p)
PAIRS = [(R("runs", "harbor", "final-v4", "run_C5.red"), R("data", "reference_toxic.red")),
         (R("runs", "harbor", "final", "run_OC1.red"), R("data", "reference_toxic.red")),
         (R("runs", "harbor", "final-v4", "run_C2.red"), R("doc", "example_dwarf.red"))]

def listing(a, b):
    return subprocess.run([P, "-r", "1", "-F", "4000", a, b], capture_output=True, text=True).stdout

random.seed(1)
total = ok = 0
for a, b in PAIRS:
    ws = mars.parse_listing(listing(a, b))
    bad = []
    for pos in random.sample(range(100, 7901), 30):
        mine, ref = mars.Mars(ws[0], ws[1], pos).run(), mars.pmars_round(a, b, P, pos)
        total += 1; ok += mine == ref
        if mine != ref: bad.append((pos, mine, ref))
    print(f"{os.path.basename(a)} vs {os.path.basename(b)}: {30 - len(bad)}/30 agree", bad[:5], flush=True)
print(f"total {ok}/{total}")
sys.exit(0 if ok == total else 1)
