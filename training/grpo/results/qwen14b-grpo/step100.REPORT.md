# GRPO report (step100, adapter /out/qwen14b-grpo/final): qwen14b-grpo

Configuration: `{"model": "Qwen/Qwen2.5-Coder-14B-Instruct", "out": "/out/qwen14b-grpo", "max_steps": 100, "prompts_per_step": 8, "num_generations": 8, "micro_batch": 8, "lr": 1e-05, "lora_r": 16, "max_completion": 768, "prompt_style": "mlx_dwarf", "temperature": 0.8, "top_p": 0.95, "top_k": 512, "save_steps": 25, "vllm_memory": 0.3, "workers": 16, "seed": 0, "samples_per_step": 64, "reward": {"rounds": 50, "tie_weight": 0.0}, "versions": {"trl": "1.17.1", "transformers": "5.17.0", "torch": "2.13.0+cu130"}}`

## Training (training pool only; reward = share of rounds won, 0 for copies)

| step | samples | valid | copies | won a round | mean training reward | best |
|---|---|---|---|---|---|---|
| 1 | 64 | 49 | 1 | 34 | 0.0415 | 0.2700 |
| 11 | 64 | 45 | 0 | 37 | 0.0347 | 0.1880 |
| 21 | 64 | 34 | 2 | 27 | 0.0370 | 0.2593 |
| 31 | 64 | 45 | 1 | 34 | 0.0399 | 0.2576 |
| 41 | 64 | 49 | 0 | 43 | 0.0594 | 0.2591 |
| 51 | 64 | 49 | 2 | 43 | 0.0684 | 0.2591 |
| 61 | 64 | 52 | 1 | 45 | 0.0698 | 0.2576 |
| 71 | 64 | 52 | 1 | 50 | 0.0850 | 0.2136 |
| 81 | 64 | 49 | 2 | 44 | 0.0614 | 0.2424 |
| 91 | 64 | 54 | 0 | 46 | 0.0718 | 0.2789 |
| 100 | 64 | 53 | 0 | 45 | 0.0821 | 0.2789 |

## Held-out evaluation hill (never used for training or selection), fresh samples

| model | samples | valid | copies | mean reward | best-of-n reward | share with reward > 0 | mean raw hill score |
|---|---|---|---|---|---|---|---|
| base | 65 | 44 | 0 | 0.0062 | 0.1771 | 0.11 | 0.0401 |
| after GRPO | 65 | 61 | 2 | 0.0218 | 0.1935 | 0.23 | 0.0931 |

Where the reward comes from (structure of the warriors with reward > 0):

| model | Dwarf with other constants | contains the Dwarf loop | other |
|---|---|---|---|
| base | 2 warriors, 53% of the reward | 0, 0% | 5, 47% |
| after GRPO | 7 warriors, 57% of the reward | 0, 0% | 8, 43% |

The reward is 0 for any warrior at or below Dwarf (hill score 0.1475); the raw hill score (points / maximum, copies and invalid samples at 0) also shows progress below that line.

Difference in mean reward: +0.0156 (95% CI +0.0014 to +0.0299, Welch normal approximation)

Mean reward by archetype asked:

| archetype | base | after GRPO |
|---|---|---|
| stone | 0.0164 | 0.0748 |
| paper | 0.0015 | 0.0155 |
| scanner | 0.0000 | 0.0000 |
| stone_imp | 0.0131 | 0.0189 |
| free | 0.0000 | 0.0000 |
