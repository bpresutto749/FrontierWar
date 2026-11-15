#!/usr/bin/env python3
"""Score sampled warriors on the training pool (default) or, once at the end, on the hidden hill.
Same gate as the verifier: a near-copy of a published, hill or sparring warrior scores 0.
usage: score.py samples.jsonl scored.jsonl [--hill train|eval] [--rounds 50]"""
import argparse, json, os, statistics, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import CORPUS, EVAL_HILL, GATE_DIRS, TRAIN_HILL, core, reward, short_copy  # noqa: E402


def score_one(args):
    src, hill, rounds = args
    ins, _ = core.assemble(src)
    out = {"valid": bool(ins), "copy": False, "score": 0.0, "wins": 0, "ties": 0, "losses": 0, "len": len(ins)}
    if not ins:
        return out
    if (core.nearest_published(ins, GATE_DIRS)["copy"] or core.nearest_published(ins, CORPUS)["copy"]
            or short_copy(ins)):                # short published warrior + dead code (common.py)
        out["copy"] = True                      # never rewarded, as in the verifier
        return out
    res = core.play_hill(src, [Path(h) for h in hill], rounds, workers=1)
    out.update(score=core.hill_score(res), wins=sum(r.wins for r in res), ties=sum(r.ties for r in res),
               losses=sum(r.losses for r in res))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--hill", choices=["train", "eval"], default="train")
    ap.add_argument("--rounds", type=int, default=50)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.inp)]
    hill = [str(h) for h in (TRAIN_HILL if a.hill == "train" else EVAL_HILL)]
    t0 = time.time()
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(score_one, [(r["source"], hill, a.rounds) for r in rows], chunksize=2))
    p = a.hill
    for r, s in zip(rows, res):
        r.update({f"{p}_{k}": v for k, v in s.items()})
        if p == "eval":
            r["eval_reward"] = reward(s["score"]) if s["valid"] and not s["copy"] else 0.0
    with open(a.out, "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    sc = [r[f"{p}_score"] for r in rows]
    print(f"{p}: n={len(rows)} valid={sum(r[f'{p}_valid'] for r in rows)} copies={sum(r[f'{p}_copy'] for r in rows)} "
          f"mean={statistics.mean(sc):.4f} max={max(sc):.4f}  ({time.time() - t0:.0f} s)", flush=True)


if __name__ == "__main__":
    main()
