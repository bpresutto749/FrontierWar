## Further runs on a GPU cluster (14–15 November 2026)

Same loop, same reward, same held-out evaluation as above, ported from `training/mlx` to
vLLM 0.11.0 and TRL 0.24.0 (one prompt per archetype, top 25% kept within each archetype).

Settings shared by every run below:
- Qwen2.5-Coder-Instruct, 7B, 14B or 32B; temperature 0.9, top-p 0.95.
- LoRA r = 16 on all linear layers, lr 1e-4, 2 epochs, a fresh adapter each round on the
  samples kept from all rounds so far.
- Training pool at 50 rounds per opponent. Hidden hill at 100 rounds, read once at the end,
  on 120 fresh samples per model (64 for the runs marked †).
- "CI" is the 95% interval on the difference in mean reward (Welch, normal approximation).

### 1. Model size, same protocol, two seeds

| model | rounds × samples | seed A: mean reward, base → final | best | seed B: mean reward, base → final | best |
|---|---|---|---|---|---|
| 7B | 5 × 2040 | 0.000 → 0.030 (CI +0.026 to +0.034) | 0.074 | evaluation still running | |
| 14B | 5 × 2040 | 0.002 → 0.051 (CI +0.038 to +0.061) | 0.222 | 0.004 → 0.037 (CI +0.020 to +0.045) | 0.363 |
| 32B | 4 × 1020 | 0.011 → 0.044 (CI +0.019 to +0.046) | 0.299 | | |
| 32B | 7 × 1020 | 0.011 → 0.082 (CI +0.055 to +0.087) | 0.329 | 0.015 → 0.059 (CI +0.029 to +0.060) | 0.304 |

The two 32B rows of seed A are the same run, read after rounds 3 and 6: the hidden hill was
consulted twice for it. Seed B was read once.

What the final samples are (every final sample file was opened):
- **7B: the imp.** 78 of 120 final samples start executing at `mov 0, 1`, as in the first run,
  with eight times more samples per round.
- **14B and 32B: their own small bombers.** 120 distinct sources per run, 6 to 10 instructions,
  built around `mov.i bomb, @ptr` / `add.ab #step, ptr` / `spl #0, 0`, with no example warrior
  in the prompt. The samples asked for a "paper" score best but are not real replicators.
- **32B, 7 rounds, seed A:** 47 of 120 samples above 0.1 (27 after round 3); median 0.057
  (0.002 after round 3). Seed B: 30 of 120 above 0.1, median 0.017.

### 2. Variants

| variant | model | rounds × samples | mean reward, base → final | best | what the final samples are |
|---|---|---|---|---|---|
| sparring feedback, 2 revision turns | 32B | 4 × 1020 | 0.012 → 0.070 (CI +0.043 to +0.073) | 0.312 | same family as the 32B runs |
| sparring feedback, 2 revision turns | 7B | 5 × 2040 | 0.001 → 0.032 (CI +0.028 to +0.035) | 0.092 | the imp (89 of 120) |
| selection floor at Dwarf's training score | 14B | 5 × 2040 | 0.002 → 0.047 (CI +0.034 to +0.057) | 0.240 | same family as the 14B runs |
| five example warriors in the prompt † | 7B | 6 × 2048 | 0.000 → 0.151 (CI +0.137 to +0.164) | 0.256 | the example stone plus dead code |
| same, nearby seed † | 7B | 6 × 2048 | 0.006 → 0.138 (CI +0.119 to +0.144) | 0.188 | the example stone plus dead code (59 of 64) |
| strategy primer + Dwarf in the prompt † | 7B | 6 × 2048 | no gain | | nothing above Dwarf to train on |
| primer + scripted constant search † | 7B | 5 × 2048 | 0.001 → 0.206 (CI +0.196 to +0.214) | 0.265 | the documentation's Dwarf, constants tuned (64 of 64) |
| same, other seed † | 7B | 5 × 2048 | 0.004 → 0.153 (CI +0.138 to +0.159) | 0.212 | same |
| primer + glossary + constant search † | 7B | 5 × 2048 | 0.005 → 0.137 (CI +0.124 to +0.139) | 0.191 | same |

**Sparring feedback.** After each draft the model is shown the table the agent's `battle` tool
returns (30 sparring warriors, 50 rounds, ids s01–s30), or pMARS's messages when the draft does
not assemble, and writes a new version. The best draft on the sparring pool is kept; the hidden
hill is never involved. Mean sparring score of drafts 0, 1, 2:

| model | base | after training |
|---|---|---|
| 32B | 0.063, 0.047, 0.048 | 0.173, 0.163, 0.156 |
| 7B | 0.002, 0.005, 0.005 | 0.143, 0.135, 0.131 |

Revised drafts score lower than first drafts, before and after training. The assembler
messages do help (32B base: 841, 869, 896 valid drafts of 1020). The 32B final reward is higher
than without feedback at equal rounds (0.070 against 0.044) because the best of three drafts is
kept, not because the model learned to use the table.

**Constant search.** Between rounds, a script changes one to three numbers of the best warriors
so far and keeps a variant that beats its parent on the training pool; the kept variants join
the SFT data. The model then learns to emit the documentation's Dwarf with tuned constants.
This is distillation of a scripted search, not design by the model. The near-copy gate does not
flag these samples.

### 3. What this shows

- **The reward can be climbed, and the gain is reproducible.** Every run with something to
  learn from shows a gain outside the noise, and the second seed confirms it at 14B and 32B.
  The size of the gain varies between seeds (32B: +0.071 and +0.045).
- **Model size matters more than sample count.** The 7B model stays on the imp at any budget
  we tried. The 14B and 32B models write working bombers from the task text alone, and the 32B
  model keeps improving with more rounds (0.044 after round 3, 0.082 after round 6).
- **The cheap strategies are all found, and all pay little.** The imp (about 0.03), a copied
  example (about 0.15), a tuned Dwarf (about 0.2).
- **Giving the small model the agent's feedback does not teach it to design.** This agrees with
  FAILURES.md: the difficulty is design, not tuning or access to information.
- **Nothing approaches the agents.** The best single sample of any run scores 0.36; the agents
  score about 0.70.

### 4. Limits

- The small model writes each warrior from a one-page summary of Redcode and five lines of
  strategy notes. It has none of the agent's longer documents, and no tools except in the
  feedback runs.
- The seed A run at 32B was read on the hidden hill twice.
- The runs with example warriors and with constant search reproduce material they were given;
  their numbers are not evidence of design.
- Tried without effect: a selection floor at Dwarf's score (14B), the glossary in the prompt
  (7B). Counting ties as zero for selection was checked offline on 331 scored samples and
  picked worse warriors for the hidden hill, so it was not run.

**Not done:** policy-gradient training (for example GRPO); a newer model of similar size
(Qwen3.6-27B needs a more recent vLLM than the one installed).
