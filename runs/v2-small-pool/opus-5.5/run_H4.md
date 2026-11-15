# Run H4 (Claude Opus 5.5, final environment, fresh agent, stopped after ~32 of 45 min)

Final: 90-instruction two-armed p-space bandit: a 6-stage silk paper and a sne oneshot
scanner with spl then dat clears; 8 exploration rounds (4 per arm), then the best arm
is frozen; `stp` instructions erase themselves so paper copies cannot corrupt p-space.
Agent's sparring figure: 0.421 at 500 rounds.
Hidden hill and trajectory: results/eval.md, results/trajectories.md (its best hidden
score was its 13-minute submission; the last 17 minutes of tuning lowered it).

Agent's log (summary): imp 0.178; mod-4 stone 0.257, with imp ring 0.148; silk 0.319 (2
stages) to ~0.385 (5-6 stages), best paper 0.402; oneshot alone 0.197; switch-on-loss
paper/scanner 0.271; qscan + paper 0.37-0.385; bandit after the p-space corruption fix
0.410 (K=6), 0.421 (K=4). Its own caveat: differences of ±0.02 "are of the order of the noise".
