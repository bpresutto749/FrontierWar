# GRPO report (step100, adapter /out/qwen3-8b-grpo/final): qwen3-8b-grpo

Configuration: `{"model": "Qwen/Qwen3-8B", "out": "/out/qwen3-8b-grpo", "max_steps": 100, "prompts_per_step": 8, "num_generations": 8, "micro_batch": 8, "lr": 1e-05, "lora_r": 16, "max_completion": 768, "prompt_style": "mlx_dwarf", "temperature": 0.8, "top_p": 0.95, "top_k": 512, "save_steps": 25, "vllm_memory": 0.3, "workers": 16, "seed": 0, "gate_example": false, "samples_per_step": 64, "reward": {"rounds": 50, "tie_weight": 0.0}, "versions": {"trl": "1.17.1", "transformers": "5.17.0", "torch": "2.13.0+cu130"}}`

## Training (training pool only; reward = share of rounds won, 0 for copies)

| step | samples | valid | copies | won a round | mean training reward | best |
|---|---|---|---|---|---|---|
| 1 | 64 | 55 | 0 | 52 | 0.0611 | 0.2576 |
| 11 | 64 | 52 | 6 | 46 | 0.0359 | 0.1496 |
| 21 | 64 | 52 | 1 | 50 | 0.0795 | 0.2576 |
| 31 | 64 | 53 | 0 | 53 | 0.0773 | 0.2576 |
| 41 | 64 | 57 | 1 | 56 | 0.0901 | 0.2576 |
| 51 | 64 | 56 | 6 | 47 | 0.0999 | 0.2576 |
| 61 | 64 | 61 | 0 | 61 | 0.0888 | 0.2576 |
| 71 | 64 | 62 | 7 | 55 | 0.0813 | 0.2193 |
| 81 | 64 | 59 | 5 | 52 | 0.1150 | 0.2576 |
| 91 | 64 | 58 | 0 | 57 | 0.1446 | 0.2576 |
| 100 | 64 | 63 | 1 | 60 | 0.1439 | 0.2576 |

## Held-out evaluation hill (never used for training or selection), fresh samples

| model | samples | valid | copies | mean reward | best-of-n reward | share with reward > 0 | mean raw hill score |
|---|---|---|---|---|---|---|---|
| base | 65 | 53 | 6 | 0.0228 | 0.1771 | 0.15 | 0.0633 |
| after GRPO | 65 | 60 | 1 | 0.0423 | 0.1771 | 0.31 | 0.1117 |

Where the reward comes from (structure of the warriors with reward > 0):

| model | Dwarf with other constants | contains the Dwarf loop | other |
|---|---|---|---|
| base | 6 warriors, 72% of the reward | 0, 0% | 4, 28% |
| after GRPO | 13 warriors, 84% of the reward | 2, 12% | 5, 5% |

The reward is 0 for any warrior at or below Dwarf (hill score 0.1475); the raw hill score (points / maximum, copies and invalid samples at 0) also shows progress below that line.

Difference in mean reward: +0.0195 (95% CI -0.0030 to +0.0419, Welch normal approximation)

Mean reward by archetype asked:

| archetype | base | after GRPO |
|---|---|---|
| stone | 0.0817 | 0.1771 |
| paper | 0.0253 | 0.0000 |
| scanner | 0.0000 | 0.0027 |
| stone_imp | 0.0000 | 0.0316 |
| free | 0.0070 | 0.0000 |
