# Run A (Claude Opus 5.5, fresh agent, 45 min budget, stopped after ~28 min)

Final: "Carpet Weaver", 14 instructions: 0.5c `seq` scanner (step 5870, gap 5)
laying a `spl #0` carpet from each hit, then a backward DAT clear. Sparring 0.375
(agent's own random-seed estimate 0.41). Hidden hill: see results/eval.md.

Agent's log (summary of its own report):
1. Silk paper, 8 processes: 0.30 (0.31 after step sweep; the 0.34 it first saw was selection noise).
2. `spl #0` stone: 0.25; with a 3-point imp spiral 0.27-0.30.
3. Scanner with two bombs per hit 0.23; oneshot 0.21.
4. P-space switchers (paper/stone, scanner/paper, scanner/stone): 0.27-0.38, none beat the plain scanner.
5. Carpet scanner 0.389 at step 2430; ~90 step values swept, multi-seed re-check -> 5870.
6. No gain: boot away from origin, 20-70 decoys, double carpet, unrolled clear, other bombs.
Stopped ~17 minutes before the deadline. Weak spots it named: qscan + stone/imp warriors.
