# GRPO report (step100, adapter /out/qwen7b-grpo/checkpoint-100): qwen7b-grpo

Configuration: `{"model": "Qwen/Qwen2.5-Coder-7B-Instruct", "out": "/out/qwen7b-grpo", "max_steps": 200, "prompts_per_step": 8, "num_generations": 8, "micro_batch": 8, "lr": 1e-05, "lora_r": 16, "max_completion": 768, "prompt_style": "mlx_dwarf", "temperature": 0.8, "top_p": 0.95, "top_k": 512, "save_steps": 25, "vllm_memory": 0.3, "workers": 16, "seed": 0, "samples_per_step": 64, "reward": {"rounds": 50, "tie_weight": 0.0}, "versions": {"trl": "1.17.1", "transformers": "5.17.0", "torch": "2.13.0+cu130"}}`

## Training (training pool only; reward = share of rounds won, 0 for copies)

| step | samples | valid | copies | won a round | mean training reward | best |
|---|---|---|---|---|---|---|
| 1 | 64 | 29 | 0 | 15 | 0.0105 | 0.2576 |
| 11 | 64 | 32 | 1 | 21 | 0.0152 | 0.1469 |
| 21 | 64 | 43 | 2 | 30 | 0.0187 | 0.2009 |
| 31 | 64 | 46 | 1 | 38 | 0.0562 | 0.2593 |
| 41 | 64 | 41 | 2 | 34 | 0.0354 | 0.2576 |
| 51 | 64 | 46 | 2 | 37 | 0.0400 | 0.2576 |
| 61 | 64 | 46 | 0 | 43 | 0.0374 | 0.2576 |
| 71 | 64 | 45 | 3 | 41 | 0.0447 | 0.2593 |
| 81 | 64 | 59 | 1 | 56 | 0.0815 | 0.2593 |
| 91 | 64 | 56 | 2 | 52 | 0.0690 | 0.2576 |
| 100 | 64 | 47 | 1 | 46 | 0.0528 | 0.2493 |

## Held-out evaluation hill (never used for training or selection), fresh samples

| model | samples | valid | copies | mean reward | best-of-n reward | share with reward > 0 | mean raw hill score |
|---|---|---|---|---|---|---|---|
| base | 65 | 43 | 1 | 0.0034 | 0.1771 | 0.03 | 0.0127 |
| after GRPO | 65 | 57 | 1 | 0.0257 | 0.1771 | 0.25 | 0.0781 |

The reward is 0 for any warrior at or below Dwarf (hill score 0.1475); the raw hill score (points / maximum, copies and invalid samples at 0) also shows progress below that line.

Difference in mean reward: +0.0223 (95% CI +0.0077 to +0.0369, Welch normal approximation)

Mean reward by archetype asked:

| archetype | base | after GRPO |
|---|---|---|
| stone | 0.0136 | 0.0844 |
| paper | 0.0000 | 0.0050 |
| scanner | 0.0000 | 0.0017 |
| stone_imp | 0.0000 | 0.0252 |
| free | 0.0034 | 0.0121 |
