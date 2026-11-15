# Run C (Claude Opus 5.5, fresh agent, 45 min budget, stopped after ~28 min)

Final: "Sickle Moon", 79 instructions: 10-line scanner (`seq` gap 10, step 6740)
booted 424 cells away, 55 `spl` decoys left at the origin, `spl #step,>step` carpet,
d-clear after a full scan. Sparring 0.456 at 100 rounds (~0.446 at 300-1000 rounds).
Hidden hill: see results/eval.md.

Agent's log (summary of its own report):
1. Silk paper 0.296. 2. First scanners killed themselves (0.19), fixed 0.276.
3. Boot + 40 decoys + self-detection exit 0.365, ~0.41 after random parameter tuning.
4. No gain: 4 other carpet bombs, 4 other clears, 3 decoy styles.
5. P-space selectors scanner/paper 0.349, adaptive scanner/stone 0.365 ("30 cycles of
   start-up delay cost ~0.05").
6. Compact 10-line version, ~350 random configurations swept, validated at 300-1000 rounds.
Its own caveat: "tuned on the sparring pool, nothing guarantees transfer to the hidden hill".
