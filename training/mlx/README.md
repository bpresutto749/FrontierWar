# Expert iteration on a Mac (Apple Silicon, MLX)

The same expert-iteration loop as `training/run_expert_iteration.sh`, on Apple Silicon with
[MLX](https://github.com/ml-explore/mlx-lm): Qwen2.5-Coder-7B-Instruct in 4 bits plus a LoRA
adapter. No GPU server needed.

```bash
bash training/mlx/setup.sh     # once: native pMARS build, .venv-mlx with mlx-lm, model download, checks
bash training/mlx/run.sh       # starts in the background and keeps the Mac awake; log in training/mlx/runs/<name>/run.log
```

Each round: `gen.py` samples N warriors (batched), `score.py` scores them on the training
pool (30 sparring + 60 training-hill warriors, never the hidden hill), `pick.py` keeps the best
quarter **of each archetype** over all rounds so far, and `mlx_lm lora` fine-tunes a fresh
adapter from the base model on them. At the end, base and final adapter each draw fresh samples
that are scored once on the hidden hill, and `report.py` writes `REPORT.md`.

What changed from the first run (GPU, vLLM, TRAINING.md), and why:

| | first run | this run |
|---|---|---|
| prompt | task + the full Redcode reference | task + a compact Redcode reference + the strategy primer's archetypes (no code), shorter so LoRA trains fast on a laptop |
| prompts per round | one | one per archetype (stone, paper, scanner, stone/imp, free), in turn |
| selection | top 25% overall | top 25% within each archetype: the first run collapsed onto the imp, the cheapest strategy the reward allows |
| reply format | free text, code block extracted | the reply starts inside a code block, so every sample is one warrior |

The reward, the gate on copies, the training pool and the held-out evaluation are unchanged.

## Run 2: learning from the environment's feedback

Run 1 trains on one-shot answers: the model never sees a game. The agent in the task does not
work that way: it writes a warrior, runs the battle tool, reads the per-opponent results and
revises. Run 2 trains on that loop, cut to one step:

```bash
bash training/mlx/run_fb.sh    # after run.sh has finished; log in training/mlx/runs/fb-<name>/run.log
```

An episode is: `gen.py` writes a draft; `feedback.py` runs the battle tool on it, with the same
output the agent gets in the task (the table of wins, losses and ties against the 30 sparring
warriors, 100 rounds each, or the assembler's messages if the draft does not assemble);
`revise.py` shows the model its draft and that output and asks for a better version. Both are
scored on the training pool. `pick_fb.py` keeps the best drafts of each archetype and, as
revision examples, the episodes whose revision beats its draft (the loss is on the revision only).
At the end, base model and final adapter each run the same number of fresh episodes on the
hidden hill; the submitted warrior is the revision if its practice score is at least the draft's,
which is what an agent can decide from what it sees. `report_fb.py` reports the draft, the
revision and the submitted warrior, the paired effect of one round of feedback for each model,
and the effect of training.
