# Run D2 (Claude Opus 5.5, fresh agent, 45 min budget, stopped after ~25 min)

Final: "Lattice Sweep", 65 instructions: unrolled boot copies a 12-line seq scanner
7727 cells away, 40 random decoy lines left behind, ~0.4c loop (step 1060, gap 11)
laying a `spl #step,>step` carpet redirected to hits, then a gated spl/dat clear with
`dat <2667` anti-imp bombs. Sparring 0.583 at 100 rounds, 0.547 at 1000 (the best
sparring warriors score ~0.549 on the same pool). Hidden hill: see results/eval.md.

Agent's log (summary): basic mod-10 scanner 0.42-0.45; boot + decoy ~0.49; oneshot
0.19; own silk paper 0.41; p-space scanner/paper 0.447 after fixing a modifier bug;
wide random search over steps, bombs, seq modes, carpet start, boot distance and decoy
size (mod-20 steps best, 0.54-0.56 at 400 rounds); a 12-24 probe qscan opening
0.50-0.53 (dropped); top-3 validated at 1000 rounds. Stopped ~20 minutes early.
