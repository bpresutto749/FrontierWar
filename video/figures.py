"""The two-model figures shown in the videos, read from results/models.json
(written by exploits/compare_models.py from the Harbor job directories). Nothing is typed in by hand."""
import json
from pathlib import Path

_M = json.loads((Path(__file__).resolve().parent.parent / "results" / "models.json").read_text())
REF = _M["reference"]
OPUS = [r for r in _M["runs"] if r["model"] == "Claude Opus 5.5"]
GPT = [r for r in _M["runs"] if r["model"] == "GPT-6.1 sol"]
GAPS = _M["gaps"]

mean = lambda xs: sum(xs) / len(xs)
OPUS_MEAN = mean([r["reward"] for r in OPUS])            # 0.713
GPT_MEAN = mean([r["reward"] for r in GPT])
N_GPT = len(GPT)
N_RUNS = 27 + sum(r["reward"] < 1 for r in GPT)          # the 27 earlier Opus runs (FAILURES.md), and these
GPT_QSCAN = sum(r["qscan"] for r in GPT)
OPUS_QSCAN = sum(r["qscan"] for r in OPUS)
GPT_DROP = (min(-r["drop"] for r in GPT), max(-r["drop"] for r in GPT))      # how much lower the real score is
OPUS_WORST_DROP = max(-r["drop"] for r in OPUS)
C5 = next(r for r in OPUS if r["label"] == "C5")
GPT_LAST_SUB = min(r["last_submission_minute"] for r in GPT)
OPUS_UNUSED = (45 - max(r["agent_minutes"] for r in OPUS), 45 - min(r["agent_minutes"] for r in OPUS))
GPT_TESTED = (min(r["programs_tested"] for r in GPT), max(r["programs_tested"] for r in GPT))
TOX_W, TOX_L, TOX_T = REF["wlt"]
GPT_W = (min(r["wlt"][0] for r in GPT), max(r["wlt"][0] for r in GPT))
GPT_L = (min(r["wlt"][1] for r in GPT), max(r["wlt"][1] for r in GPT))
GPT_T = (min(r["wlt"][2] for r in GPT), max(r["wlt"][2] for r in GPT))
LOSS_X = (GPT_L[0] / TOX_L, GPT_L[1] / TOX_L)            # losses, as a multiple of Toxic's
GPT_OVER100 = (min(r["over100"] for r in GPT), max(r["over100"] for r in GPT))
GPT_BETTER = (min(r["better_than_toxic"] for r in GPT), max(r["better_than_toxic"] for r in GPT))
WORST3 = GAPS[:3]                                        # largest mean loss gap to Toxic


def split(runs):
    """The hidden-test gap to Toxic = the gap already there in practice + the extra drop (results/models.md)."""
    pv, hv = mean([r["practice"] for r in runs]), mean([r["hill"] for r in runs])
    gp, gx = REF["practice"] - pv, (pv - hv) - (REF["practice"] - REF["hill"])
    return gp / (gp + gx)

OPUS_IN_PRACTICE, GPT_IN_PRACTICE = split(OPUS), split(GPT)      # 0.92, 0.98
GPT_PRACTICE_GAP = (min(REF["practice"] - r["practice"] for r in GPT), max(REF["practice"] - r["practice"] for r in GPT))
OVERFIT = [r for r in OPUS if (r["practice"] - r["hill"]) - (REF["practice"] - REF["hill"]) > 0.03]   # C1, C5


def f2(x):
    return f"{x:.2f}"


def about(n, step=100):
    """'about 1,500' for 1,469."""
    return f"{int(round(n / step) * step):,}"
