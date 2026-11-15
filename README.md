# FrontierWar: Core War Arena

<!-- À écrire : une phrase. Ex. : un environnement Harbor où les agents de code frontière
     restent sous le meilleur programme humain de Core War. -->

## Run it in one line

```bash
git clone https://github.com/bpresutto749/FrontierWar && cd FrontierWar && harbor run -p harbor/corewar-hill -a opencode -m anthropic/claude-opus-5-5
```

Needs Docker, [Harbor](https://pypi.org/project/harbor/) (`uv tool install harbor`) and an
API key in the shell (`export ANTHROPIC_API_KEY=...`, or `OPENAI_API_KEY` / `GEMINI_API_KEY`
with `-m openai/<model>` / `-m gemini/<model>`). The reward is in
`jobs/<job>/<trial>/verifier/reward.txt`.

Check the scale (two more lines):

```bash
harbor run -p harbor/corewar-hill -a oracle   # the #1 human program: 1.0
harbor run -p harbor/corewar-hill -a nop      # doing nothing: 0.0
```

<!-- Options utiles : -k 5 (5 essais) ; -p harbor/corewar-hill-public si Docker n'a pas le
     contrôle de sortie réseau ; détails dans RUN_HARBOR.md. -->

## The question

<!-- À écrire. La question, la réponse (« Not yet ») et le tableau :
     Can a frontier AI agent turn practice into a design that wins against opponents it has never seen?
     | | escape the traps of practice | find a winning design |
     | Claude Opus 5.5 (0.71) | ✗ | ✗ |
     | GPT-6.1 sol (0.84)     | ✓ | ✗ | -->

## The task

<!-- À écrire, 3 à 5 lignes : Core War, un programme, 45 minutes, 30 adversaires
     d'entraînement, 30 cachés (500 parties chacun), récompense 0 = Dwarf, 1 = Toxic. -->

## Results

<!-- À écrire : un tableau court.
     Claude Opus 5.5 : 0.713 (5 runs) · GPT-6.1 sol : 0.842 (5 runs) · Toxic : 1.000 · nop : 0.000
     0 of 32 frontier-agent runs reach 1. Sources : results/models.md. -->

## Why the agents fall short

<!-- À écrire : deux couches.
     1. Les pièges de l'entraînement (Opus) : s'arrête tôt, polit une idée, colle au practice.
     2. Le design (les deux) : >90 % de l'écart déjà là en practice (92 % / 98 %) ;
        GPT-6.1 sol gagne autant que Toxic, perd 3 à 5 fois plus. Détails : FAILURES.md. -->

## Can the score be trusted?

<!-- À écrire : copie et faux score = 0 ; 34 triches testées, au plus 0.24 ; score calculé
     dans une sandbox séparée. Détails : EXPLOITS.md. -->

## Videos

- [Pitch, 1 min 59](media/corewar_pitch_1min59.mp4)
- [Full demo, 8 min 10](media/corewar_demo_full.mp4)

## Bonus: training small models

<!-- À écrire : 19 runs s'améliorent (3B à 32B, deux méthodes). Détails : RL_SYNTHESIS.md. -->

## Repository

| path | what |
|---|---|
| `harbor/corewar-hill/` | the Harbor task (environment, MCP server, verifier) |
| `runs/harbor/` | the Harbor runs of both models |
| `results/` | the analyses behind every number |
| `REPORT.md` | the full report |
| `FAILURES.md`, `EXPLOITS.md`, `DECISIONS.md` | failure modes, exploit sweep, design decisions |
| `TRAINING.md`, `RL_SYNTHESIS.md`, `training/` | small-model training |
| `video/`, `media/` | the code that draws the videos, and the videos |

## Credits

<!-- À écrire : l'équipe. Tiers : CREDITS.md (pMARS, CodeClash, Digital Red Queen, auteurs
     des warriors). Licence : LICENSE (MIT). -->
