#!/usr/bin/env python3
"""Expert iteration, selection step: from every round so far, keep the best valid, original,
de-duplicated samples OF EACH ARCHETYPE (top fraction per archetype, scored on the training pool
only). Keeping each style, rather than the overall top, stops the run from collapsing onto the
cheapest strategy the reward allows (the imp, in the first run: TRAINING.md).
Writes mlx_lm chat data: the loss is on the warrior only (--mask-prompt).
usage: pick.py r0.train.jsonl [r1.train.jsonl ...] --top 0.25 --out DIR/train.jsonl"""
import argparse, json, math, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import core  # noqa: E402
from prompts import messages  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp", nargs="+")
    ap.add_argument("--top", type=float, default=0.25)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = [json.loads(l) for p in a.inp for l in open(p)]
    rows = [r for r in rows if r["train_valid"] and not r["train_copy"] and r["train_score"] > 0]
    seen, by_arch = set(), defaultdict(list)
    for r in sorted(rows, key=lambda r: -r["train_score"]):
        key = tuple(core.assemble(r["source"])[0])
        if key not in seen:
            seen.add(key); by_arch[r["arch"]].append(r)
    keep = []
    for arch, rs in sorted(by_arch.items()):
        k = max(1, math.ceil(len(rs) * a.top))
        keep += rs[:k]
        print(f"  {arch:10s} {len(rs):4d} unique originals, kept {k}, scores {rs[0]['train_score']:.3f} .. {rs[k - 1]['train_score']:.3f}")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as f:
        for r in keep:
            f.write(json.dumps({"messages": messages(r["arch"], r["source"])}) + "\n")
    print(f"kept {len(keep)} of {len(rows)} valid originals -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
