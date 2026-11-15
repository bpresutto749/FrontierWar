#!/usr/bin/env python3
"""Sample warriors from a (base or LoRA-tuned) model with vLLM.
usage: generate.py --model Qwen/Qwen2.5-Coder-7B-Instruct [--lora DIR] --n 256 --out samples.jsonl"""
import argparse
from common import build_prompt, extract, write_jsonl

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--lora")
ap.add_argument("--n", type=int, default=256)
ap.add_argument("--temperature", type=float, default=0.9)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--out", required=True)
a = ap.parse_args()

from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

llm = LLM(model=a.model, enable_lora=bool(a.lora), max_lora_rank=64, max_model_len=16384, seed=a.seed)
tok = llm.get_tokenizer()
prompt = tok.apply_chat_template([{"role": "user", "content": build_prompt()}], tokenize=False, add_generation_prompt=True)
sp = SamplingParams(n=a.n, temperature=a.temperature, top_p=0.95, max_tokens=3000, seed=a.seed)
lora = LoRARequest("adapter", 1, a.lora) if a.lora else None
out = llm.generate([prompt], sp, lora_request=lora)[0]
write_jsonl(a.out, [{"i": i, "text": o.text, "source": extract(o.text)} for i, o in enumerate(out.outputs)])
print("wrote", a.n, "samples to", a.out)
