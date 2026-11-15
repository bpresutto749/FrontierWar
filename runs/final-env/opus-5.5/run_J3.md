# Run J3 (Claude Opus 5.5, version 3, fresh agent, stopped after ~27 of 45 min)

Final: "Flint5", 11 instructions: a 5-instruction spl stone (step 3044, `dat >-1,>1` bomb)
booted 5900 cells away, the original cells left as a decoy.
Agent's sparring figure (30 warriors): 0.349 at 500 rounds. Hidden hill and trajectory:
results/eval.md, results/trajectories.md.

Agent's log (summary): stone + imp spiral 0.301, stone alone 0.343, + 3-point ring 0.318
("imps lower the score in every case"); silk 0.275, best paper 0.304; jmz scanners and
oneshot 0.19-0.20; p-space stone/paper switchers 0.30-0.352 at 200 rounds, 0.339 at 500;
qscan + switcher 0.25-0.27 ("clearly worse, no time to find out why"); stone + paper
simultaneously 0.31; tuned step and boot distance (noise). Named weak spot: ~10 opponents
(papers and fast scanners) where the stone scores below 0.15.
