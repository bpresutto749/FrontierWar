#!/usr/bin/env python3
"""Summarise an expert-iteration run directory as markdown."""
import glob, math, statistics, sys
from pathlib import Path
from common import read_jsonl

d = Path(sys.argv[1])
print(f"# Expert iteration report: {d.name}\n")
print("| round | samples | valid | published copies | mean train score | best train score |")
print("|---|---|---|---|---|---|")
for p in sorted(d.glob("r*.train.jsonl"), key=lambda p: int(p.name[1:].split(".")[0])):
    rows = read_jsonl(p)
    sc = [r["train_score"] for r in rows]
    print(f"| {p.name.split('.')[0]} | {len(rows)} | {sum(r['train_valid'] for r in rows)} | {sum(r['train_copy'] for r in rows)} | "
          f"{statistics.mean(sc):.4f} | {max(sc):.4f} |")


def summ(name):
    p = d / f"{name}.eval.jsonl"
    if not p.exists():
        return None
    rw = [r["eval_reward"] for r in read_jsonl(p)]
    return rw


b, f = summ("base"), summ("final")
if b and f:
    mb, mf = statistics.mean(b), statistics.mean(f)
    se = math.sqrt(statistics.variance(b) / len(b) + statistics.variance(f) / len(f))
    print("\nHeld-out evaluation hill (never used for training or selection), fresh samples:\n")
    print("| model | samples | mean reward | best-of-n reward | share with reward > 0 |")
    print("|---|---|---|---|---|")
    for n, r in (("base", b), ("after expert iteration", f)):
        print(f"| {n} | {len(r)} | {statistics.mean(r):.4f} | {max(r):.4f} | {sum(x > 0 for x in r) / len(r):.2f} |")
    print(f"\nDifference in mean reward: {mf - mb:+.4f} (95% CI {mf - mb - 1.96 * se:+.4f} to {mf - mb + 1.96 * se:+.4f}, Welch normal approximation)")
