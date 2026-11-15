# Expert iteration report: Qwen2.5-Coder-7B-Instruct

| round | samples | valid | published copies | mean train score | best train score |
|---|---|---|---|---|---|
| r0 | 256 | 81 | 0 | 0.0068 | 0.2156 |
| r1 | 256 | 139 | 4 | 0.0623 | 0.2223 |
| r2 | 256 | 207 | 0 | 0.1614 | 0.2196 |
| r3 | 256 | 218 | 1 | 0.1745 | 0.2191 |

Held-out evaluation hill (never used for training or selection), fresh samples:

| model | samples | mean reward | best-of-n reward | share with reward > 0 |
|---|---|---|---|---|
| base | 64 | 0.0000 | 0.0000 | 0.00 |
| after expert iteration | 64 | 0.0320 | 0.0601 | 0.77 |

Difference in mean reward: +0.0320 (95% CI +0.0273 to +0.0366, Welch normal approximation)
