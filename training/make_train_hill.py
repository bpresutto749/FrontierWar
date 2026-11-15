#!/usr/bin/env python3
"""Build a training hill from the published corpus, disjoint from the evaluation
hill and from both sparring pools (the shipped 30 and the earlier 10), and also free of near-copies of them (so that a
derivative of a hidden-hill warrior cannot leak into training).

Output: training/train_hill/*.red (default 60 warriors, fixed seed).
"""
import random, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from arena import core

N, SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 60, 20261114
protected = [ROOT / "data" / "hill", ROOT / "data" / "sparring", ROOT / "data" / "sparring_small"]
prot_names = {p.stem for d in protected for p in d.glob("*.red")}
cands = []
for f in sorted((ROOT / "data" / "corpus").rglob("*.red")):
    if f.stem in prot_names:
        continue
    ins, _ = core.assemble(f.read_text(errors="replace"))
    if not ins:
        continue
    near = core.nearest_published(ins, protected)
    if max(near["exact"], near["struct"]) >= 0.6:   # stricter than the gate: drop relatives too
        continue
    cands.append(f)
# drop duplicates between the two corpora (same assembled code)
seen, uniq = set(), []
for f in cands:
    key = tuple(core.assemble(f.read_text(errors="replace"))[0])
    if key not in seen:
        seen.add(key); uniq.append(f)
random.Random(SEED).shuffle(uniq)
out = ROOT / "training" / "train_hill"
out.mkdir(parents=True, exist_ok=True)
for f in out.glob("*.red"):
    f.unlink()
for f in uniq[:N]:
    shutil.copy(f, out / f"{f.parent.name}_{f.name}")
print(f"{len(uniq)} eligible warriors, wrote {min(N, len(uniq))} to {out}")
