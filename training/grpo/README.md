# Route 3: GRPO on Modal (reinforcement learning on the environment's reward)

Routes 1 and 2 (TRAINING.md, training/mlx) use the score only to choose which samples to
imitate: expert iteration keeps the best quarter and fine-tunes on it. Here the score of
every sample is the learning signal. For each prompt the model writes a group of 8
warriors; GRPO raises the probability of the ones that scored above the group's mean and
lowers the others. That is on-policy RL with a policy gradient, one update per 64 samples.

**Status: first run (200 steps, Modal H100) started on 15 November 2026 at 03:40.** Results
will go to REPORT.md in the run directory and to TRAINING.md.

## What runs

| file | role |
|---|---|
| `reward.py` | the training reward: share of rounds won on the training pool (30 sparring + 60 training-hill warriors, 50 rounds each), 0 if the sample does not assemble or is a copy |
| `train.py` | TRL `GRPOTrainer`: Qwen2.5-Coder-7B-Instruct with a LoRA adapter (r = 16), vLLM generation on the same GPU, 8 prompts x 8 samples per step, every scored sample written to `samples.jsonl` |
| `evaluate.py` | after training, once: 64 fresh samples from the base model and 64 from the adapter, scored on the hidden hill with the environment's reward (100 rounds, as route 1), REPORT.md |
| `probe.py` | before training: valid and winning samples of the base model for each prompt and sampling setting |
| `modal_app.py` | the same on a Modal A100 80 GB (or H100 with `GRPO_GPU=H100`) with 16 CPU cores for pMARS |

```bash
pip install modal && modal setup
modal run training/grpo/modal_app.py::probe                          # base model: valid / winning samples per prompt
modal run training/grpo/modal_app.py::smoke                          # 2 steps: checks the loop, time per step, base reward
GRPO_GPU=H100 modal run --detach training/grpo/modal_app.py::train --run qwen7b-grpo --max-steps 200
modal app logs corewar-grpo                                          # one JSON line per step
modal run training/grpo/modal_app.py::evaluate --run qwen7b-grpo
modal volume get corewar-grpo qwen7b-grpo training/grpo/runs/
```

Without Modal, `train.py` and `evaluate.py` run on any machine with one 80 GB GPU (`pip
install trl==1.17.1 vllm==0.31.0 peft datasets`, then `make -C pmars pmars`).

## Choices, and why

- **Reward: rounds won, not points.** The environment's reward counts a tie as 1 point and
  a win as 3; it is unchanged and is what `evaluate.py` measures. As a training signal from
  scratch, points have a cheap optimum: the one-line imp ties most rounds and kills nothing.
  On the training pool it scores 0.215 in points, more than most base-model samples, and
  route 1 converged on it. In wins, the imp is worth 0.022 and Dwarf 0.197. Base-model
  samples (64, from another prompt) spread from 0 to 0.26, and 31% win at least one round,
  so the groups have the variance GRPO needs. `--tie-weight` (0 to 1) puts ties back in.
- **Copies earn 0,** with the verifier's gate plus the short-warrior rule of
  `training/common.py`: without that rule, a published 3-to-5-instruction warrior followed by
  dead code passes the gate, and RL would find it.
- **Prompt: the MLX run's, plus the documentation's Dwarf as a syntax example; sampling at
  temperature 0.8, top_p 0.95** (top_k 512, which TRL requires with top_p < 1). GRPO learns
  only from groups whose rewards differ, so the prompt was chosen by `probe.py` on the base
  model (60 samples each):

  | prompt | sampling | valid | won a round | best training reward |
  |---|---|---|---|---|
  | MLX run's (`training/mlx/prompts.py`) | T 1.0 | 8 | 1.7% | 0.002 |
  | MLX run's | T 0.8, top_p 0.95 | 24 | 13% | 0.031 |
  | MLX run's + Dwarf | T 1.0 | 17 | 15% | 0.257 |
  | **MLX run's + Dwarf** | **T 0.8, top_p 0.95** | **36** | **35%** | 0.196 |
  | route 1's (task + full Redcode reference, 7,640 tokens) | T 1.0 | 11 | 3.3% | 0.061 |
  | route 1's | T 0.8, top_p 0.95 | 29 | 5% | 0.027 |

  One archetype per prompt in turn (stone, paper, scanner, stone/imp, free). The cost of the
  Dwarf: it is a published warrior, so a copy scores 0, but a retuned Dwarf passes the gate
  and wins rounds (Dwarf itself: 0.197 in wins on the training pool). Training may drift
  towards Dwarf variants; on the hidden hill Dwarf is the zero point, and the evaluation opens
  the final warriors to check.
- **No KL penalty (beta = 0), TRL's default loss.** Learning rate 1e-5 for the adapter.

## Cost and time

Modal lists an A100 80 GB at $0.000694/s (about $2.50/h), an H100 at $0.001097/s (about
$3.95/h; it needs a payment method on the account) and a CPU core at $0.0000131/s (16
cores: about $0.75/h). On an H100, the smoke run (MLX prompt, T 1.0, few valid samples) took
about 30 s per step after a 2-3 minute start; steps with more valid warriors take longer,
since every valid warrior plays 4,500 rounds. The first run (MLX prompt + Dwarf, T 0.8) takes
about 40 s per step: 200 steps in about 2 h 15 min, about $11.

## Agentic prototype (`agent.py`): not working yet

The real task is agentic: the agent tests drafts with the `spar` tool, reads the results and
revises. `agent.py` is a first step towards training that loop, set aside at 06:00 on
15 November 2026.

- **`--mode tools`**: the model may call `spar` itself (TRL's tool support). On
  Qwen2.5-Coder-7B, no call was ever made. A quarter of the replies wrote a well-formed call,
  but inside a markdown block, as an explanation to the user. This held even with the format
  spelled out in the prompt (2 smoke runs, 256 samples).
- **`--mode two_turn`** (default): the environment runs `spar` on the draft and sends the report
  back as a user message; the model then writes its final warrior, which is rewarded, and the
  report's tokens are masked out of the loss (TRL `rollout_func` with `env_mask`). Generation,
  the spar report and the reward work for all 64 samples of a step. The first optimiser step
  then fails inside TRL (`shuffle_sequence_dict`: CUDA "index out of bounds"), with and without
  TRL's importance-sampling correction. Not debugged further.
- **Left to do**: fix the rollout path, then add a two-turn evaluation on the hidden hill.
