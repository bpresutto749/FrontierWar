# GRPO report (step150, adapter /out/qwen7b-grpo-nodwarfgate/final): qwen7b-grpo-nodwarfgate

Configuration: `{"model": "Qwen/Qwen2.5-Coder-7B-Instruct", "out": "/out/qwen7b-grpo-nodwarfgate", "max_steps": 150, "prompts_per_step": 8, "num_generations": 8, "micro_batch": 8, "lr": 1e-05, "lora_r": 16, "max_completion": 768, "prompt_style": "mlx_dwarf", "temperature": 0.8, "top_p": 0.95, "top_k": 512, "save_steps": 25, "vllm_memory": 0.3, "workers": 16, "seed": 0, "gate_example": true, "samples_per_step": 64, "reward": {"rounds": 50, "tie_weight": 0.0}, "versions": {"trl": "1.17.1", "transformers": "5.17.0", "torch": "2.13.0+cu130"}}`

## Training (training pool only; reward = share of rounds won, 0 for copies)

| step | samples | valid | copies | won a round | mean training reward | best |
|---|---|---|---|---|---|---|
| 1 | 64 | 43 | 5 | 22 | 0.0097 | 0.1789 |
| 16 | 64 | 37 | 7 | 17 | 0.0053 | 0.0533 |
| 31 | 64 | 52 | 13 | 25 | 0.0164 | 0.1740 |
| 46 | 64 | 38 | 0 | 33 | 0.0167 | 0.0582 |
| 61 | 64 | 48 | 3 | 40 | 0.0230 | 0.0700 |
| 76 | 64 | 50 | 2 | 45 | 0.0275 | 0.1327 |
| 91 | 64 | 47 | 1 | 43 | 0.0286 | 0.1773 |
| 106 | 64 | 53 | 4 | 46 | 0.0320 | 0.1804 |
| 121 | 64 | 49 | 0 | 49 | 0.0318 | 0.0876 |
| 136 | 64 | 45 | 4 | 38 | 0.0257 | 0.1860 |
| 150 | 64 | 51 | 7 | 41 | 0.0232 | 0.1758 |

## Held-out evaluation hill (never used for training or selection), fresh samples

| model | samples | valid | copies | mean reward | best-of-n reward | share with reward > 0 | mean raw hill score |
|---|---|---|---|---|---|---|---|
| base | 65 | 40 | 1 | 0.0034 | 0.1771 | 0.03 | 0.0135 |
| after GRPO | 65 | 59 | 0 | 0.0050 | 0.1771 | 0.06 | 0.0447 |

Where the reward comes from (structure of the warriors with reward > 0):

| model | Dwarf with other constants | contains the Dwarf loop | other |
|---|---|---|---|
| base | 1 warriors, 80% of the reward | 0, 0% | 1, 20% |
| after GRPO | 1 warriors, 54% of the reward | 0, 0% | 3, 46% |

The reward is 0 for any warrior at or below Dwarf (hill score 0.1475); the raw hill score (points / maximum, copies and invalid samples at 0) also shows progress below that line.

Difference in mean reward: +0.0016 (95% CI -0.0064 to +0.0097, Welch normal approximation)

Mean reward by archetype asked:

| archetype | base | after GRPO |
|---|---|---|
| stone | 0.0136 | 0.0136 |
| paper | 0.0000 | 0.0035 |
| scanner | 0.0000 | 0.0000 |
| stone_imp | 0.0000 | 0.0000 |
| free | 0.0034 | 0.0080 |
