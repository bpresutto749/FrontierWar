#!/usr/bin/env python3
"""Score warriors exactly as the verifier does and summarise the gap.

usage: python3 eval.py [--json out.json] [--markdown out.md] GROUP=glob [GROUP=glob ...]
e.g.   python3 eval.py reference=data/reference_toxic.red "opus-5.5=runs/opus-5.5/*.red"

For every warrior: the originality gate (near-copy of a sparring or hill
warrior -> 0), the raw hill score (mean KotH points / 3) and the reward
(normalised between Dwarf = 0 and the reference = 1, clipped to [0, 1]). Per group: mean,
standard deviation and a 95% t-interval of the reward.
"""
import argparse
import glob
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from arena import core  # noqa: E402

HILL = sorted((ROOT / "data" / "hill").glob("*.red"))
GATE = [ROOT / "data" / "corpus", ROOT / "data" / "hill", ROOT / "data" / "sparring"]   # as the verifier
REFERENCE_TEXT = (ROOT / "data" / "reference_toxic.red").read_text(errors="replace").replace("\r", "")
DWARF, REF = 6637 / 45000, 21899 / 45000   # reward anchors: Dwarf = 0, reference = 1
T95 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26, 10: 2.23}


def score_file(path):
    src = Path(path).read_text(errors="replace")
    ins, _ = core.assemble(src)
    row = {"file": str(Path(path).relative_to(ROOT)) if Path(path).is_absolute() else str(path),
           "length": len(ins), "valid": bool(ins), "copy_of": None, "hill_score": 0.0, "reward": 0.0}
    if ins:
        gate = core.nearest_published(ins, GATE)
        exempt = src.replace("\r", "") == REFERENCE_TEXT      # the verifier's exact-text exemption
        if gate["copy"] and not exempt:
            row["copy_of"] = gate["warrior"]
        else:
            res = core.play_hill(src, HILL)
            s = core.hill_score(res)
            row["hill_score"] = round(s, 4)
            row["reward"] = round(min(1.0, max(0.0, (s - DWARF) / (REF - DWARF))), 4)
            # start-position luck: standard error of the hill score if the rounds of each
            # battle were independent random draws (per-round points 1, 1/3 or 0)
            var = 0.0
            for r in res:
                n = r.rounds
                m = r.points
                ex2 = (r.wins * 1.0 + r.ties * (1 / 9)) / n
                var += (ex2 - m * m) / n
            row["hill_se"] = round(math.sqrt(var) / len(res), 4)
            row["reward_se"] = round(row["hill_se"] / (REF - DWARF), 4)
    return row


def summary(rewards):
    n = len(rewards)
    m = statistics.mean(rewards)
    if n < 2:
        return {"n": n, "mean": round(m, 4), "sd": None, "ci95": None}
    sd = statistics.stdev(rewards)
    h = T95.get(n - 1, 1.96) * sd / math.sqrt(n)
    return {"n": n, "mean": round(m, 4), "sd": round(sd, 4), "ci95": [round(m - h, 4), round(m + h, 4)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("groups", nargs="+")
    ap.add_argument("--json")
    ap.add_argument("--markdown")
    a = ap.parse_args()
    out, md = {}, ["| group | warrior | length | hill score | reward | note |", "|---|---|---|---|---|---|"]
    for g in a.groups:
        name, pat = g.split("=", 1)
        files = sorted(glob.glob(str(ROOT / pat) if not Path(pat).is_absolute() else pat))
        rows = [score_file(f) for f in files]
        out[name] = {"rows": rows, "summary": summary([r["reward"] for r in rows]) if rows else None}
        for r in rows:
            note = "does not assemble" if not r["valid"] else (f"near-copy of {r['copy_of']}" if r["copy_of"] else "")
            se = f" ± {r['hill_se']:.3f}" if r.get("hill_se") is not None else ""
            rse = f" ± {r['reward_se']:.3f}" if r.get("reward_se") is not None else ""
            md.append(f"| {name} | {Path(r['file']).name} | {r['length']} | {r['hill_score']:.3f}{se} | {r['reward']:.3f}{rse} | {note} |")
            print(f"{name:18s} {Path(r['file']).name:28s} len {r['length']:3d}  hill {r['hill_score']:.3f}  reward {r['reward']:.3f}  {note}", flush=True)
        if rows:
            print(f"{name:18s} SUMMARY {out[name]['summary']}", flush=True)
    md.append("")
    md.append("| group | n | mean reward | sd | 95% CI |")
    md.append("|---|---|---|---|---|")
    for name, v in out.items():
        s = v["summary"]
        if s:
            md.append(f"| {name} | {s['n']} | {s['mean']:.3f} | {s['sd'] if s['sd'] is not None else '-'} | {s['ci95'] if s['ci95'] else '-'} |")
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1))
    if a.markdown:
        Path(a.markdown).write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
