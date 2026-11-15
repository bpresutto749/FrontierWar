# GRPO report (step100, adapter /out/gemma4-12b-grpo/final): gemma4-12b-grpo

Configuration: `{"model": "google/gemma-4-12B-it", "out": "/out/gemma4-12b-grpo", "max_steps": 100, "prompts_per_step": 8, "num_generations": 8, "micro_batch": 8, "lr": 1e-05, "lora_r": 16, "max_completion": 768, "prompt_style": "mlx_dwarf", "temperature": 0.8, "top_p": 0.95, "top_k": 512, "save_steps": 25, "vllm_memory": 0.3, "workers": 16, "seed": 0, "samples_per_step": 64, "reward": {"rounds": 50, "tie_weight": 0.0}, "versions": {"trl": "1.17.1", "transformers": "5.17.0", "torch": "2.13.0+cu130"}}`

## Training (training pool only; reward = share of rounds won, 0 for copies)

| step | samples | valid | copies | won a round | mean training reward | best |
|---|---|---|---|---|---|---|
| 1 | 64 | 30 | 0 | 30 | 0.0305 | 0.1480 |
| 11 | 64 | 24 | 0 | 23 | 0.0202 | 0.1096 |
| 21 | 64 | 38 | 0 | 38 | 0.0500 | 0.1558 |
| 31 | 64 | 38 | 0 | 38 | 0.0470 | 0.1482 |
| 41 | 64 | 47 | 0 | 47 | 0.0609 | 0.1771 |
| 51 | 64 | 54 | 0 | 54 | 0.0720 | 0.2022 |
| 61 | 64 | 43 | 0 | 43 | 0.0547 | 0.2080 |
| 71 | 64 | 55 | 0 | 55 | 0.0790 | 0.1662 |
| 81 | 64 | 49 | 0 | 49 | 0.0707 | 0.1891 |
| 91 | 64 | 56 | 0 | 56 | 0.0835 | 0.2633 |
| 100 | 64 | 55 | 0 | 55 | 0.0745 | 0.2576 |

## Held-out evaluation hill (never used for training or selection), fresh samples

| model | samples | valid | copies | mean reward | best-of-n reward | share with reward > 0 | mean raw hill score |
|---|---|---|---|---|---|---|---|
| base | 65 | 44 | 0 | 0.0000 | 0.0000 | 0.00 | 0.0292 |
| after GRPO | 65 | 56 | 0 | 0.0017 | 0.0923 | 0.05 | 0.0754 |

Where the reward comes from (structure of the warriors with reward > 0):

| model | Dwarf with other constants | contains the Dwarf loop | other |
|---|---|---|---|
| base | 0 warriors, 0% of the reward | 0, 0% | 0, 0% |
| after GRPO | 1 warriors, 84% of the reward | 0, 0% | 2, 16% |

The reward is 0 for any warrior at or below Dwarf (hill score 0.1475); the raw hill score (points / maximum, copies and invalid samples at 0) also shows progress below that line.

Difference in mean reward: +0.0017 (95% CI -0.0011 to +0.0045, Welch normal approximation)

Mean reward by archetype asked:

| archetype | base | after GRPO |
|---|---|---|
| stone | 0.0000 | 0.0071 |
| paper | 0.0000 | 0.0000 |
| scanner | 0.0000 | 0.0000 |
| stone_imp | 0.0000 | 0.0014 |
| free | 0.0000 | 0.0000 |
