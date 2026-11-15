# Run H1 (Claude Opus 5.5, final environment, fresh agent, stopped after ~31 of 45 min)

Final: "Origami", 13-instruction silk paper (8 processes, three copy stages at 5002 /
4953 / 2410, a bombing line). Agent's sparring figure: 0.436 at 500 rounds.
Hidden hill and trajectory: results/eval.md, results/trajectories.md.

Agent's log (summary of its own report): simple stones 0.25-0.28; first silk 0.298;
scanners 0.23-0.27 (dropped: lost ~85% locally to its own paper); p-space paper/stone
switcher 0.344 (dropped); random search over paper constants and structure -> 0.417;
two hill-climbing chains on 200 rounds -> 0.436, no progress for ~15 minutes; paper +
3-point imp ring 0.424 (dropped). Its own caveat: "the 200-round figure (0.444) is
optimistic" because each climbing step was kept only if the score did not drop.
