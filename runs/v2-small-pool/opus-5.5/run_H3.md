# Run H3 (Claude Opus 5.5, final environment, fresh agent, stopped after ~30 of 45 min)

Final: 89-instruction p-space selector that tries three self-written components in turn
for 30 rounds, then keeps the best (oneshot jmz scanner with forward d-clear; spl scanner
that switches to a dat clear; 8-process silk paper), scanners booted away with the rest
left as decoy. Agent's sparring figure: 0.376 at 500 rounds.
Hidden hill and trajectory: results/eval.md, results/trajectories.md.

Agent's log (summary): dwarf 0.215; silk 0.24-0.26; stone + imp ring 0.18; oneshot
variants 0.15-0.33; 33-configuration sweep 0.30-0.33; first switcher 0.265; fixed a
mov.ab/mov.b selector bug; tuned exploration length and loss penalty -> 0.376. Its own
caveat: "0.376 is probably a lucky draw; neighbouring configurations give 0.32-0.36".
