# Expérience de post-training — à lancer sur une machine GPU

Ce paquet entraîne un petit modèle open (Qwen2.5-Coder) à écrire des guerriers Core War
par *expert iteration*, puis compare une seule fois, sur la colline cachée, le modèle
avant et après entraînement. La colline cachée n'est jamais utilisée pendant
l'entraînement.

À chaque tour :
1. le modèle génère N guerriers ;
2. pMARS les note contre 30 + 60 adversaires d'entraînement ;
3. on garde le meilleur quart (originaux uniquement) ;
4. on fait un fine-tuning LoRA dessus.

## Prérequis

| | |
|---|---|
| matériel | Linux, 1 GPU NVIDIA ≥ 40 Go (A100/H100), ou ≥ 24 Go avec le modèle 1.5B ci-dessous |
| logiciel | CUDA, Python 3.10+, `gcc`, `make` |
| CPU | ≥ 8 cœurs conseillés : la notation des guerriers tourne sur CPU |
| réseau | accès à Hugging Face, pour télécharger le modèle |

## Lancer

```bash
unzip corewar-post-training.zip && cd corewar-post-training
python3 -m venv .venv && source .venv/bin/activate
pip install -r training/requirements-gpu.txt

bash training/smoke_test_cpu.sh            # 2–5 min, sans GPU : doit finir par "SMOKE TEST OK"

# expérience complète (≈ 2–4 h sur A100) : modèle, nombre de tours, échantillons par tour
bash training/run_expert_iteration.sh Qwen/Qwen2.5-Coder-7B-Instruct 3 256

# version rapide, ou si le GPU fait 24 Go
bash training/run_expert_iteration.sh Qwen/Qwen2.5-Coder-1.5B-Instruct 2 128
```

Le résultat s'affiche à la fin et se trouve dans
`training/runs/<modèle>/REPORT.md`. On y trouve :
- la récompense moyenne avant et après entraînement, avec l'IC 95 % de la différence ;
- le best-of-64 ;
- la part de guerriers valides.

## À renvoyer

```bash
cd training/runs && tar czf ../../resultats.tgz --exclude='adapter_*' . && cd ../..
```

`resultats.tgz` contient `REPORT.md`, les échantillons notés (`*.jsonl`) et les logs. Les
adaptateurs LoRA sont gros et ne servent pas à l'analyse : envoie-les seulement si on les
demande.

## Si ça casse

| symptôme | quoi faire |
|---|---|
| `pip` n'arrive pas à résoudre les versions | Installe les versions récentes des mêmes paquets (`pip install vllm transformers trl peft datasets`). Les scripts n'utilisent que des API stables. |
| Manque de mémoire GPU pendant le fine-tuning | Passe au modèle 1.5B, ou baisse `max_length` dans `training/sft_lora.py`. |
| Autre erreur | Envoie la sortie complète de la commande qui a échoué. |
