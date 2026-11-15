# Run G (Claude Opus 5.5, fresh agent, same instructions + task_src/lessons.md, stopped after ~28 min)

The only difference from runs A-E2 is the "Lessons from earlier attempts" section
appended to the instructions (task_src/lessons.md): treat sparring as validation,
build a wider private test set with random positions, composites dominate hills, imp
weakness, use the whole budget.

Final: "Lynx Folding", 40 instructions: p-space two-mode warrior (cell 37), a seq
scanner with spl carpet and gated spl/dat clear, or a 3-stage silk paper with
anti-imp decrements; switches mode after a loss, or after a tie in paper mode.
Sparring 0.430 (0.408 at 300 random-position rounds; ~0.70-0.80 against its own
archetype test set). Hidden hill: see results/eval.md.

It followed lessons 1-3 (built an archetype test set in work/opp/, used random
positions, stopped tuning at noise level, tried qscan openings, chose a composite) and
ignored lesson 4: it stopped at ~28 of 45 minutes, "although the instructions asked to
use the whole budget".
