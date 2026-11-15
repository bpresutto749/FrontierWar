#!/usr/bin/env python3
"""The battle tool's answer for each warrior, exactly as the agent gets it in the task: the
per-opponent table against the 30 sparring warriors (ids s01..s30, 100 rounds), or the
assembler's messages if the warrior does not assemble (arena/mcp_server.py, battle).
Adds fb_<tag> (that text) and spar_<tag> (its mean) to every row.
usage: feedback.py in.jsonl out.jsonl --tag draft|rev"""
import argparse, json, os, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import ROOT, core  # noqa: E402

SPARRING = [(f"s{i:02d}", p) for i, p in enumerate(sorted((ROOT / "data" / "sparring").glob("*.red")), 1)]
ROUNDS = 100


def battle(src):
    ins, msgs = core.assemble(src, ROUNDS)
    if not ins:
        return "does not assemble:\n" + msgs, 0.0
    res = core.play_hill(src, [p for _, p in SPARRING], ROUNDS, workers=1)
    for (i, _), r in zip(SPARRING, res):
        r.opponent = i
    return core.table(res), core.hill_score(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--tag", choices=["draft", "rev"], required=True)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.inp)]
    t0 = time.time()
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(battle, [r["source"] for r in rows], chunksize=2))
    for r, (fb, s) in zip(rows, res):
        r[f"fb_{a.tag}"], r[f"spar_{a.tag}"] = fb, s
    with open(a.out, "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    ok = [s for _, s in res]
    print(f"battle tool on {len(rows)} {a.tag}s: {sum(not fb.startswith('does not') for fb, _ in res)} assemble, "
          f"mean sparring score {sum(ok) / len(ok):.4f}  ({time.time() - t0:.0f} s)", flush=True)


if __name__ == "__main__":
    main()
