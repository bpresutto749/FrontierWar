# Run B (Claude Opus 5.5, fresh agent, 45 min budget, stopped after ~27 min)

Final: 65 instructions: 12-line 0.5c scanner (step 3364, gap 12) booted to +5396,
40 random decoy instructions left behind, spl carpet on hits, scan stops after 477
loops, then a two-pass spl/dat clear. Sparring 0.497 (random positions, 1000 rounds:
0.495) - above the reference's 0.489 on the same pool. Hidden hill: see results/eval.md.

Agent's log (summary of its own report):
- Silk paper 0.23-0.30, 0.34 after random constant search; stone/imp 0.23; oneshot 0.24.
- 0.5c scanner + spl carpet + d-clear: 0.47; step/gap search 0.46-0.51 on 30-40 rounds
  ("mostly noise at 100 rounds"); boot + decoy +0.01; two-pass clear 0.498.
- P-space scanner/paper and scanner/stone switchers 0.35-0.39 ("switching costs too much").
- Final choice among finalists by 500-1000 random-position rounds against the sparring pool.
Named weak spot: imp-based warriors (22-45% ties), "probably a bit below sparring on the hill".
