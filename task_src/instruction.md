Write the strongest Core War warrior you can, in Redcode, and submit it.

## How it is scored

Your warrior plays a hidden hill of 30 human-written competitive warriors. They come from
the public history of the ICWS '94 King-of-the-Hill and cover the whole strength range,
from weak warriors to some of the strongest ever written.

Against each hill warrior, your warrior plays 500 rounds with pMARS 0.9.4 in the standard
'94 settings:
- coresize 8000;
- 80000 cycles before a tie;
- 8000 processes;
- max warrior length 100;
- min distance 100;
- ICWS '94 instructions with the pMARS extensions (p-space is allowed).

Starting positions follow pMARS's fixed position series (`-f`), so scores are exactly
reproducible. The series is seeded from both warriors' code, so any change to yours redraws
the positions: differences of about 0.01 between versions are noise.

Per round, a win is worth 3 points, a tie 1 and a loss 0. Your **hill score** is your mean
points per round over the whole hill, divided by 3, so 1 means every round was won.

The reward rescales the hill score so that Dwarf, the classic bomber in `doc/example_dwarf.red`
(hill score 0.1475), gets 0 and a strong human-written warrior (hill score 0.4866) gets 1:

    reward = min(1, max(0, (hill score - 0.1475) / (0.4866 - 0.1475)))

A warrior that does not assemble scores 0. pMARS hangs on very long source lines, so:
- comment lines are cut to 200 characters;
- a code line longer than 200 characters makes the file invalid;
- files are limited to 20 000 bytes.

Your warrior is assembled exactly as it is scored: two warriors, 500 rounds.

Write your own warrior. A near-copy of any published warrior in our corpus of about 580
(the hill and sparring warriors included) scores 0, including a short published warrior
with a few lines added or its numbers nudged (`get_rules` gives the exact rule). Using
published ideas and techniques with your own constants is fine; submitting someone else's
warrior is not.

## What you have

The MCP server `corewar` provides these tools:

| tool | what it does |
|---|---|
| `get_rules` | these rules |
| `list_sparring` | the ids (s01–s30) of 30 sparring warriors from the same ladder as the hill, spread over the same strength range. None of them is on the hill. They are black boxes: you can play them, but their source is not available. |
| `battle(source, opponents=None, rounds=100)` | plays your warrior against sparring warriors with the scoring settings (rounds up to 500) |
| `battle_custom(source, opponent_source, rounds=100)` | plays two warriors of your own against each other |
| `submit(source)` | sets your final submission. You can submit as often as you like; the last accepted submission is the one scored. |
| `status` | shows the clock and what is currently submitted |

In `/app`:

| path | what it is |
|---|---|
| `bin/pmars` | the scoring simulator |
| `doc/` | the Redcode language reference, a beginners' guide, the ICWS '94 draft, the pMARS manual, and `strategy_primer.md`, a short summary of common strategies |
| `tools/spar.py` | command-line access to the MCP server, for scripted sweeps: `python3 tools/spar.py my.red`, `python3 tools/spar.py --submit my.red`, `python3 tools/spar.py --status` |
| `tools/battle.py` | local battles against warriors you wrote yourself: `python3 tools/battle.py my.red --vs a.red b.red` |

Submit with the `submit` tool (or `tools/spar.py --submit`). If nothing was submitted
through the server, the file `/app/submission.red` is scored instead.

You have 45 minutes. Every reply from the server ends with a clock: minutes used and
minutes left, counted from your first call to it; the run itself stops 45 minutes after it
starts, so the real time left can be slightly shorter. Do not use the internet. Keep a valid
submission in place as you work: whatever is submitted when you stop is your result.
