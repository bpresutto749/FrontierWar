#!/usr/bin/env python3
"""Held-out evaluation of a two-turn run (agent.py --mode two_turn): for the base model and for the
trained adapter, the model writes a draft, `spar` reports on it (30 sparring warriors, as in
training), and the model writes its final warrior. Drafts and finals are both scored once on the
hidden hill with the environment's reward (100 rounds per opponent, the copy gate), so the report
shows the trained model's gain and how much the second turn adds.

usage: evaluate_agent.py --run runs/qwen7b-agent [--adapter DIR] [--n 64]
writes RUN/agent.base.eval.jsonl, RUN/agent.final.eval.jsonl, RUN/AGENT_REPORT.md
"""
import argparse
import json
import math
import os
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from reward import Scorer  # noqa: E402  (before vLLM: the scoring processes fork first)
from common import EVAL_HILL, reward, score_many, write_jsonl  # noqa: E402
from agent import FEEDBACK, spar_report  # noqa: E402
from train import ARCHETYPES, PREFILL, prompt_text, source_of  # noqa: E402


def two_turn(llm, tok, cfg, n, lora, seed, pool):
    from vllm import SamplingParams
    names = [a for a, _ in ARCHETYPES]
    per = math.ceil(n / len(names))
    prompts = {a: prompt_text(tok, cfg.get("prompt_style", "mlx_dwarf"), a) for a in names}
    kw = dict(temperature=cfg.get("temperature", 0.8), top_p=cfg.get("top_p", 0.95), top_k=cfg.get("top_k", -1) or -1,
              max_tokens=cfg.get("turn_tokens", 768))
    outs = llm.generate([prompts[a] for a in names], SamplingParams(n=per, seed=seed, **kw), lora_request=lora)
    drafts = [(a, o.text) for a, g in zip(names, outs) for o in g.outputs][:n]
    reports = list(pool.map(spar_report, [source_of(t) for _, t in drafts], chunksize=1))
    second = [prompts[a] + t + ("" if t.rstrip().endswith("```") else "\n```") + "<|im_end|>\n<|im_start|>user\n"
              + FEEDBACK.format(report=r) + "<|im_end|>\n<|im_start|>assistant\n" + PREFILL
              for (a, t), r in zip(drafts, reports)]
    finals = llm.generate(second, SamplingParams(n=1, seed=seed + 1, **kw), lora_request=lora)
    return [{"arch": a, "draft": source_of(t), "report": r, "source": source_of(f.outputs[0].text)}
            for (a, t), r, f in zip(drafts, reports, finals)]


def score(rows, key, workers):
    res = score_many([r[key] for r in rows], EVAL_HILL, rounds=100, workers=workers)
    return [reward(s["score"]) if s["valid"] and not s["copy"] else 0.0 for s in res]


def ci(a, b):
    se = math.sqrt(statistics.variance(a) / len(a) + statistics.variance(b) / len(b))
    d = statistics.mean(b) - statistics.mean(a)
    return d, d - 1.96 * se, d + 1.96 * se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--adapter")
    ap.add_argument("--n", type=int, default=64)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    a = ap.parse_args()
    run = Path(a.run)
    cfg = json.loads((run / "config.json").read_text())
    scorer = Scorer(a.workers)
    scorer.warm()
    from vllm import LLM
    from vllm.lora.request import LoRARequest
    llm = LLM(model=cfg["model"], enable_lora=True, max_lora_rank=64, max_model_len=6144, seed=a.seed)
    tok = llm.get_tokenizer()
    rows = {}
    for tag, lora in (("base", None), ("final", LoRARequest("adapter", 1, a.adapter or str(run / "final")))):
        rs = two_turn(llm, tok, cfg, a.n, lora, a.seed, scorer.pool)
        for r, d, f in zip(rs, score(rs, "draft", a.workers), score(rs, "source", a.workers)):
            r["draft_reward"], r["eval_reward"] = d, f
        rows[tag] = rs
        write_jsonl(run / f"agent.{tag}.eval.jsonl", rs)
    L = [f"# Two-turn evaluation: {run.name}", "", "Hidden hill, environment's reward, 100 rounds; each model writes a draft, "
         "gets the spar report on it, then writes its final warrior.", "",
         "| model | samples | mean reward, draft | mean reward, final | final > 0 | best final |", "|---|---|---|---|---|---|"]
    for tag, name in (("base", "base"), ("final", "after two-turn GRPO")):
        d = [r["draft_reward"] for r in rows[tag]]
        f = [r["eval_reward"] for r in rows[tag]]
        L.append(f"| {name} | {len(f)} | {statistics.mean(d):.4f} | {statistics.mean(f):.4f} | "
                 f"{sum(x > 0 for x in f) / len(f):.2f} | {max(f):.4f} |")
    d, lo, hi = ci([r["eval_reward"] for r in rows["base"]], [r["eval_reward"] for r in rows["final"]])
    L += ["", f"Gain of the trained model on the final warrior: {d:+.4f} (95% CI {lo:+.4f} to {hi:+.4f}, Welch)."]
    for tag, name in (("base", "base"), ("final", "trained")):
        d, lo, hi = ci([r["draft_reward"] for r in rows[tag]], [r["eval_reward"] for r in rows[tag]])
        L.append(f"Second turn minus draft, {name} model: {d:+.4f} (95% CI {lo:+.4f} to {hi:+.4f}; paired samples, "
                 "Welch used as an approximation).")
    text = "\n".join(L) + "\n"
    (run / "AGENT_REPORT.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
