#!/usr/bin/env python3
"""Keep the best valid, original, de-duplicated samples as SFT data (expert iteration).
usage: select_sft.py scored.jsonl [more.jsonl ...] --top 0.25 --out sft.jsonl"""
import argparse
from common import build_prompt, read_jsonl, write_jsonl, core

ap = argparse.ArgumentParser()
ap.add_argument("inp", nargs="+")
ap.add_argument("--top", type=float, default=0.25)
ap.add_argument("--min-score", type=float, default=0.0)
ap.add_argument("--out", required=True)
a = ap.parse_args()
rows = [r for p in a.inp for r in read_jsonl(p) if r["train_valid"] and not r["train_copy"]]
seen, uniq = set(), []
for r in sorted(rows, key=lambda r: -r["train_score"]):
    key = tuple(core.assemble(r["source"])[0])
    if key in seen:
        continue
    seen.add(key); uniq.append(r)
k = max(1, int(len(uniq) * a.top))
keep = [r for r in uniq[:k] if r["train_score"] >= a.min_score]
prompt = build_prompt()
# prompt-completion format: TRL trains on the completion (the warrior) only
write_jsonl(a.out, [{"prompt": [{"role": "user", "content": prompt}],
                     "completion": [{"role": "assistant", "content": "```redcode\n" + r["source"] + "```"}],
                     "train_score": r["train_score"]} for r in keep])
print(f"{len(rows)} valid originals, {len(uniq)} unique, kept {len(keep)} (min score {keep[-1]['train_score']:.3f})" if keep else "nothing kept")
