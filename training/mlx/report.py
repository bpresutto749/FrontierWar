#!/usr/bin/env python3
"""Markdown report of an MLX expert-iteration run directory.
usage: report.py RUN_DIR [FINAL] > RUN_DIR/REPORT.md   (FINAL: name of the evaluated adapter's files, default "final")"""
import json, math, statistics, sys
from collections import defaultdict
from pathlib import Path

d = Path(sys.argv[1])
rd = lambda p: [json.loads(l) for l in open(p)]
cfg = json.loads((d / "config.json").read_text()) if (d / "config.json").exists() else {}
print(f"# MLX expert iteration: {d.name}\n")
if cfg:
    print("Settings: " + ", ".join(f"{k} = {v}" for k, v in cfg.items()) + "\n")

print("## Training pool (30 sparring + 60 training-hill warriors, 50 rounds each)\n")
print("| round | samples | valid | published copies | mean score | best score | mean score of valid originals |")
print("|---|---|---|---|---|---|---|")
rounds = sorted(d.glob("r*.train.jsonl"), key=lambda p: int(p.name[1:].split(".")[0]))
for p in rounds:
    rows = rd(p)
    sc = [r["train_score"] for r in rows]
    ok = [r["train_score"] for r in rows if r["train_valid"] and not r["train_copy"]]
    print(f"| {p.name.split('.')[0]} | {len(rows)} | {sum(r['train_valid'] for r in rows)} | {sum(r['train_copy'] for r in rows)} | "
          f"{statistics.mean(sc):.4f} | {max(sc):.4f} | {statistics.mean(ok) if ok else 0:.4f} |")

print("\nMean training score by archetype prompt:\n")
archs = sorted({r["arch"] for p in rounds for r in rd(p)})
print("| round | " + " | ".join(archs) + " |")
print("|---" * (len(archs) + 1) + "|")
for p in rounds:
    by = defaultdict(list)
    for r in rd(p):
        by[r["arch"]].append(r["train_score"])
    print(f"| {p.name.split('.')[0]} | " + " | ".join(f"{statistics.mean(by[a]):.3f}" for a in archs) + " |")


def ev(name):
    p = d / f"{name}.eval.jsonl"
    return rd(p) if p.exists() else None


FINAL = sys.argv[2] if len(sys.argv) > 2 else "final"
b, f = ev("base"), ev(FINAL)
if b and f:
    print("\n## Hidden hill (never used for training or selection), fresh samples, scored once, 100 rounds\n")
    print("| model | samples | valid | mean reward | best-of-n reward | share with reward > 0 | share that win any round |")
    print("|---|---|---|---|---|---|---|")
    for n, rows in (("base", b), ("after expert iteration" + ("" if FINAL == "final" else f" ({FINAL})"), f)):
        rw = [r["eval_reward"] for r in rows]
        print(f"| {n} | {len(rows)} | {sum(r['eval_valid'] for r in rows)} | {statistics.mean(rw):.4f} | {max(rw):.4f} | "
              f"{sum(x > 0 for x in rw) / len(rw):.2f} | {sum(r['eval_wins'] > 0 for r in rows) / len(rows):.2f} |")
    rb, rf = [r["eval_reward"] for r in b], [r["eval_reward"] for r in f]
    diff = statistics.mean(rf) - statistics.mean(rb)
    se = math.sqrt(statistics.variance(rb) / len(rb) + statistics.variance(rf) / len(rf))
    print(f"\nDifference in mean reward: {diff:+.4f} (95% CI {diff - 1.96 * se:+.4f} to {diff + 1.96 * se:+.4f}, Welch, normal approximation)")
    print("\nBy archetype prompt (mean reward, base -> final):\n")
    for a in archs:
        x = [r["eval_reward"] for r in b if r["arch"] == a]; y = [r["eval_reward"] for r in f if r["arch"] == a]
        if x and y:
            print(f"- {a}: {statistics.mean(x):.3f} -> {statistics.mean(y):.3f} (best {max(y):.3f}, n = {len(y)})")
    best = max(f, key=lambda r: r["eval_reward"])
    print(f"\nBest final sample on the hidden hill: reward {best['eval_reward']:.3f} ({best['arch']} prompt):\n")
    print("```redcode\n" + best["source"].strip() + "\n```")
