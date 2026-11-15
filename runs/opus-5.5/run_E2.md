# Run E2 (Claude Opus 5.5, fresh agent, 45 min budget, stopped after ~28 min)

Final: 12-instruction silk paper (8 processes, four spl/mov spawn pairs, steps 5431,
1838, 2172, 1610 from a random search of ~280 step sets validated at 300-500 rounds).
Sparring 0.418 (0.416 at 300-500 rounds). Hidden hill: see results/eval.md.

Agent's log (summary): silk variants 0.30-0.416; qscan + paper 0.34-0.39; stone 0.32,
stone + paper 0.385; own scanners 0.16 then 0.33; p-space paper/stone 0.33-0.37 and
paper/scanner 0.37-0.39. Its own forecast: "expect about 0.4 on the hidden hill".
