# Run J2 (Claude Opus 5.5, version 3, fresh agent, stopped after ~30 of 45 min)

Final: 17-instruction 0.8c scanner (two-way unrolled add.f/seq/sne loop, gap 20, step 1405)
that switches on the first find to a spl/mov/djn.f core clear with self-skip.
Agent's sparring figure (30 warriors): 0.455 at 500 rounds. Hidden hill and trajectory:
results/eval.md, results/trajectories.md.

Agent's log (summary): silk 0.266; mod-5 stone 0.316; 0.66c scanner + dat clear 0.387-0.395;
two-pass clear 0.30; + 3-point imp ring 0.32; p-space scanner/stone 0.349-0.394 ("the longer
code weakens the scanner and selection does not make up for it"); 0.8c + ~40 step/gap
combinations 0.42-0.455; decoys, more unrolling, other clears 0.36-0.449. Its own caveat:
the scan start offset swings the score from 0.35 to 0.45 on this pool, so "differences of
0.01 between variants are probably noise with respect to the hidden hill".
