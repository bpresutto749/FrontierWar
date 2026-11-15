"""Training reward for GRPO: the share of rounds won on the training pool.

The training pool is the one every training route uses (common.TRAIN_HILL: the 30 sparring
warriors and the 60-warrior training hill). The hidden hill is never touched here.

Why rounds won, not points. The environment's reward counts a tie as 1 point and a win as
3, which is right for judging a warrior. As a training signal from scratch it has a cheap
local optimum: the one-line imp (`mov 0, 1`) kills nothing and ties most rounds. It scores
0.215 in points on the training pool, more than most base-model samples, and expert
iteration converged on it (TRAINING.md, route 1). Counted in wins, the imp is worth 0.022 and
the documentation's Dwarf 0.197. GRPO_TIE_WEIGHT gives ties a weight between 0 (default) and
1 (the environment's points) if a run wants it.

A sample earns 0 when it does not assemble or when the gate calls it a copy: the verifier's
gate (published, hill and sparring warriors) plus the short-warrior rule of common.py.

usage (check a file of samples):  python3 reward.py samples.jsonl [--workers 8]
"""
import importlib.util
import multiprocessing
import os
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

# training/common.py is loaded from its file. training/ itself must not be on sys.path: it holds
# a directory named "mlx", which would then be importable as `mlx`, and transformers would take
# it for Apple's MLX library (ModuleNotFoundError: mlx.core, during training).
if "common" not in sys.modules:
    _spec = importlib.util.spec_from_file_location("common", Path(__file__).resolve().parent.parent / "common.py")
    sys.modules["common"] = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(sys.modules["common"])
from common import CORPUS, GATE_DIRS, TRAIN_HILL, core, extract, short_copy  # noqa: E402

ROUNDS = int(os.environ.get("GRPO_ROUNDS", "50"))
TIE_WEIGHT = float(os.environ.get("GRPO_TIE_WEIGHT", "0"))
_HILL = [Path(h) for h in TRAIN_HILL]
_DWARF = None


def dwarf_shape(ins):
    """'dwarf' if the warrior is the documentation's Dwarf with other constants, 'dwarf_loop' if it
    contains the Dwarf's loop (structure only: opcodes, modifiers, modes), else None."""
    global _DWARF
    if _DWARF is None:
        src = (Path(core.__file__).resolve().parent.parent / "doc" / "example_dwarf.red").read_text()
        _DWARF = core._structure(core._strip(core.assemble(src)[0]))
    st = core._structure(core._strip(ins))
    if st == _DWARF:
        return "dwarf"
    n = len(_DWARF)
    return "dwarf_loop" if any(st[i:i + n] == _DWARF for i in range(len(st) - n + 1)) else None


def score(src, rounds=ROUNDS, tie_weight=TIE_WEIGHT):
    out = {"valid": False, "copy": None, "dwarf_shape": None, "wins": 0, "ties": 0, "losses": 0, "points": 0.0, "reward": 0.0}
    try:
        ins, _ = core.assemble(src)
    except Exception:       # e.g. non-ASCII code: pMARS rejects it and its message is not UTF-8
        return out
    if not ins:
        return out
    out["valid"] = True
    for dirs in (GATE_DIRS, CORPUS):
        g = core.nearest_published(ins, dirs)
        if g["copy"]:
            out["copy"] = g["warrior"]
            return out
    s = short_copy(ins)
    if s:
        out["copy"] = s
        return out
    # GRPO_GATE_EXAMPLE=1: a variant of the prompt's example (the Dwarf with other constants, or
    # anything built around its loop) earns 0 in training, so retuning the example does not pay.
    shape = dwarf_shape(ins)
    out["dwarf_shape"] = shape
    if shape and os.environ.get("GRPO_GATE_EXAMPLE") == "1":
        out["copy"] = f"example:{shape}"
        return out
    res = core.play_hill(src, _HILL, rounds, workers=1)
    w, t, l = (sum(getattr(r, k) for r in res) for k in ("wins", "ties", "losses"))
    n = max(1, w + t + l)
    out.update(wins=w, ties=t, losses=l, points=(3 * w + t) / (3 * n), reward=(3 * w + tie_weight * t) / (3 * n))
    return out


def _noop(_):
    return os.getpid()


class Scorer:
    """A pool of scoring processes. Create it, and call warm(), before importing torch: the
    workers are forked from a process with no CUDA context and no threads."""

    def __init__(self, workers=None):
        self.workers = workers or os.cpu_count()
        self.pool = ProcessPoolExecutor(self.workers, mp_context=multiprocessing.get_context("fork"))

    def warm(self):
        list(self.pool.map(_noop, range(self.workers)))     # with fork, all workers start on the first map
        list(self.pool.map(score, [";redcode-94\n;name warm\n        mov.i #0, 1\n"] * self.workers))  # caches the corpus

    def __call__(self, sources):
        return list(self.pool.map(score, sources, chunksize=1))


def summary(results):
    rw = [r["reward"] for r in results]
    return {
        "n": len(rw),
        "mean_reward": round(statistics.mean(rw), 4) if rw else 0.0,
        "max_reward": round(max(rw), 4) if rw else 0.0,
        "share_won_a_round": round(sum(r["wins"] > 0 for r in results) / max(1, len(rw)), 3),
        "valid": sum(r["valid"] for r in results),
        "copies": sum(bool(r["copy"]) for r in results),
        "mean_points": round(statistics.mean(r["points"] for r in results), 4) if rw else 0.0,
    }


if __name__ == "__main__":
    import argparse
    import json

    ap = argparse.ArgumentParser()
    ap.add_argument("samples")
    ap.add_argument("--workers", type=int)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.samples)]
    sc = Scorer(a.workers)
    res = sc([r.get("source") or extract(r.get("text", "")) for r in rows])
    print(json.dumps(summary(res)))
