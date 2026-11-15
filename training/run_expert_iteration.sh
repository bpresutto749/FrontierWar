#!/bin/bash
# Expert iteration on the TRAINING hill only; the evaluation hill is touched once, at the end.
# usage: bash training/run_expert_iteration.sh [MODEL] [ROUNDS] [N]
set -euo pipefail
cd "$(dirname "$0")"
MODEL=${1:-Qwen/Qwen2.5-Coder-7B-Instruct}
ROUNDS=${2:-3}
N=${3:-256}
OUT=runs/$(basename "$MODEL")
mkdir -p "$OUT"
LORA=""
for r in $(seq 0 "$ROUNDS"); do
  python3 generate.py --model "$MODEL" ${LORA:+--lora "$LORA"} --n "$N" --seed "$r" --out "$OUT/r$r.samples.jsonl"
  python3 score.py "$OUT/r$r.samples.jsonl" "$OUT/r$r.train.jsonl" --hill train | tee "$OUT/r$r.train.log"
  [ "$r" = "$ROUNDS" ] && break
  python3 select_sft.py "$OUT"/r*.train.jsonl --top 0.25 --out "$OUT/r$r.sft.jsonl"
  python3 sft_lora.py --model "$MODEL" --data "$OUT/r$r.sft.jsonl" --out "$OUT/adapter_r$((r+1))"
  LORA="$OUT/adapter_r$((r+1))"
done
# Held-out evaluation: base model (round 0 samples) vs final adapter, fresh samples, evaluation hill.
python3 generate.py --model "$MODEL" --n 64 --seed 1000 --out "$OUT/base.eval.samples.jsonl"
python3 score.py "$OUT/base.eval.samples.jsonl" "$OUT/base.eval.jsonl" --hill eval --rounds 100 | tee "$OUT/base.eval.log"
python3 generate.py --model "$MODEL" --lora "$LORA" --n 64 --seed 1000 --out "$OUT/final.eval.samples.jsonl"
python3 score.py "$OUT/final.eval.samples.jsonl" "$OUT/final.eval.jsonl" --hill eval --rounds 100 | tee "$OUT/final.eval.log"
python3 report.py "$OUT" > "$OUT/REPORT.md"
cat "$OUT/REPORT.md"
