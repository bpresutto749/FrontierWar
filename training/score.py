#!/usr/bin/env python3
"""Score sampled warriors on the training hill (default) or the evaluation hill.
usage: score.py samples.jsonl scored.jsonl [--hill train|eval] [--rounds 50]"""
import argparse, statistics
from common import TRAIN_HILL, EVAL_HILL, read_jsonl, write_jsonl, score_many, reward

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--hill", choices=["train", "eval"], default="train")
ap.add_argument("--rounds", type=int, default=50)
ap.add_argument("--workers", type=int)
a = ap.parse_args()
rows = read_jsonl(a.inp)
hill = TRAIN_HILL if a.hill == "train" else EVAL_HILL
res = score_many([r["source"] for r in rows], hill, a.rounds, a.workers)
for r, s in zip(rows, res):
    r.update({f"{a.hill}_{k}": v for k, v in s.items()})
    if a.hill == "eval":
        r["eval_reward"] = reward(s["score"]) if s["valid"] and not s["copy"] else 0.0
write_jsonl(a.out, rows)
sc = [r[f"{a.hill}_score"] for r in rows]
print(f"n={len(rows)} valid={sum(r[f'{a.hill}_valid'] for r in rows)} copies={sum(r[f'{a.hill}_copy'] for r in rows)} "
      f"mean={statistics.mean(sc):.4f} max={max(sc):.4f}")
