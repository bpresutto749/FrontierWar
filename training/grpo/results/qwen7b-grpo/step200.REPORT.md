# GRPO report (step200, adapter /out/qwen7b-grpo/final): qwen7b-grpo

Configuration: `{"model": "Qwen/Qwen2.5-Coder-7B-Instruct", "out": "/out/qwen7b-grpo", "max_steps": 200, "prompts_per_step": 8, "num_generations": 8, "micro_batch": 8, "lr": 1e-05, "lora_r": 16, "max_completion": 768, "prompt_style": "mlx_dwarf", "temperature": 0.8, "top_p": 0.95, "top_k": 512, "save_steps": 25, "vllm_memory": 0.3, "workers": 16, "seed": 0, "samples_per_step": 64, "reward": {"rounds": 50, "tie_weight": 0.0}, "versions": {"trl": "1.17.1", "transformers": "5.17.0", "torch": "2.13.0+cu130"}}`

## Training (training pool only; reward = share of rounds won, 0 for copies)

| step | samples | valid | copies | won a round | mean training reward | best |
|---|---|---|---|---|---|---|
| 1 | 64 | 29 | 0 | 15 | 0.0105 | 0.2576 |
| 21 | 64 | 43 | 2 | 30 | 0.0187 | 0.2009 |
| 41 | 64 | 41 | 2 | 34 | 0.0354 | 0.2576 |
| 61 | 64 | 46 | 0 | 43 | 0.0374 | 0.2576 |
| 81 | 64 | 59 | 1 | 56 | 0.0815 | 0.2593 |
| 101 | 64 | 50 | 1 | 46 | 0.0447 | 0.2391 |
| 121 | 64 | 55 | 1 | 51 | 0.0842 | 0.2593 |
| 141 | 64 | 57 | 2 | 55 | 0.1144 | 0.2593 |
| 161 | 64 | 58 | 2 | 56 | 0.0995 | 0.2593 |
| 181 | 64 | 49 | 3 | 46 | 0.0935 | 0.2576 |
| 200 | 64 | 51 | 4 | 45 | 0.0739 | 0.2584 |

## Held-out evaluation hill (never used for training or selection), fresh samples

| model | samples | valid | copies | mean reward | best-of-n reward | share with reward > 0 | mean raw hill score |
|---|---|---|---|---|---|---|---|
| base | 65 | 39 | 1 | 0.0034 | 0.1771 | 0.03 | 0.0141 |
| after GRPO | 65 | 60 | 0 | 0.0525 | 0.1938 | 0.46 | 0.1204 |

Where the reward comes from (structure of the warriors with reward > 0):

| model | Dwarf with other constants | contains the Dwarf loop | other |
|---|---|---|---|
| base | 1 warriors, 80% of the reward | 0, 0% | 1, 20% |
| after GRPO | 18 warriors, 74% of the reward | 6, 17% | 6, 9% |

The reward is 0 for any warrior at or below Dwarf (hill score 0.1475); the raw hill score (points / maximum, copies and invalid samples at 0) also shows progress below that line.

Difference in mean reward: +0.0491 (95% CI +0.0304 to +0.0677, Welch normal approximation)

Mean reward by archetype asked:

| archetype | base | after GRPO |
|---|---|---|
| stone | 0.0136 | 0.1456 |
| paper | 0.0000 | 0.0191 |
| scanner | 0.0000 | 0.0318 |
| stone_imp | 0.0000 | 0.0391 |
| free | 0.0034 | 0.0267 |
