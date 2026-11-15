# FrontierWar: Core War Arena

<!-- À écrire : une phrase. Ex. : un environnement Harbor où les agents de code frontière
     restent sous le meilleur programme humain de Core War. -->

## Run it in one line

```bash
git clone https://github.com/bpresutto749/FrontierWar && cd FrontierWar && harbor run -p harbor/corewar-hill -a opencode -m anthropic/claude-opus-5-5
```

Needs Docker, [Harbor](https://pypi.org/project/harbor/) (`uv tool install harbor`) and an
API key in the shell (`export ANTHROPIC_API_KEY=...`, or `OPENAI_API_KEY` / `GEMINI_API_KEY`
with `-m openai/<model>` / `-m gemini/<model>`). The reward is in
`jobs/<job>/<trial>/verifier/reward.txt`.

Check the scale (two more lines):

```bash
harbor run -p harbor/corewar-hill -a oracle   # the #1 human program: 1.0
harbor run -p harbor/corewar-hill -a nop      # doing nothing: 0.0
```

<!-- Options utiles : -k 5 (5 essais) ; -p harbor/corewar-hill-public si Docker n'a pas le
     contrôle de sortie réseau ; détails dans RUN_HARBOR.md. -->

# FrontierWar: Core War Arena

Core War Arena is a Harbor environment in which a frontier coding agent has 45 minutes to write
one program for Core War, practising against opponents it can see, before that program is judged
against opponents it has never seen. On this task, the best frontier agents we ran still fall
short of Toxic, the #1 human program, and the environment shows precisely where and why.

## Run it in one line

```bash
git clone https://github.com/bpresutto749/FrontierWar && cd FrontierWar && harbor run -p harbor/corewar-hill -a opencode -m anthropic/claude-opus-5-5
```

You need Docker, Harbor (`uv tool install harbor`) and an API key exported in your shell
(`ANTHROPIC_API_KEY`, or `OPENAI_API_KEY` / `GEMINI_API_KEY` with `-m openai/<model>` or
`-m gemini/<model>`). The reward, a single number between 0 and 1, is written to
`jobs/<job>/<trial>/verifier/reward.txt`. To check the scale yourself, `-a oracle` submits the
#1 human program and scores 1.0, and `-a nop` does nothing and scores 0.0. `-k 5` runs five
attempts, and `-p harbor/corewar-hill-public` is there for Docker hosts without egress control
(RUN_HARBOR.md).

## The question

Can a frontier AI agent turn practice into a design that wins against opponents it has never
seen? Not yet. The agents we tested either cannot escape the traps of practice, or cannot find a
winning design, or both: Claude Opus 5.5 falls into the traps and misses the design, while
GPT-6.1 sol escapes every trap and still misses the design.

## The task

Core War is a programming game from 1984: two programs share one memory of 8,000 cells, each
tries to make the other crash, and the last one still running wins. The agent writes a single
program in Redcode, an assembly language of about twenty instructions. For 45 minutes it can
play as often as it likes against 30 practice opponents, which it sees only as black boxes, and
every reply tells it how many minutes are left. Its last submission is then played 500 times
against each of 30 hidden opponents, all human-written King-of-the-Hill programs, which makes
15,000 games scored by pMARS, the game's official simulator. The reward is linear between Dwarf,
the beginner's program from the documentation, at 0, and Toxic, the #1 of 264 human programs, at 1. It is capped at 1, but the raw score is not, so the benchmark does not saturate yet.

## Results

Through `harbor run` and OpenCode, Claude Opus 5.5 scores 0.713 on average over 5 runs, with no
run above 0.741, and GPT-6.1 sol scores 0.842 over 5 runs, between 0.817 and 0.899. Toxic scores
1.000 by construction and doing nothing scores 0.000. None of the 32 frontier-agent runs recorded
on this task, these ten and 22 earlier Claude Opus runs, reaches 1. Every figure is computed from
the run folders in `runs/harbor/` by the scripts in `exploits/`, and summarised in
`results/models.md`.

## Why the agents fall short

The first layer is a set of three traps of practice, and Claude Opus 5.5 falls into all of them.
It stops early, leaving 12 to 29 of its 45 minutes unused. It polishes one idea: none of its five
final programs opens by looking for the enemy, which is exactly what Toxic does. And in two runs
its program fits the practice opponents rather than the test, losing 0.06 to 0.09 between the
practice score and the hidden score, against 0.02 for Toxic; one of those runs even writes, in its
own final message, that part of its practice score is overfitting. GPT-6.1 sol avoids all three:
it works until minute 43.5 or later, four of its five programs find the enemy first, and its
hidden score stays within 0.01 to 0.03 of its practice score, like Toxic's.

The second layer is the design, and neither agent gets past it. Over 90% of the gap to Toxic on
the hidden test is already there against the opponents the agents can see and replay at will:
92% for Claude Opus 5.5 and 98% for GPT-6.1 sol. Over the 15,000 hidden games, GPT-6.1 sol wins
as often as Toxic (3,870 to 5,011 wins against 4,033) but loses three to five times as often
(3,394 to 5,913 losses against 1,167), mostly against scanners such as Alladin's Cave, Crimp and
vamp 0.2b; Claude Opus 5.5 loses between 3,061 and 8,111 times. Their programs attack well but do
not survive. More practice does not fix this: with three times more time, Claude Opus 5.5 reaches
the same score (0.704 without a clock, 0.713 with one), and a run that tests up to 1,469 programs
is still nowhere near the 10^140 possible twelve-line programs, so what wins is a good idea, not
brute force. The details, with the agents' own words, are in FAILURES.md.

## Can the score be trusted?

The program is scored after the agent has finished, in a separate and sealed verifier that the
agent cannot read or write. Copying a published program scores 0, including short published
programs padded with dead code or slightly retuned, and faking the score file scores 0. Of the 34
cheats and shortcuts we tested against the real verifier, none scores more than 0.24. Doing
nothing scores 0 and the #1 human program scores 1, so anyone can check both ends of the scale
with one command each. The exploit sweep and every case are in EXPLOITS.md.

## Videos

The [1 min 59 pitch](media/corewar_pitch_1min59.mp4) gives the question, the answer and the two
layers in one go, and the [full demo](media/corewar_demo_full.mp4), about eight minutes, replays
one Claude Opus run from its logs, shows one real game against a hidden opponent, and walks
through every figure above. The code that draws both is in `video/`.

## Bonus: training small models

The environment is also a training signal. Across expert iteration and reinforcement learning
(GRPO), on open models from 3B to 32B parameters, 19 training runs improve their reward on the
hidden opponents beyond the noise, and the gain replicates with a second seed at 7B, 14B and 32B.
A 32B model, starting from the task text alone, learns to write its own bombers and goes from
about 0.01 to between 0.06 and 0.08, with a best single program at 0.33. The runs and their
reports are in RL_SYNTHESIS.md, TRAINING.md and `training/`.

## Repository

The Harbor task itself, with its environment, its MCP server and its verifier, lives in
`harbor/corewar-hill/`. The Harbor runs of both models are kept in `runs/harbor/`, and
the analyses behind every number in `results/`, produced by the scripts in `exploits/`.
The full report is in REPORT.md, the failure modes in FAILURES.md, the exploit sweep in
EXPLOITS.md, and the choices we made and why in DECISIONS.md. The small-model training is
described in TRAINING.md and RL_SYNTHESIS.md, with its code in `training/`. The videos are in
`media/`, and the code that draws them in `video/`.

