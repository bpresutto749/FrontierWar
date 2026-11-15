#!/bin/bash
# CPU-only check that everything except the GPU steps works on this machine:
# builds pMARS, scores a few known warriors on the training pool and the hidden hill,
# selects SFT data and writes a report. Takes 2-5 minutes.
set -euo pipefail
cd "$(dirname "$0")/.."
make -C pmars pmars >/dev/null
python3 - <<'PY'
import json, glob
rows = [{"i": i, "text": "", "source": open(f).read()} for i, f in enumerate(sorted(glob.glob("baselines/*.red")))]
with open("/tmp/smoke.samples.jsonl", "w") as fh:
    for r in rows: fh.write(json.dumps(r) + "\n")
PY
mkdir -p /tmp/smoke_run
cd training
python3 score.py /tmp/smoke.samples.jsonl /tmp/smoke_run/r0.train.jsonl --hill train
python3 select_sft.py /tmp/smoke_run/r0.train.jsonl --top 0.5 --out /tmp/smoke_run/r0.sft.jsonl
python3 score.py /tmp/smoke.samples.jsonl /tmp/smoke_run/base.eval.jsonl --hill eval --rounds 100
cp /tmp/smoke_run/base.eval.jsonl /tmp/smoke_run/final.eval.jsonl
python3 report.py /tmp/smoke_run
echo "SMOKE TEST OK"
