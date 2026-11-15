# Core War Arena: the full report (results, failure modes, integrity, limits)

**Can a frontier AI agent turn practice into a design that wins against opponents it has never seen?**

Not yet. They can't find a winning design, escape the traps of practice, or both:

| | find a winning design | escape the traps of practice |
|---|---|---|
| Claude Opus 5.5 (0.71) | ✗ | ✗ |
| GPT-6.1 sol (0.84) | ✗ | ✓ |

Over 90% of both agents' gap to the #1 human program is already there on the opponents they practise on (92% and 98%).

*Break the Agent (AfterQuery), Junction 2026 · Harbor task `harbor/corewar-hill` · run it
with `harbor run -p harbor/corewar-hill -a opencode -m <provider/model>` (RUN_HARBOR.md)*

**Videos:** [pitch, 1 min 59](media/corewar_pitch_1min59.mp4) ·
[full demo, 8 min 10](media/corewar_demo_full.mp4) (how they are made, and two shorter cuts: video/README.md)

**Headline.** On the same task, through `harbor run` + OpenCode, Claude Opus 5.5 scores
**0.713** (5 runs, all ≤ 0.741) and GPT-6.1 sol **0.842** (5 runs, 0.817–0.899), against **1.000** for
the #1 human program (Toxic, Elo #1 of 264) and 0.000 for doing nothing. 0 of 32 AI runs
recorded on this task reached 1.

**Two layers: the traps of practice, on top of the design.**

Underneath is design. On the 30 practice opponents, which it can test against as often as it
likes, GPT-6.1 sol's final program already trails Toxic: 98% of its gap on the hidden test is
there in practice. Its hidden score stays close to its practice score, as Toxic's does. Over the
15,000 hidden games it wins as often as Toxic, yet loses three to five times as often. It scores 0.84.

On top come three traps of practice: stopping early, polishing one idea, fitting the practice set.
Claude Opus 5.5 falls into all three (12–29 of its 45 minutes unused; none of its 5 programs finds
the enemy first; in runs C1 and C5 the hidden score falls 0.06–0.09 below practice, against 0.02
for Toxic) and trails further: 0.71, with 92% of its gap already there in practice.

GPT-6.1 sol avoids the traps. No model has closed the design gap yet, and that is what Core War
Arena keeps ranking.

In one sentence: *practice traps on top of a deeper design gap: Core War Arena measures both,
and ranks agents on the one no model has closed.* The figures are in [Two layers](#two-layers-the-traps-of-practice-and-the-design)
(`exploits/compare_models.py` → `results/models.md`).

## In three paragraphs

**What the agent has to do.** Write an original Core War warrior in Redcode and submit it
through the environment's MCP server. Core War is the 1984 programming game in which two
assembly programs share a circular memory and each tries to make the other crash. The
warrior is scored against a **hidden hill of 30 human-written King-of-the-Hill warriors**,
using the exact simulator (pMARS). To work with, the agent gets:
- that simulator;
- the language reference and a strategy primer;
- **30 black-box sparring opponents** drawn from the same ladder as the hill, with the same
  strength spread;
- a clock at the end of every server reply: minutes used and minutes left of the 45.

**Why it is hard.** Everything needed is available: rules, an exact simulator, a strategy
primer, and a representative test set whose scores track the hidden hill (r = 0.83 over 19
agent-level warriors, `results/proxy_check.md`). Claude Opus 5.5 still plateaus below the #1 human
program, **even on the opponents it can see** (GPT-6.1 sol, below, avoids these traps and still falls short):
- **On the visible pool**, they reach 0.34–0.49, against 0.507 for the human reference.
  On the hidden hill, the same warriors stay at 0.32–0.40, against 0.487.
- **They converge on a single tuned archetype.** They try composite designs, find them weaker
  than that archetype, and abandon them, although the strongest human warriors are
  composites.
- **More time does not help them.** Without a clock (v3), the five Harbor runs stopped
  after 4–14 minutes, and three said they had run out of time ("I ran out of the 45
  minutes"). With a clock in every reply (v4, shipped), they worked 16–33 minutes, played
  up to 637 battles, and their reward did not move: 0.704 → 0.713. One stopped "with about
  22 minutes left on the clock".
- **They mistake the visible score for the real one.** In v4, two of the five runs spent
  their extra minutes raising the visible score and lowering the hidden one (C1: visible
  0.390 → 0.437, hidden 0.391 → 0.373), and the best visible score, 0.489, is 0.018 from
  the reference on the visible pool and 0.089 below it on the hidden hill (FAILURES.md).
- **The gap is not overfitting.** All 15 Harbor and v3 final warriors score below the
  reference on the very pool they tuned on, which the reference plays as is. In v4,
  92% of the hidden-hill gap is already there on the visible pool; the rest, the agents'
  extra visible-to-hidden drop, is 8%. Picking each run's best submission on the hidden
  hill with hindsight lifts the v4 mean from 0.713 to 0.741 only (`results/overfit_check.md`).

None of these is a Core War quirk. They are the mistakes coding agents make in everyday
work: tuning for the tests they can see instead of the behaviour that matters, declaring the
job done while time and room to improve remain, and polishing one solution instead of
designing a better one. Here each one is measured, against a fixed human bar. The task has
the shape of any agent work judged against hidden, adaptive opposition: exploit and defence
code, bidding agents, code under fuzzing.

**How it is scored.**
- **Hill score.** Each warrior plays 500 rounds against each of the 30 hidden warriors (3
  points per win, 1 per tie). The hill score is the mean points per round / 3.
- **Reward.** The verifier writes `reward = clip((hill − 0.1475) / (0.4866 − 0.1475), 0, 1)`
  to `/logs/verifier/reward.txt`.
  - Dwarf gets 0. It is A. K. Dewdney's classic bomber and the example warrior in the agent's
    own documentation.
  - The human reference gets 1. It is Toxic, by John Metcalf, Elo #1 of 264 humans, fixed
    before any agent run.
  - The reward is clipped at 1 (the challenge's [0, 1] rule). The raw hill score is not: Toxic
    scores 0.487 of a possible 1.000, so a program stronger than the #1 human program would still
    be ranked by its hill score. The best AI run so far reaches 0.899; the benchmark doesn't
    saturate yet.
- **Reproducibility.** Scores are deterministic: pMARS fixed position series, standard error
  about ±0.01.
- **Copies.** A near-copy of any of 581 published warriors scores 0.
- **The zero point was changed after the fact.** Until all 17 recorded runs had been scored,
  including the five final runs (J1–J5), the zero point was a one-line imp (`mov.i #0, 1`,
  hill 0.1650). It is now Dwarf (hill 0.1475).
  - Why: the imp never kills anything and scores only through ties, which makes it a
    degenerate zero. Dwarf is the canonical first warrior and the very example the agent is
    handed, so reward 0 now reads "no better than the textbook example".
  - Every reward was recomputed from the stored raw hill scores, without rerunning any agent
    (`exploits/rescore_anchor.py` → `results/rescored_dwarf_anchor.md`).
  - Both anchors are affine maps of the same raw score, so the order of the runs is unchanged.
    Every agent's reward rises slightly (v3 mean 0.653 → 0.671), and the gap to the reference
    in raw hill score is untouched.

## Results

| | visible pool (30) | hidden-hill score | reward |
|---|---|---|---|
| **The #1 human program** (Toxic) | 0.507 | 0.487 | **1.000** |
| **GPT-6.1 sol (`openai/gpt-6.1-sol`), v4.1, `harbor run` + OpenCode, 5 runs (agents worked 43.8–45 min)** | 0.442–0.468 | 0.425–0.452 | **0.842** (95% CI 0.80–0.88; all 5 ≤ 0.899) |
| **Claude Opus 5.5, shipped environment (v4, with clock), `harbor run` + OpenCode, 5 runs (agents worked 16–33 min)** | 0.382–0.489 | 0.373–0.399 | **0.713** (95% CI 0.67–0.75; all 5 ≤ 0.741) |
| Claude Opus 5.5, v3 (no clock), `harbor run` + OpenCode, 5 runs (agents stopped after 4–14 min) | 0.342–0.422 | 0.362–0.398 | 0.704 (CI 0.65–0.76; all 5 ≤ 0.739) |
| Claude Opus 5.5, v3, local Claude agent harness, 5 runs (25–35 min used) | 0.349–0.455 | 0.320–0.394 | 0.671 (CI 0.55–0.79; all 5 ≤ 0.728) |
| Claude Opus 5.5, version 2 (10 black-box sparring), 5 runs | — | 0.309–0.401 | 0.595 (CI 0.44–0.75) |
| Claude Opus 5.5, version 1 (10 visible sparring sources, no primer), 5 runs | — | 0.372–0.465 | 0.746 (CI 0.61–0.88) |
| Claude Sonnet 5.5, version 1, 1 run | — | 0.195 | 0.140 |
| CodeClash ladder warriors, July 2026 (Opus 4.8 / GPT-5.5 / Sonnet 5 / Gemini 3.5 Flash) | — | 0.083–0.332 | 0.000–0.543 |
| Best trivial warrior (5-line stone); one-line imp | — | 0.228; 0.165 | 0.237; 0.052 |
| Qwen2.5-Coder-7B-Instruct after 4 rounds of expert iteration on the environment (base model: 0.000), 64 samples | — | 0.124 mean | 0.032 mean (best 0.060) |
| Qwen2.5-Coder-7B-Instruct after 200 GRPO steps on the environment (base model: 0.003), 65 samples; 91% of this reward comes from variants of the Dwarf shown in the prompt (training/grpo/RESULTS.md) | — | 0.120 mean | 0.053 mean (best 0.194) |
| Dwarf (the documentation's example; a published warrior, so as a submission the copy gate gives 0) | — | 0.147 | 0.000 |
| Do-nothing | — | 0.000 | 0.000 |

None of the 32 runs (27 Opus or Sonnet, across four environment versions and two harnesses,
and 5 GPT-6.1 sol) reached the reference. The best reached 0.936. Every number comes from `make eval`
(`results/eval.md`). For the Harbor runs, `make eval` rescores the ten submissions outside
Docker and matches the reward the Harbor verifier wrote (to the 4 decimals `eval.md` reports) (`runs/harbor/`,
`results/trajectories_harbor*.md`). Run histories, agents' working directories and their own
reports are in `runs/`.

**Real Harbor runs** (Harbor 0.25.0, Docker Desktop, macOS arm64, egress control on;
logs in `runs/harbor/`):

| `harbor run -p harbor/corewar-hill …` | reward | wall time | cost |
|---|---|---|---|
| `-a oracle` | 1.000 | 1 min 09 | — |
| `-a nop` | 0.000 | 27 s | — |
| `-a opencode -m anthropic/claude-opus-5-5 -k 1` | 0.739 | 5 min 33 (agent 4.1 min) | $0.50 |
| `-a opencode -m anthropic/claude-opus-5-5 -k 4` (4 concurrent trials) | 0.736, 0.732, 0.681, 0.632 | 15 min 45 (agents 4.4–13.6 min) | $2.04 |
| **v4** `-a oracle` | 1.000 | 39 s | — |
| **v4** `-a opencode -m anthropic/claude-opus-5-5 -k 5` (4 concurrent, then 1) | 0.741, 0.740, 0.727, 0.692, 0.666 | 42 min 47 (agents 16.5–32.7 min) | $11.75 |
| **v4.1** (as shipped) `-a oracle`; `-a nop` | 1.000; 0.000 | 49 s; 32 s | — |
| **v4.1** `-a opencode -m openai/gpt-6.1-sol -k 5` (4 concurrent, then 1) | 0.899, 0.835, 0.833, 0.824, 0.817 | agents 45 min (stopped by the time limit) | — |

The first five agent rows are v3 (OC1–OC5), then v4 (C1–C5), then v4.1 (G1–G5). v4.1 changed
only the copy gate, which none of these submissions comes near, and the hidden hill is scored the same way. Per-run details, and which
trial directory is which run, are in `runs/harbor/README.md`.

**v4 = v3 + the clock.** The clock was added after the v3 Harbor runs, in which agents
stopped after 4 minutes saying they had run out of time: an agent with no way to read the
time left could argue the budget was withheld. The reward, the hill, the sparring pool, the
verifier and the rest of the instruction are unchanged (DECISIONS.md).

Every Claude OpenCode trial is flagged `NonZeroAgentExitCodeError`: OpenCode prints an `EPIPE: broken
pipe` error when it starts and exits with code 1 after the agent finishes normally (the
last event of every trial is `step_finish`, reason `stop`). The verifier still runs and the
reward stands. 3 of the 5 GPT-6.1 sol trials are flagged `AgentTimeoutError` instead: they were still
working at the 45-minute limit.
An earlier attempt that failed on an empty API credit balance, before any model call, is
kept in `runs/harbor/opencode-opus-5.5-no-credit` and not counted.

## Two layers: the traps of practice, and the design

Claude Opus 5.5 (v4, C1–C5) and GPT-6.1 sol (v4.1, G1–G5), same instruction, same tools, same 45 minutes, same
hidden hill. Every figure is computed from the Harbor job folders by `exploits/compare_models.py`
(`results/models.md`, with the per-run table).

**On top: three traps of practice. Claude Opus falls into all three; GPT-6.1 sol avoids them.**

| trap | Claude Opus 5.5 (5 runs) | GPT-6.1 sol (5 runs) | the #1 human program |
|---|---|---|---|
| fits the practice set: hidden-hill score minus practice score, final submission | +0.016 to −0.090 (C5: 0.489 → 0.398); C1 and C3 raised practice and lowered the real score | −0.012 to −0.032 | −0.020 |
| polishes one idea: opens with a quick scan (pMARS listing: ≥ 4 of the first 8 instructions are SEQ/SNE/CMP) | 0 of 5 | 4 of 5 | yes (`;strategy qscan -> paper/imp`) |
| stops early: minute of the last accepted submission, of 45 | 12.5–30.5; 12–29 minutes left unused | 43.5–44.6; 3 of 5 runs ended at the 45-minute limit | — |

These are observations on two models, not a mechanism: we do not claim the traps cause Opus's
gap, nor that fixing them is easy.

**Underneath: design. Most of the gap is already there on the opponents the agent can see.**
The hidden-test gap to Toxic splits into the gap already there against the 30 practice opponents and
the extra practice-to-hidden drop beyond Toxic's own (same split as `exploits/overfit_check.py`):

| model | practice score | hidden score | mean hidden gap to Toxic | of which: already in practice | of which: extra drop |
|---|---|---|---|---|---|
| Claude Opus 5.5 | 0.383–0.489 | 0.373–0.399 | 0.097 | 0.090 (92%) | +0.007 (8%) |
| GPT-6.1 sol | 0.442–0.468 | 0.425–0.452 | 0.054 | 0.053 (98%) | +0.001 (2%) |
| Toxic, the #1 human program | 0.507 | 0.487 | | | |

Neither model writes programs that survive like the #1 human program. Over the 15,000 games of the
hidden hill (30 opponents × 500):

| | wins | losses | ties | opponents it loses to more than 100 times |
|---|---|---|---|---|
| Toxic, the #1 human program | 4,033 | 1,167 | 9,800 | 2 |
| GPT-6.1 sol, lowest–highest run | 3,870–5,011 | 3,394–5,913 | 4,076–7,736 | 13–25 |
| Claude Opus 5.5, lowest–highest run | 2,629–5,380 | 3,061–8,111 | 1,785–9,310 | 12–28 |

GPT-6.1 sol wins about as often as Toxic and loses 2.9 to 5.1 times as often. It does
better than Toxic against 7 to 11 of the 30 opponents, depending on the run. The largest gaps
(mean losses over the GPT-6.1 sol runs, out of 500; strategies are the opponents' own `;strategy` lines):

| opponent | strategy | Toxic losses | GPT-6.1 sol losses, per run |
|---|---|---|---|
| Alladin's Cave | pswitch stone, CLP, one-shot dclear, and one-shot spl/dat wiper | 6 | 311, 314, 219, 235, 260 |
| Crimp | small cmp scanner | 14 | 310, 327, 210, 227, 249 |
| vamp 0.2b | vamp/scan->s/d-clear | 14 | 270, 280, 202, 263, 210 |
| vamps are back 0.2 | hybrid vampire/scanner | 61 | 260, 304, 261, 306, 262 |
| Rave | Carpet-bombing scanner based on Agony and Medusa's | 3 | 279, 258, 157, 148, 154 |

Most of these scan for their opponent. Toxic's strategy line is `qscan -> paper/imp`; no GPT-6.1 sol
strategy line describes imps of its own (G5's mentions only anti-imp bombs, aimed at the opponent's).
That is a hypothesis for the survival gap, not something we have tested.

**GPT-6.1 sol did not copy.** Copy check of the final submissions (thresholds 0.80 exact, 0.90
structural): at scoring, highest exact similarity 0.429 (retroq), highest structural
0.594 (hector2). Rechecked with the current, stricter gate: highest structural
0.793 (G2, leprechaunonspeed); the short-warrior rule flags none.

**Brute force is not what is happening.** The runs test 484–1,469 distinct programs each
(GPT-6.1 sol; Claude Opus 165–616), at most about 1,500, against
10^140 possible 12-line programs.

**How the GPT-6.1 sol runs ended.** 3 of the 5 were stopped by Harbor's 45-minute agent limit
(`AgentTimeoutError`); the others (G4, G5) exited by themselves at 44.9 and 43.8 minutes. The verifier scored the last accepted
submission in every case, as it does for any run.

## What this measures, and what it doesn't

It measures a skill real coding needs and most benchmarks miss: turning the cases you can test into
a design that wins on the ones you can't.

- **Measures:** writing code that stays robust against hidden tests (30 opponents it never sees);
  choosing between several designs; knowing when to stop.
- **Does not measure:** reading a large codebase, fixing bugs, using APIs, understanding a vague
  request. The programs are under 100 instructions, in a toy language.
- **Not shown:** that its ranking of models follows their ranking on real tasks. With two models,
  we cannot say. To test it: run 5 or 6 models, then compare with a benchmark of real tasks such as
  SWE-bench.

## How the environment works

```
┌──────────── agent container (main) ─────────────┐     ┌────── MCP sidecar "arena" ──────┐
│ OpenCode / any Harbor agent                     │ MCP │ get_rules  list_sparring (ids)  │
│ /app/bin/pmars   /app/doc (+ strategy primer)   │────▶│ battle  battle_custom           │
│ /app/tools/spar.py  /app/tools/battle.py        │     │ submit (last accepted counts)   │
│ /app/submission.red (fallback)                  │     │ status · clock  → /results/*    │
└──── network: allowlist (model APIs only) ──────┘     │ 30 sparring warriors, black box │
                                                         └──────────────┬──────────────────┘
          artifacts (re-created at their source paths in the verifier): │
          /results/submission.red, events.jsonl, history/, /app/submission.red
                                                                         ▼
                ┌──── verifier container (separate, no network) ────────────────────┐
                │ hidden hill (30) · near-copy gate (581 published warriors)        │
                │ battle-context assembly · sanitised source · pMARS as `nobody`    │
                │ → /logs/verifier/reward.txt  +  details.json                      │
                └───────────────────────────────────────────────────────────────────┘
```

**Integrity.** The agent never sees hill or sparring code or names, and gets no hill
feedback. Each of the following scores 0 and has a regression case in `make exploits`:
- copies of published warriors, including padded, retuned or embedded copies;
- assembly-context tricks (`WARRIORS` / `ROUNDS`);
- pMARS hangs and oversized files;
- planted files in `/logs/artifacts`.

The oracle reaches exactly 1.0 only through the MCP path. Two adversarial reviews found real
holes (35/100, then 50/100); every one is closed (DECISIONS.md). EXPLOITS.md lists every
attack and the remaining risks.

## Reproduce

```bash
make test        # regression tests: anchors, determinism, sanitiser, gate, assembly context, isolation
make eval        # no Docker: reference, baselines, every recorded run (with standard errors)
make exploits    # exploit and simple-strategy cases through the real verifier, plus stop-early tables
make trajectories  # every submission of every run on its visible pool and on the hidden hill
make overfit     # is the gap just overfitting? visible-pool gap vs extra visible-to-hidden drop
make videos      # check and redraw the videos into media/ (video/README.md)
make task lint   # regenerate harbor/corewar-hill(-public) from sources and lint them
make harbor-reference && make harbor-nop && make harbor-agent MODEL=<provider/model>   # Docker + API key
```

## Files

| file | content |
|---|---|
| FAILURES.md | the evidence for each failure mode, in tables and in the agents' own words |
| EXPLOITS.md | every attack on the reward and what stops it |
| TRAINING.md | training a small model on the environment: Qwen2.5-Coder-7B, expert iteration, base 0.000 → 0.032 on the hidden hill |
| RL_SYNTHESIS.md | all the small-model training runs (expert iteration 7B–32B, GRPO 3B–14B and more): what improves, and what does not |
| DECISIONS.md | what was fixed before the agent runs, and what changed after which review |
| RUN_HARBOR.md | Harbor commands and what to look at in a run |
| CREDITS.md | pMARS (GPL), CodeClash, Digital Red Queen, and the warrior authors |
| LICENSE | MIT, for our own code and documents; the third-party parts listed in CREDITS.md keep their own licences |

| folder | content |
|---|---|
| `harbor/corewar-hill` | the Harbor task as shipped (generated by `build_task.py`; `-public` is the copy without the hidden hill) |
| `arena/` | the rules engine (`core.py`: scoring, copy gate), the MCP server the agent talks to, RULES.md |
| `task_src/` | the agent's instruction, its tools (`spar.py`) and the verifier (`verify.py`) |
| `data/` | the hidden hill (30), the sparring pool (30), the corpus of 581 published warriors, the reference |
| `doc/` | the documents the agent gets: Redcode reference, ICWS '94 standard, strategy primer |
| `pmars/` | the pMARS simulator source (GPL) |
| `runs/` | every recorded agent run: warriors, event logs, submission histories, Harbor job folders |
| `results/` | every table quoted in the docs, generated by the `make` targets |
| `exploits/` | the exploit sweep, stop-early, trajectory and overfitting analyses |
| `baselines/` | simple and textbook warriors |
| `tests/` | the regression tests (`make test`) |
| `training/` | the small-model training (TRAINING.md) |
| `video/`, `media/` | the code that draws the videos, and the videos |

## Related work

- **CodeClash** ([arXiv 2511.00839](https://arxiv.org/abs/2511.00839), Stanford, Princeton and
  Cornell, ICML 2026).
  - LLM agents edit codebases that compete in arenas, Core War among them, over multi-round
    tournaments. The authors report that in one arena the best model lost every round to a
    static expert-written bot.
  - Its CC:Ladder is where our hidden hill, sparring pool and reference come from (CREDITS.md).
  - What differs here: one reward against a fixed hidden hill and a fixed human reference,
    black-box sparring, a gate on published code, and an account of why agents plateau
    (FAILURES.md) rather than a ranking of models.
- **Digital Red Queen** ([arXiv 2601.03335](https://arxiv.org/abs/2601.03335), MIT and Sakana
  AI, January 2026).
  - An LLM evolves Core War warriors round after round, each one against all the earlier ones.
    The evolved warriors become more general against held-out human warriors, and independent
    runs converge on similar strategies.
  - It is a search method that produces warriors. This repository is an environment that
    measures agents, and its training routes change model weights (TRAINING.md).
  - Our second corpus (317 human warriors) comes from its repository.
- **Evolved warriors** ([corewar.info](https://corewar.info/evolve.htm)).
  - Evolutionary search has produced champions on small hills: μGP's White Noise was the first
    machine-made King of the Hill, on the SAL Tiny Hill in 2004.
  - corewar.info notes that evolution had yet to prove itself under larger core settings, such
    as the standard ones this environment uses.
  - Some evolved warriors are in our corpus: Gymnosperm Trickery was produced by the RedRace
    evolver.

## Honest limits

- **How the agent runs were made.** The 17 earlier runs were made with Claude agents in a
  local copy of the arena, with the same instruction, simulator and sparring server
  (reached through `tools/spar.py`, which calls the same MCP tools). Only the ten runs
  in `runs/harbor/` went through Harbor + OpenCode, with Claude Opus 5.5, and the 5 GPT-6.1 sol runs.
- **The copy gate was corrected once after the runs (v4.1).** It had flagged one of the 85
  recorded submissions, run C1's first (a 12-instruction silk paper, replaced 18 minutes
  later), because its structure matched one building block of a larger published warrior.
  The rule given to the agent allows published techniques, so the gate now flags structural
  matches only against half or more of a published warrior. No reported reward changed, and
  every exploit case still scores 0 (DECISIONS.md, EXPLOITS.md).
- **Concurrency.** Runs J1–J3 and then J4–J5 ran concurrently, sharing one 2-CPU machine.
  The Harbor trials ran up to 4 at a time on one laptop (Docker Desktop, macOS arm64), so
  their battles shared its CPUs; each trial was still capped at its own 2 CPUs.
- **Stop-early.** A frontier model's 5-minute draft is already a working warrior. In v4,
  cutting each run at 5 minutes earns 0.63 on average, at 20 minutes 0.74, and the final
  submissions 0.71 (local v3: 0.50, 0.69, 0.67). The reward measures warrior strength, not
  effort; what it shows is that more minutes do not buy these agents strength, and in two
  v4 runs they cost some. FAILURES.md reads this as the plateau it is.
- **What remains to run.**
  - More models through Harbor + OpenCode; see RUN_HARBOR.md and "What this measures" above.
  - The small-model training (TRAINING.md) ran once: Qwen2.5-Coder-7B goes from 0.000 to
    0.032 mean reward on the hidden hill (95% CI of the gain +0.027 to +0.037). It learned
    to write valid code and converged on the imp, which the reward pays little.
