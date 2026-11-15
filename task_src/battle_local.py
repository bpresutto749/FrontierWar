#!/usr/bin/env python3
"""Battle a warrior locally against warriors you wrote yourself.

usage: python3 tools/battle.py my.red --vs other1.red other2.red ... [--rounds 100]

(The sparring warriors live on the corewar MCP server: use its `battle` tool or
tools/spar.py.)

Scoring per opponent follows King-of-the-Hill rules: 3 points per round won,
1 per tie, 0 per loss, normalised by 3*rounds (so 1.0 = won every round).
Core settings are the standard '94 hill: coresize 8000, 80000 cycles,
8000 processes, max length 100, min distance 100.
"""
import argparse, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
PMARS = HERE / "bin" / "pmars"


def sanitize(text):
    """pMARS hangs on very long source lines: comment lines are cut to 200
    characters, inline comments are dropped from over-long code lines, and a code
    line still longer than 200 characters makes the file invalid."""
    out = []
    for line in text.replace('\r', '').split('\n'):
        if len(line) > 200:
            if line.lstrip().startswith(';'):
                line = line[:200]
            else:
                line = line.split(';', 1)[0].rstrip()
                if len(line) > 200:
                    return None
        out.append(line)
    return '\n'.join(out) + '\n'


def battle(a, b, rounds):
    p = subprocess.run([str(PMARS), "-b", "-k", "-r", str(rounds), "-f", str(a), str(b)],
                       capture_output=True, text=True, timeout=300)
    lines = [l for l in p.stdout.strip().splitlines() if l.split() and l.split()[0].lstrip('-').isdigit()]
    if len(lines) < 2:
        return None, (p.stdout + p.stderr).strip()[-400:]
    w1, t1 = map(int, lines[-2].split()[:2])
    w2, _ = map(int, lines[-1].split()[:2])
    return (w1, w2, t1), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("warrior")
    ap.add_argument("--rounds", type=int, default=100)
    ap.add_argument("--vs", nargs="+", required=True)
    a = ap.parse_args()
    clean = sanitize(Path(a.warrior).read_text(errors="replace"))
    if clean is None:
        sys.exit("invalid: a code line is longer than 200 characters")
    import tempfile
    tf = tempfile.NamedTemporaryFile("w", suffix=".red", delete=False)
    tf.write(clean); tf.close()
    a.warrior = tf.name
    opps = [Path(x) for x in a.vs]
    with ThreadPoolExecutor(os.cpu_count() or 2) as ex:
        res = list(ex.map(lambda o: battle(a.warrior, o, a.rounds), opps))
    tot = 0.0
    print(f"{'opponent':28s} {'win':>4s} {'loss':>4s} {'tie':>4s}  score")
    for o, (r, err) in zip(opps, res):
        if r is None:
            print(f"{o.stem:28s} ERROR: {err}")
            continue
        s = (3 * r[0] + r[2]) / (3 * a.rounds)
        tot += s
        print(f"{o.stem:28s} {r[0]:4d} {r[1]:4d} {r[2]:4d}  {s:.3f}")
    print(f"{'MEAN':28s} {'':14s}  {tot / len(opps):.3f}")


if __name__ == "__main__":
    sys.exit(main())
