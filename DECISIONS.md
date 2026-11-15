# DECISIONS.md — what was fixed when, and what changed after results came in

These notes come from the session log. They are written so a reviewer can check that the
gap was not tuned after the fact.

## Fixed before any agent run on this task

- **Hidden hill.** Every 8th warrior of the CodeClash CC:Ladder Elo ranking, from
  rank 11 to rank 243, weakest first: 30 warriors (`data/split.json`).
- **Sparring pool.** Every 24th warrior from rank 7: 10 warriors, disjoint from the hill.
- **Reference.** Toxic, the Elo #1 of the 264 humans. It was chosen from the external
  ranking, not from our hill. Measured on our hill, it is not the strongest human: the
  top 8 humans score 0.475–0.532. We kept the pre-declared choice.
- **Score.** Standard King-of-the-Hill points (3 per win, 1 per tie), pMARS defaults,
  fixed position series.
- **Probes before the agents.** The CodeClash LLM warriors and the trivial warriors were
  measured first, to check the ceiling: LLM warriors 0.08–0.34, reference 0.48.

## Changed after the first three agent runs (A, B, C), and why

| change | effect on the comparison |
|---|---|
| **Rounds per opponent: 60 → 100.** Runs A–C were told 60. | Deterministic either way; only the precision of the estimate changes. Later raised to 500 (next section); all numbers in this repo now use 500. |
| **Reward rescaled.** `(hill − imp) / (reference − imp)` instead of the raw hill score. | An affine map: no ranking or gap test changes. We did it because a one-line imp collects 0.158 raw from ties, which would make "simple strategies earn little" hard to read. |
| **Copy gate: false positive fixed.** The first gate flagged run B's original warrior as a "copy". Its 40 decoy lines happened to contain the opcode pattern of a short published warrior. | Structural containment was removed. Exact containment was kept. |
| **Copy gate: scope narrowed** (later reversed, see review 2). It zeroed only copies of hill or sparring warriors and reported the rest of the 581-warrior corpus. | At the time we believed the reference would be flagged against its relative Mercenary. Measured with the final gate, Toxic vs Mercenary is exact 0.775, structural 0.88, so it is not flagged. The real conflict is that `toxic.red` itself is in the corpus, which the exact-text exemption of review 2 resolves. |
| **Hill selection rule removed from the agent instruction.** | With internet access, an agent could otherwise reconstruct the hidden hill from the public ladder. |

## Changed after the first adversarial review (35/100), before the version-2 runs

A fresh critic agent broke version 1. Every fix below is covered by a regression case in
`make exploits` or `make test`.

| finding | fix |
|---|---|
| **Fatal.** Harbor re-creates artifacts in a separate verifier at their *source* path. The verifier looked under `/logs/artifacts`, so every submission, the oracle's included, would have scored 0. | Read `/results/submission.red`, then `/app/submission.red`. Never read `/logs/artifacts`, which the agent can write. |
| pMARS predefines `WARRIORS` and `ROUNDS`. A source could assemble as an imp for the copy check and as Halcyon in battle: reward 1.25. | Every check now uses the listing from the exact scoring context. |
| Lightly edited sparring warriors passed the gate (padding removed, one constant changed: rewards 1.04–1.19). 6 of the 10 sparring warriors beat the reference on the hill. | The sparring pool became **black boxes** (ids only, no source, no names). The gate also removes padding and uses contiguous-run containment. |
| The agent phase had public network access, and 6 public warriors not on the hill beat the reference. | Agent phase on an **allowlist** (sidecar + model APIs; extend with `--allow-agent-host`). |
| At 100 rounds, a cosmetic edit that re-draws the `-f` position series moved D2 by up to 0.05 in reward. | **500 rounds** per opponent. The standard error is reported for every score (about ±0.01 in reward). The anchors were recomputed at 500 rounds: imp 0.1650, reference 0.4866. |
| F3 ("the gap concentrates on imp-based opponents") was not supported by the data. | Claim removed. |
| `reward.json` carried non-reward keys, which Harbor aggregates. | Only `reward` and `hill_score` remained; everything else went to `details.json`. Later the challenge required a single number in `reward.txt`, which is what the verifier now writes. |

**What changed for the agent.**
- Sparring warriors became black boxes, reached through MCP or `tools/spar.py`.
- A short public strategy primer (`doc/strategy_primer.md`) was added, so that the
  difficulty cannot be put down to withheld community knowledge.
- Scoring moved to 500 rounds.

Because the agent's environment changed, these changes were followed by new runs: version 2,
`runs/v2-small-pool/`. Runs A–E2 and G (`runs/opus-5.5*`) were made in version 1 and are
kept as earlier evidence, rescored at 500 rounds.

## Changed after the second adversarial review (50/100), before the version-3 runs

| finding | fix |
|---|---|
| Under egress control, Harbor puts every service without explicit networking into the egress sidecar's network namespace, so `arena` would not resolve. The oracle hid this because `solve.sh` also wrote the fallback file. | MCP is now reached on `localhost:8000` in the default (allowlist) task, with a `corewar-hill-public` variant that uses `arena:8000`. `solve.sh` submits only through MCP, and the oracle was verified end to end (MCP submit → sidecar → verifier = 1.0). |
| Published warriors not on the hill beat the reference (forjohn 1.12, maelstrom 1.10). | The gate now covers all 581 published warriors. The only exemption is the reference's exact text, so editing it is gated and reproducing it earns exactly 1.0. Wildcard cloud domains were removed from the allowlist. |
| **"Withheld information."** The 10-warrior sparring pool predicted the hidden hill poorly: r = 0.57 over 19 agent-level final warriors (`results/proxy_check.md`; the review measured 0.05 on the 22 intermediate v2 submissions). The difficulty could be put down to a bad proxy. | **The sparring pool is now 30 warriors drawn from the same ladder as the hill, with the same strength spread** (`data/split.json`). On the same 19 warriors it correlates r = 0.83 with the hidden hill. It stays black-box. |
| A false claim in FAILURES.md: in version 1 the highest sparring score was D2, not B. | Corrected. |
| `os.cpu_count()` sized the battle pool by host CPUs; a timeout counted silently as a loss; the file was read before the size check. | `ARENA_WORKERS` (default 2); one retry with a 4× timeout; size checked first. |
| `submit` rejections revealed sparring membership. | `submit` no longer gates; only the verifier does. |

**What changed for the agent.**
- 30 black-box sparring warriors instead of 10.
- The full-corpus originality rule.

The 10-warrior runs are kept as **version 2** (`runs/v2-small-pool/`). The headline is
**version 3** (`runs/final-env/`), the environment shipped in `harbor/`.

## Changed after all runs were scored: the reward's zero point

| change | effect on the comparison |
|---|---|
| **Zero point: one-line imp → Dwarf.** The zero point moved from a one-line imp (`mov.i #0, 1`, hill 0.1650) to Dwarf (A. K. Dewdney's classic bomber, `doc/example_dwarf.red`, hill 0.1475). This was decided after all 17 runs had been scored, including the five final runs. | **Why:** the imp never kills and scores only through ties. Dwarf is the canonical first warrior and the example the agent is handed, so reward 0 reads "no better than the textbook example". **Effect:** an affine change of the same raw score, so the order of the runs is unchanged. Every reward was recomputed from the stored raw hill scores without rerunning any agent (`exploits/rescore_anchor.py` → `results/rescored_dwarf_anchor.md`). Agents' rewards rise slightly (v3 mean 0.653 → 0.671); the raw-score gap is unchanged. |

## Runs excluded

- **D and E.** Killed at about 14 minutes by an API quota error. Kept in `runs/aborted/`
  and never scored on the hidden hill. They were replaced by D2 and E2 with identical
  instructions.
- **The first Harbor + OpenCode attempt** (`runs/harbor/opencode-opus-5.5-no-credit/`).
  The API refused its first model call (empty credit balance), so no model output exists.
  The next five attempts (OC1, then OC2–OC5 in one `-k 4` job) are all counted.
- **No run was discarded for its score.**

## Added after the Harbor runs (no change to the environment)

- **Five Harbor + OpenCode runs (OC1–OC5)** were added to the results with the task
  exactly as shipped: same `harbor/corewar-hill`, instruction, verifier and anchor. All five
  started after the Dwarf anchor was fixed. They are reported in full; nothing was rerun.
- **`results/stop_early.md` and `results/stop_early_v2.md` were regenerated.** They still
  held imp-anchor rewards from before the zero-point change; the Dwarf-anchor values were
  already in `results/rescored_dwarf_anchor.md`, and the regenerated files now match them.
- **`exploits/trajectories.py` accepts `LABEL=DIR:START`**, so Harbor trial directories
  (all named `artifacts`) get readable labels. The scoring is unchanged.
- **`exploits/overfit_check.py` (`make overfit`) was added after all runs**, to answer the
  objection that the gap is overfitting to the visible pool (FAILURES.md, F3). It only reads
  the stored trajectories and scores the reference; it changes no reward.
- **The reward column of `results/trajectories.md` and `trajectories_v2.md` was rewritten
  with the Dwarf anchor** (`exploits/trajectories.py --rescore`, no battle rerun). It still
  held imp-anchor rewards; the visible and hidden scores are unchanged, byte for byte.

## Changed after the v3 Harbor runs: version 4, a clock

| change | why, and its effect on the comparison |
|---|---|
| **Every arena reply ends with a clock**: minutes used and minutes left of the 45, counted from the agent's first call to the server (`arena/mcp_server.py`; one sentence added to the instruction and to `RULES.md`). | **Why:** in the five v3 Harbor runs the agents stopped after 4–14 minutes, and three said they had run out of time. The agent had no way to read the time left, which a judge could fairly call withheld information. The change gives the agent more information, not less. **Unchanged:** the reward, the anchors, the hidden hill, the sparring pool, the verifier, the copy gate, the 45-minute limit. **Effect:** agents worked 16–33 minutes instead of 4–14; the mean reward went from 0.704 to 0.713. v4 is the shipped version; v3's runs stay in the results. |

The five v4 runs (C1–C5) are one `-k 5` job, reported in full. The v4 oracle run, made
before them to check the rebuilt images, scored 1.000.

## Changed after the v4 runs: version 4.1, a copy-gate correction

| change | why, and its effect on the comparison |
|---|---|
| **Structural containment counts only for whole or half copies.** The structural test (constants removed) used to flag a submission whose structure is contained in any published warrior. It now flags it only when the submission contains a published warrior or reproduces at least half of one (`arena/core.py`, `FRAGMENT_SHARE = 0.5`). The exact test, with constants, is unchanged: a verbatim piece of a published warrior is still a copy. | **Why:** the gate flagged run C1's first submission, a 12-instruction silk paper whose structure matched the paper block of Jack in the Box II, a 51-instruction p-space switcher between a silk paper and a Tornado bomber (exact similarity 0.25). The instruction says that using published ideas and techniques is fine, so this was the gate being stricter than its own rule. **Effect:** the gate is strictly weaker than before, so no score can fall. No final submission had been flagged, so no reported reward changed. All 35 exploit cases give the same results (`results/exploits.md`), and `tests/test_env.py` now checks that a verbatim piece, a retuned half copy and a retuned whole copy are still flagged. The agent's instruction is unchanged. The rebuilt task was checked through Harbor: oracle 1.000, nop 0.000 (`runs/harbor/v4.1-*`). |

## Small-model training

The expert-iteration run (TRAINING.md) used the training reward and prompt exactly as
committed before it ran. Its evaluation on the hidden hill was run once, by the script.
Nothing was rerun or selected after seeing the result.

## Open choices we considered and rejected

| option | why we rejected it |
|---|---|
| A top-heavy hill (the 30 strongest warriors) | It might widen the gap, but choosing it after seeing results would be selection on the test set. |
| A whitelist entry so the reference passes a whole-corpus gate | It would be a special case only the oracle could use. |
| An LLM-evolved reference, Digital Red Queen style | Not reproducible within the event. The human expert is also the more meaningful bar. |

## pMARS: one-entry overflow fixed (14 November 2026, after all runs)

Building pMARS with clang for the Mac training run exposed a bug in `pmars/clparse.c`: the
command-line option table (`OPTNUM` 21) was one entry short, so the last option written
overflowed into the next static variable. gcc builds (every score in this repository, and the
Harbor verifier's) placed something harmless there; a clang build overwrote `useExtRNG` and
crashed. `OPTNUM` is now 32, and `-Dround=pmars_round` avoids the clash between pMARS's global
`round` and the C library's `round()` under clang. Same outputs before and after, gcc and
clang: the reference against Blizzard (200 rounds, fixed series) gives 46/7/147 with the old
gcc build, the new gcc build and the clang build; run C5 against Blizzard at `-F 7253` gives
0/70/30 with all three. `harbor/` was regenerated with the fix (`make task`); the verifier scores nothing differently.

## Three judge-style red-team reviews (reviews 3–5), after all runs were scored

Three independent reviewers, 15 minutes each, tried to break the reward. Fixes, all with
regression cases in `make exploits` (EXPLOITS.md has the details):
- Review 3: short published warriors (Gymnosperm Trickery, 5 instructions) passed the copy gate
  padded (0.52) or with 2 constants nudged (0.57). New rule for the 44 strong short published
  warriors (`data/strong_short.json`).
- Review 4: SUB of an immediate is now normalised as ADD; the oracle's reference file is Toxic
  plus one comment line, so the published Toxic is no longer exempt from the gate.
- Review 5: the short rule requires the step size to match (it had zeroed an honest stone/imp);
  a lone carriage return is now a line break on both sides; the rules given to the agent state
  the short-warrior rule, that position draws depend on the code, and that the run's hard limit
  starts with the run.
No recorded agent submission is flagged by the new rules, so no reported reward changes. The
agent-facing text changed after the runs: the added sentences describe rules the runs were
already scored under (copy gate, positions, time), except the short-warrior rule, which is new
and flags none of their submissions.

## GPT-6.1 sol runs, and the two-level reading (15 November 2026)

Five GPT-6.1 sol runs (`openai/gpt-6.1-sol` through OpenCode, G1–G5) were made on v4.1, after all the
Claude runs and after the task was fixed; nothing in the task, the hidden hill, the sparring pool
or the verifier was changed for them. v4.1 differs from v4 (C1–C5) only in the copy gate, which none
of these submissions comes near (`results/models.md` rechecks all ten with the current gate).
GPT-6.1 sol scores 0.842 (0.817–0.899) against 0.713 for Claude Opus and 1.000 for Toxic, and does not
make the three mistakes documented for Opus. The README and the videos were rewritten after these
runs around two levels: those mistakes, and a design gap that GPT-6.1 sol still shows (it loses 2.9 to
5.1 times as many games as Toxic). This is a reading of two models, not a tested mechanism; the
README says what it does not show.
