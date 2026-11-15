# GRPO report (step150, adapter /out/qwen7b-grpo/checkpoint-150): qwen7b-grpo

Configuration: `{"model": "Qwen/Qwen2.5-Coder-7B-Instruct", "out": "/out/qwen7b-grpo", "max_steps": 200, "prompts_per_step": 8, "num_generations": 8, "micro_batch": 8, "lr": 1e-05, "lora_r": 16, "max_completion": 768, "prompt_style": "mlx_dwarf", "temperature": 0.8, "top_p": 0.95, "top_k": 512, "save_steps": 25, "vllm_memory": 0.3, "workers": 16, "seed": 0, "samples_per_step": 64, "reward": {"rounds": 50, "tie_weight": 0.0}, "versions": {"trl": "1.17.1", "transformers": "5.17.0", "torch": "2.13.0+cu130"}}`

## Training (training pool only; reward = share of rounds won, 0 for copies)

| step | samples | valid | copies | won a round | mean training reward | best |
|---|---|---|---|---|---|---|
| 1 | 64 | 29 | 0 | 15 | 0.0105 | 0.2576 |
| 16 | 64 | 45 | 0 | 28 | 0.0285 | 0.2380 |
| 31 | 64 | 46 | 1 | 38 | 0.0562 | 0.2593 |
| 46 | 64 | 58 | 3 | 54 | 0.0602 | 0.2593 |
| 61 | 64 | 46 | 0 | 43 | 0.0374 | 0.2576 |
| 76 | 64 | 48 | 1 | 46 | 0.0500 | 0.2576 |
| 91 | 64 | 56 | 2 | 52 | 0.0690 | 0.2576 |
| 106 | 64 | 57 | 0 | 53 | 0.0765 | 0.2593 |
| 121 | 64 | 55 | 1 | 51 | 0.0842 | 0.2593 |
| 136 | 64 | 58 | 1 | 55 | 0.1133 | 0.2576 |
| 151 | 64 | 56 | 1 | 55 | 0.1280 | 0.2576 |

## Held-out evaluation hill (never used for training or selection), fresh samples

| model | samples | valid | copies | mean reward | best-of-n reward | share with reward > 0 | mean raw hill score |
|---|---|---|---|---|---|---|---|
| base | 65 | 39 | 1 | 0.0034 | 0.1771 | 0.03 | 0.0141 |
| after GRPO | 65 | 60 | 1 | 0.0431 | 0.1771 | 0.38 | 0.1103 |

The reward is 0 for any warrior at or below Dwarf (hill score 0.1475); the raw hill score (points / maximum, copies and invalid samples at 0) also shows progress below that line.

Difference in mean reward: +0.0397 (95% CI +0.0225 to +0.0568, Welch normal approximation)

Mean reward by archetype asked:

| archetype | base | after GRPO |
|---|---|---|
| stone | 0.0136 | 0.1157 |
| paper | 0.0000 | 0.0062 |
| scanner | 0.0000 | 0.0227 |
| stone_imp | 0.0000 | 0.0347 |
| free | 0.0034 | 0.0361 |
