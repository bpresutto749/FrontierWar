#!/usr/bin/env python3
"""Run 2 selection: two kinds of training examples, from every round so far, scored on the
training pool only (never the hidden hill).
- drafts: the best valid, original, de-duplicated drafts of each archetype (as in run 1);
- revisions: episodes in which the revision, written after reading the battle tool's output on the
  draft, scores higher than the draft; the best of them per archetype. The example is the whole
  episode (task, draft, battle output) and the loss falls on the revision only (--mask-prompt).
usage: pick_fb.py --rounds r0 [r1 ...] --dir RUN --top 0.25 --top-rev 0.5 --out DIR/train.jsonl"""
import argparse, json, math, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import core  # noqa: E402
from prompts import messages, revision_messages  # noqa: E402

MAX_CHARS = 8400           # about 3,000 tokens: longer episodes would be cut by --max-seq-length


def ok(r):
    return r["train_valid"] and not r["train_copy"] and r["train_score"] > 0


def best_per_arch(rows, frac, key, label):
    seen, by = set(), defaultdict(list)
    for r in sorted(rows, key=lambda r: -key(r)):
        k = tuple(core.assemble(r["source"])[0])
        if k not in seen:
            seen.add(k); by[r["arch"]].append(r)
    keep = []
    for arch, rs in sorted(by.items()):
        n = max(1, math.ceil(len(rs) * frac))
        keep += rs[:n]
        print(f"  {label:9s} {arch:10s} {len(rs):4d} candidates, kept {n}, scores {key(rs[0]):.3f} .. {key(rs[n - 1]):.3f}")
    return keep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", nargs="+", required=True)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--top", type=float, default=0.25)
    ap.add_argument("--top-rev", type=float, default=0.5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = Path(a.dir)
    drafts, revs = [], []
    for r in a.rounds:
        dr = {x["i"]: x for x in map(json.loads, open(d / f"{r}.drafts.train.jsonl"))}
        drafts += [x for x in dr.values() if ok(x)]
        for x in map(json.loads, open(d / f"{r}.revs.train.jsonl")):
            base = dr[x["i"]]["train_score"] if ok(dr[x["i"]]) else 0.0
            if ok(x) and x["train_score"] > base:
                x["gain"] = x["train_score"] - base
                revs.append(x)
    keep_d = best_per_arch(drafts, a.top, lambda r: r["train_score"], "drafts")
    keep_r = best_per_arch(revs, a.top_rev, lambda r: r["train_score"], "revisions") if revs else []
    out = [{"messages": messages(r["arch"], r["source"])} for r in keep_d]
    long_ = 0
    for r in keep_r:
        m = revision_messages(r["arch"], r["draft"], r["fb_draft"], r["source"])
        if sum(len(x["content"]) for x in m) > MAX_CHARS:
            long_ += 1; continue
        out.append({"messages": m})
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as f:
        f.writelines(json.dumps(x) + "\n" for x in out)
    print(f"kept {len(keep_d)} drafts and {len(keep_r) - long_} revisions ({long_} too long) "
          f"of {len(revs)} improving revisions -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
