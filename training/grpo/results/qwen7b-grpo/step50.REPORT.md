# GRPO report (step50, adapter /out/qwen7b-grpo/checkpoint-50): qwen7b-grpo

Configuration: `{"model": "Qwen/Qwen2.5-Coder-7B-Instruct", "out": "/out/qwen7b-grpo", "max_steps": 200, "prompts_per_step": 8, "num_generations": 8, "micro_batch": 8, "lr": 1e-05, "lora_r": 16, "max_completion": 768, "prompt_style": "mlx_dwarf", "temperature": 0.8, "top_p": 0.95, "top_k": 512, "save_steps": 25, "vllm_memory": 0.3, "workers": 16, "seed": 0, "samples_per_step": 64, "reward": {"rounds": 50, "tie_weight": 0.0}, "versions": {"trl": "1.17.1", "transformers": "5.17.0", "torch": "2.13.0+cu130"}}`

## Training (training pool only; reward = share of rounds won, 0 for copies)

| step | samples | valid | copies | won a round | mean training reward | best |
|---|---|---|---|---|---|---|
| 1 | 64 | 29 | 0 | 15 | 0.0105 | 0.2576 |
| 5 | 64 | 34 | 1 | 15 | 0.0131 | 0.2022 |
| 9 | 64 | 29 | 0 | 19 | 0.0094 | 0.0662 |
| 13 | 64 | 36 | 1 | 25 | 0.0297 | 0.2593 |
| 17 | 64 | 39 | 0 | 29 | 0.0145 | 0.0753 |
| 21 | 64 | 43 | 2 | 30 | 0.0187 | 0.2009 |
| 25 | 64 | 49 | 4 | 35 | 0.0394 | 0.2576 |
| 29 | 64 | 45 | 0 | 36 | 0.0276 | 0.2576 |
| 33 | 64 | 35 | 1 | 28 | 0.0203 | 0.0898 |
| 37 | 64 | 43 | 1 | 36 | 0.0533 | 0.2576 |
| 41 | 64 | 41 | 2 | 34 | 0.0354 | 0.2576 |
| 45 | 64 | 40 | 1 | 37 | 0.0303 | 0.2009 |

## Held-out evaluation hill (never used for training or selection), fresh samples

| model | samples | valid | copies | mean reward | best-of-n reward | share with reward > 0 |
|---|---|---|---|---|---|---|
| base | 65 | 40 | 1 | 0.0034 | 0.1771 | 0.03 |
| after GRPO | 65 | 49 | 2 | 0.0074 | 0.1771 | 0.06 |

Difference in mean reward: +0.0040 (95% CI -0.0056 to +0.0137, Welch normal approximation)

Mean reward by archetype asked:

| archetype | base | after GRPO |
|---|---|---|
| stone | 0.0136 | 0.0272 |
| paper | 0.0000 | 0.0000 |
| scanner | 0.0000 | 0.0000 |
| stone_imp | 0.0000 | 0.0099 |
| free | 0.0034 | 0.0000 |
