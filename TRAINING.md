# TRAINING.md — using the environment to make agents better

The environment produces a dense, exact, cheap reward: a few seconds per warrior on 2
cores. It also has a clean train/test split.

## Data separation

| set | warriors | used for |
|---|---|---|
| hidden evaluation hill | 30 (`data/hill`) | final measurement only, once |
| sparring pool | 30 (`data/sparring`) | the agent's visible opponents, and part of the training reward |
| training hill | 60 (`training/train_hill`) | the rest of the training reward |

The training hill is built by `training/make_train_hill.py` from the 581-warrior public
corpus. It excludes:
- every hill warrior and every warrior of both sparring pools;
- every relative of those warriors (similarity ≥ 0.6, stricter than the 0.8 gate);
- duplicates.

That leaves 401 eligible warriors. The 60 are sampled from them with a fixed seed.

**How well each pool predicts the hidden hill** (`training/check_proxy.py` →
`results/proxy_check.md`, 31 recorded final warriors, 100 rounds):

| pool | all warriors: Pearson / Spearman | agent-level warriors (hidden ≥ 0.30, n = 19): Pearson / Spearman |
|---|---|---|
| sparring (30) | 0.98 / 0.92 | **0.83 / 0.66** |
| training hill (60) | 0.94 / 0.82 | 0.39 / 0.28 |
| earlier 10-warrior pool | 0.94 / 0.87 | 0.57 / 0.49 |

The training reward therefore combines the sparring pool, which ranks agent-level warriors
well, with the training hill, which adds breadth. The hidden hill is never used for training
or selection.

## Route 1: small model, expert iteration (`training/`)

**Summary of all training runs (expert iteration on a GPU cluster, 7B to 32B, and GRPO):
`RL_SYNTHESIS.md`.** The cluster runs are detailed in `training/CLUSTER_RUNS.md`.

```
bash training/run_expert_iteration.sh Qwen/Qwen2.5-Coder-7B-Instruct 3 256
```

Each round:
1. **`generate.py`** samples 256 warriors with vLLM. The prompt is the task plus the Redcode
   reference.
2. **`score.py`** scores them on the training reward pool.
3. **`select_sft.py`** keeps the top 25% of the valid, original, de-duplicated samples.
   Training never rewards a near-copy of any of the 581 published warriors, the same rule as
   the verifier, so the model cannot learn to regurgitate.
4. **`sft_lora.py`** fine-tunes a LoRA (r = 16) on the kept samples, which then generates
   the next round.

At the end, the script draws 64 fresh samples from the base model and 64 from the final
adapter. It scores both once on the hidden hill and writes a report with the mean reward,
the best-of-64 and a 95% interval on the difference (`report.py`).

**Run: Qwen2.5-Coder-7B-Instruct, 4 rounds × 256 samples** (`bash
training/run_expert_iteration.sh Qwen/Qwen2.5-Coder-7B-Instruct 3 256`, on a friend's GPU,
14 November 2026). Every file the run wrote, except the raw generation dumps, is in
`training/results/qwen2.5-coder-7b-instruct/` (`REPORT.md`, logs, scored samples, SFT sets).

| round | samples | valid | published copies | mean training score | best training score |
|---|---|---|---|---|---|
| r0 (base model) | 256 | 81 | 0 | 0.007 | 0.216 |
| r1 | 256 | 139 | 4 | 0.062 | 0.222 |
| r2 | 256 | 207 | 0 | 0.161 | 0.220 |
| r3 | 256 | 218 | 1 | 0.175 | 0.219 |

(The "published copies" column was counted with the v4 gate, before the v4.1 correction.)

Hidden hill, 64 fresh samples per model, scored once (100 rounds per opponent):

| model | valid | mean reward | best-of-64 reward | samples above Dwarf |
|---|---|---|---|---|
| base | 24 / 64 | 0.000 | 0.000 | 0 / 64 |
| after expert iteration | 53 / 64 | **0.032** | 0.060 | 49 / 64 |

Difference in mean reward: **+0.032, 95% CI [+0.027, +0.037]** (Welch, normal
approximation).

**What it learned, read plainly.** The gain is real and outside the noise, but it is small,
and the reason is visible in the samples:
- **It learned to write code that assembles:** 24 of 64 valid samples before, 53 after.
  Most base samples were `DAT` lines that die at once.
- **It converged on the imp.** 47 of the 53 valid final samples start executing at
  `mov 0, 1`, the one-line imp that copies itself forward forever, followed by dead code.
  The imp never kills anything and scores only through ties. Rescored at 500 rounds, the
  five best final samples reach hidden-hill 0.161–0.169, against 0.160 for a bare
  `mov 0, 1`.
- **The best training score did not move** (0.216 → 0.219): expert iteration pulled the mean
  of the model up to its own best-of-256, as it is designed to, and found nothing beyond it.

**What this shows about the environment.**
- **The reward has a gradient from zero** that a 7B model can climb with 1,024 samples and
  four LoRA updates.
- **The cheapest strategy the reward allows is worth little.** Training found the imp, the
  textbook degenerate warrior, and the reward pays it 0.04–0.06. Under the earlier imp
  anchor this run would have shown no gain at all; the anchor was moved to Dwarf before
  this run, for the reason given in the README, and both readings are stated here.
- **The distance to the frontier agents (0.70) and the reference (1.0) is the room left.**
  Getting past the imp needs a model that can write a working bomber, paper or scanner from
  the reference text, which the 7B model could not do in 4 rounds.

**Not done:** a larger model, more rounds, or the strategy primer in the prompt.

## Route 2: telling a frontier agent what went wrong (run G, and the primer)

**Run G (version 1)** received `task_src/lessons.md`, appended to the same instruction. Its
four points are general:
- treat sparring as validation;
- build an archetype test set with random positions;
- composites dominate hills;
- use the whole budget.

It contains no warrior code and no hidden-hill content.

| | reward |
|---|---|
| G | 0.716 |
| fresh Opus runs of the same version (A, B, C, D2, E2) | 0.661–0.936 (mean 0.746) |

G followed the method advice and built a composite, which no fresh v1 run did. It still
stopped at 28 of 45 minutes.

**Versions 2 and 3** give every run `doc/strategy_primer.md`, which carries the same
general advice. Their means are 0.595 and 0.671, and the failure modes of FAILURES.md
persist.

Prompting changes the agents' process, not their result. That is the case for using the
environment as a training signal (Route 1).

## Route 3: reinforcement learning with GRPO (`training/grpo/`)

First runs on 15 November 2026: results in `training/grpo/RESULTS.md` (updated as runs finish),
method in `training/grpo/README.md`. Main run: on the hidden hill, the mean reward of
Qwen2.5-Coder-7B goes from 0.0034 to 0.0525 after 200 steps (95% CI of the gain +0.030 to
+0.068), but 91% of that reward comes from variants of the Dwarf shown in the prompt. A
replicate (another seed) gains less but significantly (0.023 at step 150), and a control without
the Dwarf in the prompt gains 0.004, none of it from Dwarf shapes. The score of every
sample is the gradient (GRPO, Qwen2.5-Coder-7B-Instruct + LoRA, on a Modal H100), instead of
choosing which samples to imitate. The training reward counts rounds won on the training pool,
so the imp, which ties without killing, is worth 0.022 instead of 0.215. The evaluation is
unchanged: the environment's reward on the hidden hill, once, base against trained.

**A gate rule added for training only (15 November 2026).** The verifier's containment test
needs 6+ instructions, so a published warrior of 3 to 5 instructions followed by dead code
passes the gate: Gymnosperm Trickery plus 3 `dat` lines earns 0.577 at 500 rounds. Every
training scorer (`training/common.py`, `training/mlx/score.py`, `training/grpo/reward.py`) now
treats such a sample as a copy. No agent warrior in `runs/` (94 distinct) and no published
warrior against another (564) is flagged by it. The results above were scored before this
rule; the verifier does not apply it yet.

## What a trained agent should learn here

The environment exposes the failure modes directly, so a training run can target them:

| failure | what exposes it |
|---|---|
| plateau below expert level | the reward, and the sparring score against the reference's 0.507 |
| single-archetype convergence | the per-opponent breakdown in `details.json` |
| optimising the visible set | the sparring-vs-hidden comparison over the submission history |
| early stopping | the timestamped event log `events.jsonl` |
