# Real Harbor runs of `harbor/corewar-hill`

Harbor 0.25.0, Docker Desktop on macOS arm64, egress control on, 14 November 2026. Each
directory is an unmodified Harbor job directory, except that the local user name in paths was
replaced by `USER` and OpenCode's internal git snapshots (`agent/opencode/xdg-data/opencode/snapshot`)
were left out. No API key appears in any file.

| directory | command | result |
|---|---|---|
| `oracle/` | `-a oracle` | reward 1.000 |
| `nop/` | `-a nop` | reward 0.000 |
| `opencode-opus-5.5-no-credit/` | `-a opencode -m anthropic/claude-opus-5-5 -k 1` | not a run: the API refused the first call (empty credit balance); no model output; not counted |
| `opencode-opus-5.5-run1/` | same, `-k 1` | OC1 |
| `opencode-opus-5.5-runs2-5/` | same, `-k 4` | OC2–OC5 |
| `v4-oracle/` | v4 (clock added), `-a oracle` | reward 1.000 |
| `v4-opencode-opus-5.5/` | v4, `-a opencode -m anthropic/claude-opus-5-5 -k 5` | C1–C5 |
| `v4.1-oracle/` | v4.1 (copy-gate correction), `-a oracle` | reward 1.000 |
| `v4.1-nop/` | v4.1, `-a nop` | reward 0.000 |
| `v4-opencode-gpt-6.1/` | v4.1, `-a opencode -m openai/gpt-6.1-sol -k 5` | G1–G5 |

| run | trial directory | agent minutes | reward | hidden-hill score | cost |
|---|---|---|---|---|---|
| OC1 | `opencode-opus-5.5-run1/corewar-hill__mDmMtQB` | 4.1 | 0.739 | 0.398 | $0.50 |
| OC2 | `opencode-opus-5.5-runs2-5/corewar-hill__FjYrU8F` | 13.6 | 0.736 | 0.397 | $0.39 |
| OC3 | `opencode-opus-5.5-runs2-5/corewar-hill__yztouhA` | 5.8 | 0.732 | 0.396 | $0.57 |
| OC4 | `opencode-opus-5.5-runs2-5/corewar-hill__63vBycW` | 4.4 | 0.632 | 0.362 | $0.52 |
| OC5 | `opencode-opus-5.5-runs2-5/corewar-hill__bJ7ph5p` | 13.2 | 0.681 | 0.378 | $0.55 |

Mean reward 0.704 (95% CI 0.65–0.76, t with 4 degrees of freedom).

**v4 (shipped: a clock in every server reply), C1–C5**, numbered by the start of their agent
phase (C5 waited for a free slot):

| run | trial directory | agent minutes | reward | hidden-hill score | cost |
|---|---|---|---|---|---|
| C1 | `v4-opencode-opus-5.5/corewar-hill__vYa5MUj` | 32.7 | 0.666 | 0.373 | $3.06 |
| C2 | `v4-opencode-opus-5.5/corewar-hill__xtDXjV4` | 22.9 | 0.741 | 0.399 | $2.22 |
| C3 | `v4-opencode-opus-5.5/corewar-hill__47Js9Lc` | 29.8 | 0.692 | 0.382 | $1.60 |
| C4 | `v4-opencode-opus-5.5/corewar-hill__RNStjor` | 24.1 | 0.727 | 0.394 | $2.52 |
| C5 | `v4-opencode-opus-5.5/corewar-hill__X7kqQnj` | 16.5 | 0.740 | 0.398 | $2.35 |

Mean reward 0.713 (95% CI 0.67–0.75). `final-v4/run_C1.red` … `run_C5.red` are copies of the
scored submissions. OC2–OC5 are numbered by
the start of their agent phase. All five trials are flagged `NonZeroAgentExitCodeError`
(OpenCode's `EPIPE` at start-up, exit code 1 after a normal `step_finish`); the verifier ran
in every one.

`final/run_OC1.red` … `run_OC5.red` are copies of the five scored submissions (`make eval` scores them).

In each trial directory: `verifier/reward.txt` and `verifier/details.json` (the score),
`artifacts/events.jsonl` and `artifacts/history/` (every battle and submission), and
`agent/opencode.txt` (the full OpenCode event stream, including the agent's final report).

**v4.1, GPT-6.1 sol (`openai/gpt-6.1-sol` through OpenCode), G1–G5**, `-a opencode -m openai/gpt-6.1-sol -k 5`
(4 concurrent, then 1), 15 November 2026, numbered by the start of their agent phase. Copied from the
user's job folder `jobs/2026-11-15__02-52-18/` with the user name replaced by `USER`; OpenCode's git
snapshots and its session database (`opencode.db`, up to 78 MB per trial) were left out:
`agent/trajectory.json` and `agent/opencode.txt` keep the whole session.

| run | trial directory | agent minutes | reward | hidden-hill score | how it ended |
|---|---|---|---|---|---|
| G1 | `v4-opencode-gpt-6.1/corewar-hill__kGJPs6d` | 45.0 | 0.899 | 0.452 | AgentTimeoutError |
| G2 | `v4-opencode-gpt-6.1/corewar-hill__oVzqKdF` | 45.0 | 0.817 | 0.425 | AgentTimeoutError |
| G3 | `v4-opencode-gpt-6.1/corewar-hill__sSVg7T6` | 45.0 | 0.833 | 0.430 | AgentTimeoutError |
| G4 | `v4-opencode-gpt-6.1/corewar-hill__ULF7YNr` | 44.9 | 0.824 | 0.427 | NonZeroAgentExitCodeError |
| G5 | `v4-opencode-gpt-6.1/corewar-hill__cu8fgqp` | 43.8 | 0.835 | 0.431 | NonZeroAgentExitCodeError |

Mean reward 0.842. Comparison with C1–C5 and Toxic: `exploits/compare_models.py` → `results/models.md`.

Reproduce the trajectory table (`results/trajectories_harbor.md`):

```bash
make trajectories   # v3: runs/harbor/start_times.txt, v4: runs/harbor/start_times_v4.txt
```
