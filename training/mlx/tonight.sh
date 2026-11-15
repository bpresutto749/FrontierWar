#!/bin/bash
# Tonight's sequence on the Mac, in the background: wait for run 1 to end; check its adapters
# (round 3's LoRA diverged to NaN, so adapter_r4 only writes '!!!!'); evaluate adapter_r3, the last
# finite one (chosen on the training pool: round-3 samples mean 0.137, round-4 samples 0), on the
# hidden hill exactly like the final adapter (120 samples, seed 1000, 100 rounds); then start run 2.
set -uo pipefail
cd "$(dirname "$0")/../.."
R1=training/mlx/runs/qwen7b-1114-2211
LOG=training/mlx/runs/tonight.log
if [ -z "${INNER:-}" ]; then
  INNER=1 nohup caffeinate -ims bash "$0" > "$LOG" 2>&1 &
  echo "started in the background (pid $!). Log: $(pwd)/$LOG"; exit 0
fi
PY=.venv-mlx/bin/python; MODEL=mlx-community/Qwen2.5-Coder-7B-Instruct-4bit
export ARENA_WORKERS=1 PYTHONUNBUFFERED=1
echo "=== $(date +%H:%M:%S) waiting for run 1"
until grep -qE "RUN_DONE|FAILED" "$R1/run.log" 2>/dev/null; do sleep 20; done
echo "=== $(date +%H:%M:%S) run 1 has ended; its adapters:"
for r in 1 2 3 4; do $PY training/mlx/check_adapter.py "$R1/adapter_r$r" --no-fallback; done
echo "=== $(date +%H:%M:%S) hidden-hill evaluation of adapter_r3"
$PY training/mlx/gen.py --model "$MODEL" --adapter "$R1/adapter_r3" --n 120 --seed 1000 --out "$R1/adapter_r3.eval.samples.jsonl" \
  && $PY training/mlx/score.py "$R1/adapter_r3.eval.samples.jsonl" "$R1/adapter_r3.eval.jsonl" --hill eval --rounds 100 \
  && $PY training/mlx/report.py "$R1" adapter_r3 > "$R1/REPORT_adapter_r3.md" && cat "$R1/REPORT_adapter_r3.md"
echo "=== $(date +%H:%M:%S) starting run 2"
bash training/mlx/run_fb.sh
echo "TONIGHT_DONE"
