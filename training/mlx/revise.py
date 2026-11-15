#!/usr/bin/env python3
"""Second turn of an episode: the model sees its draft and the battle tool's output on it, and
writes a revision. Rows keep the draft (draft, draft_finish) and get the revision as source/text.
usage: revise.py --model M [--adapter DIR] --inp rR.fb.jsonl --seed S --out rR.revs.jsonl"""
import argparse, json, sys, time
from pathlib import Path

import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import BatchGenerator
from mlx_lm.sample_utils import make_sampler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen import stop_sequences
from prompts import PREFILL, revision_messages, source_of


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--adapter")
    ap.add_argument("--inp", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--temp", type=float, default=0.9)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--max-tokens", type=int, default=900)
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    mx.random.seed(a.seed + 7919)
    model, tok = load(a.model, adapter_path=a.adapter)
    rows = [json.loads(l) for l in open(a.inp)]
    prompts = [tok.encode(tok.apply_chat_template(revision_messages(r["arch"], r["source"], r["fb_draft"]),
                                                  add_generation_prompt=True, tokenize=False) + PREFILL,
                          add_special_tokens=False) for r in rows]
    t0 = time.time()
    gen = BatchGenerator(model, stop_tokens=stop_sequences(tok), sampler=make_sampler(temp=a.temp, top_p=a.top_p),
                         completion_batch_size=a.batch, prefill_batch_size=min(8, a.batch))
    uids = gen.insert(prompts, [a.max_tokens] * len(prompts))
    toks = {u: [] for u in uids}
    finish, done, ntok = {}, 0, 0
    while responses := gen.next_generated():
        for r in responses:
            if r.finish_reason != "stop":
                toks[r.uid].append(r.token); ntok += 1
            if r.finish_reason is not None:
                finish[r.uid] = r.finish_reason; done += 1
                if done % 32 == 0 or done == len(uids):
                    print(f"  {done}/{len(uids)} revisions, {ntok} tokens, {ntok / (time.time() - t0):.0f} tok/s", flush=True)
    gen.close()

    with open(a.out, "w") as f:
        for u, r in zip(uids, rows):
            text = tok.decode(toks[u])
            r = dict(r, draft=r["source"], draft_finish=r["finish"], text=text, finish=finish.get(u),
                     source=source_of(text))
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(rows)} revisions to {a.out} in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
