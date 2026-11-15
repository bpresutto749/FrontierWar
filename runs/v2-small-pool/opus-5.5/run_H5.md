# Run H5 (Claude Opus 5.5, final environment, fresh agent, stopped after ~27 of 45 min)

Final: 32-instruction p-space switcher (switch after a loss) between a 4-pair silk paper
and a 4-cell stone booted 4000 cells away; `stp` replaced by `dat` after use so paper
copies cannot re-enter the decision code. Agent's sparring figure: 0.409 at 500 rounds.
Hidden hill and trajectory: results/eval.md, results/trajectories.md.

Agent's log (summary): silk 3 pairs 0.371; 3-instruction stone 0.324; spl stone 0.250;
oneshot to d-clear 0 (self-kill bugs), fixed 0.262; paper/stone switcher 0.359, 0.39 with
the stone booted; 3-strategy p-space bandit capped at 0.39 (fixed a p-space corruption
bug); 4-pair paper 0.394 alone; switcher with it 0.409; nothing beat 0.409 at 500 rounds
(hysteresis, stone/imp 0.168, other stones, random step sweeps that fall back to ~0.40).
