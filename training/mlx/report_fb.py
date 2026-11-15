#!/usr/bin/env python3
"""Markdown report of a run-2 directory (episodes with the battle tool's feedback).
usage: report_fb.py RUN_DIR > RUN_DIR/REPORT.md"""
import json, math, statistics as st, sys
from pathlib import Path

d = Path(sys.argv[1])
rd = lambda p: [json.loads(l) for l in open(p)]
cfg = json.loads((d / "config.json").read_text()) if (d / "config.json").exists() else {}
print(f"# MLX expert iteration with the battle tool's feedback: {d.name}\n")
if cfg:
    print("Settings: " + ", ".join(f"{k} = {v}" for k, v in cfg.items()) + "\n")


def sc(r, p):
    return r[f"{p}_score"] if r[f"{p}_valid"] and not r[f"{p}_copy"] else 0.0


def ci(xs):
    m = st.mean(xs); h = 1.96 * math.sqrt(st.variance(xs) / len(xs)) if len(xs) > 1 else float("nan")
    return f"{m:+.4f} (95% CI {m - h:+.4f} to {m + h:+.4f})"


print("## Training pool (30 sparring + 60 training-hill warriors, 50 rounds each)\n")
print("| round | episodes | valid drafts | valid revisions | mean draft | mean revision | best revision | revision beats draft |")
print("|---|---|---|---|---|---|---|---|")
rounds = sorted({p.name.split(".")[0] for p in d.glob("r*.revs.train.jsonl")}, key=lambda s: int(s[1:]))
for r in rounds:
    dr = {x["i"]: x for x in rd(d / f"{r}.drafts.train.jsonl")}; rv = rd(d / f"{r}.revs.train.jsonl")
    a = [sc(dr[x["i"]], "train") for x in rv]; b = [sc(x, "train") for x in rv]
    print(f"| {r} | {len(rv)} | {sum(x['train_valid'] for x in dr.values())} | {sum(x['train_valid'] for x in rv)} | "
          f"{st.mean(a):.4f} | {st.mean(b):.4f} | {max(b):.4f} | {sum(y > x for x, y in zip(a, b)) / len(rv):.2f} |")

ev = {}
for name in ("base", "final"):
    p = d / f"{name}.episodes.jsonl"
    if p.exists():
        dr = {x["i"]: x for x in rd(d / f"{name}.drafts.eval.jsonl")}
        ev[name] = [(dr[x["i"]], x) for x in rd(p)]
if ev:
    print(f"\n## Hidden hill (never used for training or selection), {len(next(iter(ev.values())))} fresh episodes per model (same prompts and seed), 100 rounds\n")
    print("Submitted = the revision if its practice score (battle tool, sparring) is at least the draft's, else the "
          "draft: what an agent can choose with the information it has.\n")
    print("| model | valid drafts | valid revisions | mean reward, draft | mean reward, revision | mean reward, submitted | best submitted | revision beats draft |")
    print("|---|---|---|---|---|---|---|---|")
    sub = {}
    for name, eps in ev.items():
        a = [x["eval_reward"] for x, _ in eps]; b = [y["eval_reward"] for _, y in eps]
        s = [y["eval_reward"] if y["spar_rev"] >= y["spar_draft"] else x["eval_reward"] for x, y in eps]
        sub[name] = s
        print(f"| {'base' if name == 'base' else 'after training'} | {sum(x['eval_valid'] for x, _ in eps)} | "
              f"{sum(y['eval_valid'] for _, y in eps)} | {st.mean(a):.4f} | {st.mean(b):.4f} | {st.mean(s):.4f} | "
              f"{max(s):.4f} | {sum(v > u for u, v in zip(a, b)) / len(eps):.2f} |")
    for name, eps in ev.items():
        print(f"\nEffect of one round of feedback ({name}): revision minus draft, paired: "
              + ci([y["eval_reward"] - x["eval_reward"] for x, y in eps]))
    if len(sub) == 2:
        x, y = sub["base"], sub["final"]
        diff = st.mean(y) - st.mean(x); se = math.sqrt(st.variance(x) / len(x) + st.variance(y) / len(y))
        print(f"\nTraining effect on the submitted warrior: {diff:+.4f} (95% CI {diff - 1.96 * se:+.4f} to "
              f"{diff + 1.96 * se:+.4f}, Welch, normal approximation)")
        best = max(ev["final"], key=lambda e: max(e[0]["eval_reward"], e[1]["eval_reward"]))
        w = best[1] if best[1]["eval_reward"] >= best[0]["eval_reward"] else best[0]
        print(f"\nBest final warrior on the hidden hill: reward {w['eval_reward']:.3f} ({w['arch']} prompt):\n")
        print("```redcode\n" + w["source"].strip() + "\n```")
