# Two-turn evaluation: qwen7b-agent

Hidden hill, environment's reward, 100 rounds; each model writes a draft, gets the spar report on it, then writes its final warrior.

| model | samples | mean reward, draft | mean reward, final | final > 0 | best final |
|---|---|---|---|---|---|
| base | 64 | 0.0035 | 0.0007 | 0.02 | 0.0438 |
| after two-turn GRPO | 64 | 0.0056 | 0.0051 | 0.06 | 0.1833 |

Gain of the trained model on the final warrior: +0.0045 (95% CI -0.0021 to +0.0111, Welch).
Second turn minus draft, base model: -0.0028 (95% CI -0.0085 to +0.0030; paired samples, Welch used as an approximation).
Second turn minus draft, trained model: -0.0004 (95% CI -0.0095 to +0.0086; paired samples, Welch used as an approximation).
