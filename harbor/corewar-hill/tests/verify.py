"""Verifier: scores the submitted warrior on the hidden hill.

Runs in its own container (environment_mode = "separate"). The hidden hill and
the corpus exist only here. The submission comes from the artifacts Harbor
collects after the run: the last accepted `submit` (arena sidecar), or, if that
is empty, /app/submission.red from the agent container.

hill_score = mean KotH points per round over the hill / 3, in [0, 1].
reward = (hill_score - DWARF) / (REF - DWARF), clipped to [0, 1]: the fraction of the
way from Dwarf, A. K. Dewdney's classic bomber and the example warrior in the agent's
documentation (hill score 0.1475), to the human expert reference Toxic (0.4866). 1.0 = reference level or better. Written as one
number to /logs/verifier/reward.txt, as the challenge requires; details.json holds
the raw hill score, the unclipped value and the per-opponent results.
It is 0 when the file is missing, does not assemble, or is a near-copy of any
published warrior in the corpus (581 warriors, hill and sparring included). The
one exemption is the exact bytes of the reference file itself, so the oracle can
be scored: reproducing it byte for byte earns exactly 1.0, any edit of it is gated.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from arena import core  # noqa: E402

import os
OUT = Path(os.environ.get("VERIFIER_OUT", "/logs/verifier"))
HILL = sorted((HERE / "data" / "hill").glob("*.red"))
assert len(HILL) == 30, "hidden hill missing"
SPARRING = HERE / "data" / "sparring"
CORPUS = HERE / "data" / "corpus"
DWARF = 6637 / 45000  # hill_score of Dwarf (doc/example_dwarf.red) at 500 rounds (0.147489)
REF = 21899 / 45000  # hill_score of the reference, solution/reference.red (0.486644)


# In a separate verifier environment Harbor re-creates every artifact at its
# *source* path (the `destination` only names the copy on the host). So the
# sidecar's submission appears at /results/submission.red and the agent's file at
# /app/submission.red. /logs/artifacts is never read: the agent can write there.
SUBMISSION_PATHS = [Path(os.environ.get("SIDECAR_SUBMISSION", "/results/submission.red")),
                    Path(os.environ.get("APP_SUBMISSION", "/app/submission.red"))]


# sha256 of the oracle's reference file as the verifier reads it (line endings normalised).
# It is the published Toxic plus one comment line, so the published file itself is not exempt:
# an agent that recalls or downloads Toxic byte for byte gets the copy gate, not 1.0 (judge review 4).
REFERENCE_SHA256 = "82160f7846bd950ca930a97cce9fa84dbfc64e344ed6bc74f7e8fc12c390da70"


def find_submission():
    for p in SUBMISSION_PATHS:
        if not p.is_file():
            continue
        if p.stat().st_size > core.MAX_SOURCE:
            return p, "\0" * (core.MAX_SOURCE + 1)       # too big: rejected by the sanitiser, never read
        text = p.read_text(errors="replace")
        if text.strip():
            return p, text
    return None, ""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    reward = {"reward": 0.0}
    details = {"hill_size": len(HILL), "rounds": core.ROUNDS}
    path, src = find_submission()
    details["source_file"] = str(path) if path else None
    if path is None:
        details["reason"] = "no submission"
    else:
        details["sha256"] = hashlib.sha256(src.encode()).hexdigest()
        ins, msgs = core.assemble(src)
        details["length"] = len(ins)
        if not ins:
            details["reason"] = "does not assemble"
            details["pmars"] = msgs
        else:
            exempt = hashlib.sha256(src.replace("\r", "").encode()).hexdigest() == REFERENCE_SHA256
            pub = core.nearest_published(ins, [CORPUS, HERE / "data" / "hill", SPARRING])
            details["nearest_published"] = pub
            details["nearest_published_similarity"] = max(pub["exact"], pub["struct"])
            details["reference_exemption"] = exempt
            if pub["copy"] and not exempt:
                details["reason"] = f"near-copy of published warrior {pub['warrior']}"
            else:
                res = core.play_hill(src, HILL)
                score = core.hill_score(res)
                raw = (score - DWARF) / (REF - DWARF)
                reward["reward"] = round(min(1.0, max(0.0, raw)), 6)
                details["hill_score"] = round(score, 6)
                details["reward_unclipped"] = round(raw, 6)
                details["per_opponent"] = {r.opponent: {"wins": r.wins, "losses": r.losses, "ties": r.ties,
                                                        "points": round(r.points, 4), "error": r.error} for r in res}
                details["reason"] = "scored"
    details["seconds"] = round(time.time() - t0, 1)
    (OUT / "reward.txt").write_text(f"{reward['reward']:.6f}\n")
    (OUT / "details.json").write_text(json.dumps(details, indent=1))
    print(f"reward {reward['reward']:.6f}  hill_score {details.get('hill_score', 0.0)}")
    print(details.get("reason"))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # always leave a reward file
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "reward.txt").write_text("0.000000\n")
        (OUT / "details.json").write_text(json.dumps({"reason": f"verifier error: {e!r}"}))
        print("verifier error", repr(e))
