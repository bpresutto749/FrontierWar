# GRPO report (step150, adapter /out/qwen3b-grpo/final): qwen3b-grpo

Configuration: `{"model": "Qwen/Qwen2.5-Coder-3B-Instruct", "out": "/out/qwen3b-grpo", "max_steps": 150, "prompts_per_step": 8, "num_generations": 8, "micro_batch": 8, "lr": 1e-05, "lora_r": 16, "max_completion": 768, "prompt_style": "mlx_dwarf", "temperature": 0.8, "top_p": 0.95, "top_k": 512, "save_steps": 25, "vllm_memory": 0.3, "workers": 16, "seed": 0, "samples_per_step": 64, "reward": {"rounds": 50, "tie_weight": 0.0}, "versions": {"trl": "1.17.1", "transformers": "5.17.0", "torch": "2.13.0+cu130"}}`

## Training (training pool only; reward = share of rounds won, 0 for copies)

| step | samples | valid | copies | won a round | mean training reward | best |
|---|---|---|---|---|---|---|
| 1 | 64 | 38 | 10 | 24 | 0.0278 | 0.2576 |
| 16 | 64 | 39 | 5 | 32 | 0.0435 | 0.2593 |
| 31 | 64 | 51 | 2 | 46 | 0.0761 | 0.2593 |
| 46 | 64 | 39 | 5 | 31 | 0.0497 | 0.2038 |
| 61 | 64 | 51 | 2 | 47 | 0.1000 | 0.2593 |
| 76 | 64 | 59 | 6 | 52 | 0.1320 | 0.2593 |
| 91 | 64 | 63 | 2 | 61 | 0.1644 | 0.2593 |
| 106 | 64 | 63 | 4 | 58 | 0.1730 | 0.2593 |
| 121 | 64 | 62 | 1 | 61 | 0.1507 | 0.2593 |
| 136 | 64 | 60 | 3 | 57 | 0.1563 | 0.2576 |
| 150 | 64 | 63 | 2 | 61 | 0.1898 | 0.2593 |

## Held-out evaluation hill (never used for training or selection), fresh samples

| model | samples | valid | copies | mean reward | best-of-n reward | share with reward > 0 | mean raw hill score |
|---|---|---|---|---|---|---|---|
| base | 65 | 32 | 8 | 0.0118 | 0.1771 | 0.09 | 0.0271 |
| after GRPO | 65 | 63 | 0 | 0.0837 | 0.1771 | 0.69 | 0.1623 |

Where the reward comes from (structure of the warriors with reward > 0):

| model | Dwarf with other constants | contains the Dwarf loop | other |
|---|---|---|---|
| base | 5 warriors, 88% of the reward | 1, 12% | 0, 0% |
| after GRPO | 36 warriors, 81% of the reward | 9, 19% | 0, 0% |

The reward is 0 for any warrior at or below Dwarf (hill score 0.1475); the raw hill score (points / maximum, copies and invalid samples at 0) also shows progress below that line.

Difference in mean reward: +0.0718 (95% CI +0.0513 to +0.0923, Welch normal approximation)

Mean reward by archetype asked:

| archetype | base | after GRPO |
|---|---|---|
| stone | 0.0523 | 0.1771 |
| paper | 0.0000 | 0.0639 |
| scanner | 0.0000 | 0.0616 |
| stone_imp | 0.0069 | 0.0694 |
| free | 0.0000 | 0.0463 |
