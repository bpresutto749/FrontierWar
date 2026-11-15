#!/usr/bin/env python3
"""Sample warriors with MLX (Apple Silicon), base model or base + LoRA adapter, batched.
usage: gen.py --model M [--adapter DIR] --n 256 --seed 0 --out samples.jsonl"""
import argparse, json, sys, time
from pathlib import Path

import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import BatchGenerator
from mlx_lm.sample_utils import make_sampler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prompts import PREFILL, assign, messages, source_of


def stop_sequences(tok):
    stops = {(t,) for t in tok.eos_token_ids}
    for name in ("<|im_end|>", "<|endoftext|>"):
        t = tok.convert_tokens_to_ids(name)
        if isinstance(t, int) and t >= 0:
            stops.add((t,))
    for s in ("```", "\n```", "```\n", " ```", "\n```\n"):
        ids = tok.encode(s, add_special_tokens=False)
        if ids:
            stops.add(tuple(ids))
    return [list(s) for s in stops]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--adapter")
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--temp", type=float, default=0.9)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--max-tokens", type=int, default=900)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    mx.random.seed(a.seed)
    model, tok = load(a.model, adapter_path=a.adapter)
    archs = assign(a.n)
    prompts = []
    for arch in archs:
        text = tok.apply_chat_template(messages(arch), add_generation_prompt=True, tokenize=False) + PREFILL
        prompts.append(tok.encode(text, add_special_tokens=False))

    t0 = time.time()
    gen = BatchGenerator(model, stop_tokens=stop_sequences(tok), sampler=make_sampler(temp=a.temp, top_p=a.top_p),
                         completion_batch_size=a.batch, prefill_batch_size=min(16, a.batch))
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
                    print(f"  {done}/{len(uids)} samples, {ntok} tokens, {ntok / (time.time() - t0):.0f} tok/s", flush=True)
    gen.close()

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as f:
        for i, (u, arch) in enumerate(zip(uids, archs)):
            text = tok.decode(toks[u])
            f.write(json.dumps({"i": i, "arch": arch, "finish": finish.get(u), "text": text,
                                "source": source_of(text)}) + "\n")
    print(f"wrote {len(uids)} samples to {a.out} in {time.time() - t0:.0f} s "
          f"({sum(f == 'length' for f in finish.values())} hit max tokens)", flush=True)


if __name__ == "__main__":
    main()
