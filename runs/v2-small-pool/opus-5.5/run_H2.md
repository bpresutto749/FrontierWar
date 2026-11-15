# Run H2 (Claude Opus 5.5, final environment, fresh agent, stopped after ~29 of 45 min)

Final: 84-instruction p-space switcher between three self-written components: a 0.66c
oneshot scanner with an unrolled spl/dat clear, a 3-stage silk paper, and a spl stone
booted to +6000; per-component scores kept in p-space (+2 win, 0 tie, -1 loss, argmax).
Agent's sparring figure: 0.488 at 500 rounds (the reference scores 0.498 on the same pool).
Hidden hill and trajectory: results/eval.md, results/trajectories.md.

Agent's log (summary): components alone 0.215-0.39; 2-component switchers 0.36-0.376;
p-space scoring 0.399; adding the booted stone 0.41-0.475; scanner step 1736/4 -> 0.488.
Its own caveats: "the 0.488 is probably a bit flattering, best of many variants";
neighbouring settings give 0.44-0.45; the selector "freezes on an average component".
