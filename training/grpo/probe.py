#!/usr/bin/env python3
"""Before a GRPO run: how often does the base model write a warrior that assembles and wins a
round, for each prompt and sampling setting? GRPO learns only from groups whose rewards
differ, so the share of samples that win at least one round is what matters.

Prompts (all end inside the reply's code block, "```redcode\n"):
  mlx      training/mlx/prompts.py (compact reference + archetypes, no warrior code)
  mlx_dwarf  the same plus the documentation's Dwarf as a syntax example. Dwarf is a published
           warrior: a copy scores 0, but retuned variants pass the gate.
  route1   training/common.py build_prompt() (task + the full Redcode reference), route 1's prompt

usage: probe.py --n 64      (one line of JSON per configuration)
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from reward import Scorer, summary  # noqa: E402  (before vLLM: see Scorer)

from train import ARCHETYPES, prompt_text, source_of  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-Coder-7B-Instruct")
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--styles", default="mlx,mlx_dwarf,route1")
    ap.add_argument("--sampling", default="1.0:1.0,0.8:0.95", help="temperature:top_p pairs")
    a = ap.parse_args()
    scorer = Scorer(a.workers)
    scorer.warm()
    from vllm import LLM, SamplingParams

    llm = LLM(model=a.model, max_model_len=12288, seed=0, enable_prefix_caching=True)
    tok = llm.get_tokenizer()
    names = [n for n, _ in ARCHETYPES]
    per = max(1, a.n // len(names))
    for style in a.styles.split(","):
        prompts = [prompt_text(tok, style, n) for n in names]
        for pair in a.sampling.split(","):
            t, p = (float(x) for x in pair.split(":"))
            gens = llm.generate(prompts, SamplingParams(n=per, temperature=t, top_p=p, max_tokens=768, seed=1))
            srcs = [source_of(o.text) for g in gens for o in g.outputs]
            res = scorer(srcs)
            print(json.dumps({"model": a.model, "style": style, "temperature": t, "top_p": p, "prompt_tokens": len(tok(prompts[0])["input_ids"]),
                              **summary(res)}), flush=True)


if __name__ == "__main__":
    main()
