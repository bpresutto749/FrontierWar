# GRPO report (step150, adapter /out/qwen7b-grpo-nodwarf/final): qwen7b-grpo-nodwarf

Configuration: `{"model": "Qwen/Qwen2.5-Coder-7B-Instruct", "out": "/out/qwen7b-grpo-nodwarf", "max_steps": 150, "prompts_per_step": 8, "num_generations": 8, "micro_batch": 8, "lr": 1e-05, "lora_r": 16, "max_completion": 768, "prompt_style": "mlx", "temperature": 0.8, "top_p": 0.95, "top_k": 512, "save_steps": 25, "vllm_memory": 0.3, "workers": 16, "seed": 0, "samples_per_step": 64, "reward": {"rounds": 50, "tie_weight": 0.0}, "versions": {"trl": "1.17.1", "transformers": "5.17.0", "torch": "2.13.0+cu130"}}`

## Training (training pool only; reward = share of rounds won, 0 for copies)

| step | samples | valid | copies | won a round | mean training reward | best |
|---|---|---|---|---|---|---|
| 1 | 64 | 33 | 2 | 3 | 0.0009 | 0.0349 |
| 16 | 64 | 33 | 0 | 8 | 0.0038 | 0.0442 |
| 31 | 64 | 30 | 0 | 8 | 0.0060 | 0.1776 |
| 46 | 64 | 19 | 0 | 9 | 0.0064 | 0.1316 |
| 61 | 64 | 35 | 2 | 13 | 0.0072 | 0.1089 |
| 76 | 64 | 25 | 1 | 13 | 0.0084 | 0.1933 |
| 91 | 64 | 35 | 0 | 17 | 0.0085 | 0.0722 |
| 106 | 64 | 45 | 0 | 23 | 0.0179 | 0.2011 |
| 121 | 64 | 26 | 0 | 16 | 0.0171 | 0.1880 |
| 136 | 64 | 37 | 1 | 25 | 0.0159 | 0.1860 |
| 150 | 64 | 40 | 0 | 21 | 0.0143 | 0.0776 |

## Held-out evaluation hill (never used for training or selection), fresh samples

| model | samples | valid | copies | mean reward | best-of-n reward | share with reward > 0 | mean raw hill score |
|---|---|---|---|---|---|---|---|
| base | 65 | 26 | 2 | 0.0000 | 0.0000 | 0.00 | 0.0010 |
| after GRPO | 65 | 42 | 2 | 0.0040 | 0.0552 | 0.11 | 0.0326 |

The reward is 0 for any warrior at or below Dwarf (hill score 0.1475); the raw hill score (points / maximum, copies and invalid samples at 0) also shows progress below that line.

Difference in mean reward: +0.0040 (95% CI +0.0010 to +0.0069, Welch normal approximation)

Mean reward by archetype asked:

| archetype | base | after GRPO |
|---|---|---|
| stone | 0.0000 | 0.0050 |
| paper | 0.0000 | 0.0055 |
| scanner | 0.0000 | 0.0036 |
| stone_imp | 0.0000 | 0.0042 |
| free | 0.0000 | 0.0014 |
