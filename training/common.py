"""Shared helpers for the small-model training loops (expert iteration, GRPO)."""
import difflib
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from arena import core  # noqa: E402

# Training reward pool: the agent's own 30 sparring warriors (same distribution as the
# hidden hill, r = 0.83 with it over agent-level warriors, results/proxy_check.md),
# plus the 60-warrior training hill for breadth. Neither contains a hidden-hill warrior.
TRAIN_HILL = sorted((ROOT / "data" / "sparring").glob("*.red")) + sorted((ROOT / "training" / "train_hill").glob("*.red"))
EVAL_HILL = sorted((ROOT / "data" / "hill").glob("*.red"))
GATE_DIRS = [ROOT / "data" / "hill", ROOT / "data" / "sparring"]
CORPUS = [ROOT / "data" / "corpus"]
DWARF, REF = 6637 / 45000, 21899 / 45000

DOC_FILES = ["index.md", "opcodes.md", "modifiers.md", "addressing_modes.md", "labels.md", "operands.md", "metadata.md"]


def build_prompt():
    doc = "\n\n".join((ROOT / "doc" / "redcode" / f).read_text() for f in DOC_FILES)
    return (
        "Write an original Core War warrior in Redcode (ICWS '94, pMARS 0.9.4, coresize 8000, "
        "80000 cycles, 8000 processes, max length 100, min distance 100). It will fight a hill of "
        "strong human-written warriors; per round win = 3 points, tie = 1, loss = 0. "
        "Reply with the complete warrior in a single ```redcode code block, starting with ;redcode-94 "
        "and a ;name line. Do not copy published warriors.\n\n"
        "Redcode reference:\n\n" + doc
    )


CODE_RE = re.compile(r"```(?:redcode|red|asm)?\s*\n(.*?)```", re.S)


def extract(text):
    m = CODE_RE.findall(text)
    src = max(m, key=len) if m else text
    return src.strip() + "\n"


# Short published warriors. The copy gate's containment test needs 6+ instructions, so a
# published warrior of 3 to 5 instructions followed by dead code passes it: Gymnosperm
# Trickery (5 instructions) + 3 `dat #1, #1` lines earns reward 0.577 at 500 rounds. Training
# never rewards that: a published warrior of SHORT_MIN to 5 instructions found inside a longer
# sample, at >= core.COPY_EXACT of its instructions (constants included, order kept), makes the
# sample a copy. Checked for false positives (15 November 2026): 0 of 94 distinct agent warriors
# (runs/ and the tune set), 0 of 564 distinct published warriors against each other. One- and
# two-instruction warriors (the imp line, `jmp 0`) are left out: they are parts of countless
# original warriors, and the best of them is worth about 0.10 in reward.
# The verifier does not apply this rule yet (arena/core.py is unchanged).
SHORT_MIN = 3
_SHORT = None


def _short_published():
    global _SHORT
    if _SHORT is None:
        seen, _SHORT = set(), []
        for d in CORPUS + GATE_DIRS:
            for f in sorted(Path(d).rglob("*.red")):
                ins = core._strip(core.assemble(f.read_text(errors="replace"))[0])
                if SHORT_MIN <= len(ins) < 6 and tuple(ins) not in seen:
                    seen.add(tuple(ins))
                    _SHORT.append((f.stem, ins))
    return _SHORT


def short_copy(ins):
    """Name of the short published warrior contained in `ins`, or None."""
    a = core._strip(ins)
    for name, b in _short_published():
        if len(a) > len(b):
            sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
            if sum(bl.size for bl in sm.get_matching_blocks()) / len(b) >= core.COPY_EXACT:
                return name
    return None


def _score_one(args):
    src, hill, rounds = args
    ins, _ = core.assemble(src)
    if not ins:
        return {"valid": False, "copy": False, "score": 0.0, "len": 0, "published_sim": 0.0}
    gate = core.nearest_published(ins, GATE_DIRS)
    pub = core.nearest_published(ins, CORPUS)
    if gate["copy"] or pub["copy"] or short_copy(ins):
        # training never rewards published warriors, even ones the eval gate would allow
        return {"valid": True, "copy": True, "score": 0.0, "len": len(ins), "published_sim": max(pub["exact"], pub["struct"])}
    s = core.hill_score(core.play_hill(src, [Path(h) for h in hill], rounds, workers=1))
    return {"valid": True, "copy": False, "score": s, "len": len(ins), "published_sim": max(pub["exact"], pub["struct"])}


def score_many(sources, hill, rounds=50, workers=None):
    hill = [str(h) for h in hill]
    with ProcessPoolExecutor(workers) as ex:
        return list(ex.map(_score_one, [(s, hill, rounds) for s in sources], chunksize=4))


def reward(hill_score):
    return min(1.0, max(0.0, (hill_score - DWARF) / (REF - DWARF)))


def write_jsonl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def read_jsonl(path):
    return [json.loads(l) for l in open(path)]
