# GRPO report (step150, adapter /out/qwen7b-grpo-seed1/final): qwen7b-grpo-seed1

Configuration: `{"model": "Qwen/Qwen2.5-Coder-7B-Instruct", "out": "/out/qwen7b-grpo-seed1", "max_steps": 150, "prompts_per_step": 8, "num_generations": 8, "micro_batch": 8, "lr": 1e-05, "lora_r": 16, "max_completion": 768, "prompt_style": "mlx_dwarf", "temperature": 0.8, "top_p": 0.95, "top_k": 512, "save_steps": 25, "vllm_memory": 0.3, "workers": 16, "seed": 1, "samples_per_step": 64, "reward": {"rounds": 50, "tie_weight": 0.0}, "versions": {"trl": "1.17.1", "transformers": "5.17.0", "torch": "2.13.0+cu130"}}`

## Training (training pool only; reward = share of rounds won, 0 for copies)

| step | samples | valid | copies | won a round | mean training reward | best |
|---|---|---|---|---|---|---|
| 1 | 64 | 44 | 1 | 22 | 0.0230 | 0.2576 |
| 16 | 64 | 37 | 0 | 25 | 0.0164 | 0.2380 |
| 31 | 64 | 42 | 0 | 33 | 0.0340 | 0.2576 |
| 46 | 64 | 46 | 2 | 34 | 0.0435 | 0.2593 |
| 61 | 64 | 50 | 0 | 43 | 0.0431 | 0.2576 |
| 76 | 64 | 56 | 0 | 53 | 0.0909 | 0.2593 |
| 91 | 64 | 54 | 4 | 46 | 0.0653 | 0.2576 |
| 106 | 64 | 57 | 1 | 50 | 0.0820 | 0.2593 |
| 121 | 64 | 44 | 0 | 41 | 0.0644 | 0.2593 |
| 136 | 64 | 51 | 1 | 49 | 0.0401 | 0.1791 |
| 150 | 64 | 52 | 3 | 47 | 0.0635 | 0.2576 |

## Held-out evaluation hill (never used for training or selection), fresh samples

| model | samples | valid | copies | mean reward | best-of-n reward | share with reward > 0 | mean raw hill score |
|---|---|---|---|---|---|---|---|
| base | 65 | 39 | 1 | 0.0034 | 0.1771 | 0.03 | 0.0141 |
| after GRPO | 65 | 60 | 1 | 0.0228 | 0.1771 | 0.23 | 0.0868 |

Where the reward comes from (structure of the warriors with reward > 0):

| model | Dwarf with other constants | contains the Dwarf loop | other |
|---|---|---|---|
| base | 1 warriors, 80% of the reward | 0, 0% | 1, 20% |
| after GRPO | 7 warriors, 74% of the reward | 0, 0% | 8, 26% |

The reward is 0 for any warrior at or below Dwarf (hill score 0.1475); the raw hill score (points / maximum, copies and invalid samples at 0) also shows progress below that line.

Difference in mean reward: +0.0194 (95% CI +0.0051 to +0.0337, Welch normal approximation)

Mean reward by archetype asked:

| archetype | base | after GRPO |
|---|---|---|
| stone | 0.0136 | 0.0844 |
| paper | 0.0000 | 0.0000 |
| scanner | 0.0000 | 0.0000 |
| stone_imp | 0.0000 | 0.0103 |
| free | 0.0034 | 0.0193 |
