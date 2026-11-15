#!/bin/bash
# Expert iteration on Apple Silicon with MLX: Qwen2.5-Coder-7B-Instruct (4-bit) + LoRA.
# The hidden hill is touched once, at the end, to compare the base model with the final adapter.
#   bash training/mlx/run.sh          -> starts in the background (keeps the Mac awake), returns at once
# Settings (environment): MODEL ROUNDS N NEVAL TOP LR. Log: training/mlx/runs/<name>/run.log
set -uo pipefail
cd "$(dirname "$0")/../.."
ROOT=$(pwd)
NAME=${NAME:-qwen7b-$(date +%m%d-%H%M)}
OUT=training/mlx/runs/$NAME
if [ -z "${INNER:-}" ]; then
  mkdir -p "$OUT"
  INNER=1 NAME=$NAME nohup caffeinate -ims bash "$0" > "$OUT/run.log" 2>&1 &
  echo "started in the background (pid $!). Log: $ROOT/$OUT/run.log"
  echo "The Mac stays awake while it runs; keep it plugged in. You can close this window."
  exit 0
fi

PY=.venv-mlx/bin/python
MODEL=${MODEL:-mlx-community/Qwen2.5-Coder-7B-Instruct-4bit}
ROUNDS=${ROUNDS:-4}; N=${N:-256}; NEVAL=${NEVAL:-120}; TOP=${TOP:-0.25}; LR=${LR:-2e-5}
export ARENA_WORKERS=1 PYTHONUNBUFFERED=1
step() { echo; echo "=== $(date +%H:%M:%S) $*"; }
die() { echo "FAILED: $*"; exit 1; }
cat > "$OUT/config.json" <<EOF
{"model": "$MODEL", "rounds": $ROUNDS, "samples_per_round": $N, "eval_samples": $NEVAL, "keep_top_per_archetype": $TOP,
 "lora": "mlx_lm defaults (rank 8, scale 20), 16 layers, lr $LR, 2 epochs (at least 20 steps), batch 4, fresh from the base model each round",
 "temperature": 0.9, "top_p": 0.95, "train_rounds_per_opponent": 50, "eval_rounds_per_opponent": 100}
EOF

step "smoke test: 10 samples, scoring, selection, 2 LoRA steps"
S=$OUT/smoke
$PY training/mlx/gen.py --model "$MODEL" --n 10 --seed 99 --out $S/s.samples.jsonl || die "smoke generation"
$PY training/mlx/score.py $S/s.samples.jsonl $S/s.train.jsonl --hill train --rounds 10 || die "smoke scoring"
$PY training/mlx/pick.py $S/s.train.jsonl --top 1 --out $S/sft/train.jsonl || die "smoke selection"
if [ -s $S/sft/train.jsonl ]; then
  $PY -m mlx_lm lora --model "$MODEL" --train --data $S/sft --adapter-path $S/adapter --iters 2 --batch-size 1 \
    --num-layers 16 --mask-prompt --max-seq-length 2048 --grad-checkpoint --steps-per-report 1 --steps-per-eval 1000 \
    --save-every 1000 || die "smoke LoRA"
  $PY training/mlx/gen.py --model "$MODEL" --adapter $S/adapter --n 2 --seed 98 --max-tokens 64 --out $S/a.samples.jsonl || die "smoke generation with adapter"
fi

ADAPTER=""
for r in $(seq 0 "$ROUNDS"); do
  step "round $r: generate $N"
  $PY training/mlx/gen.py --model "$MODEL" ${ADAPTER:+--adapter "$ADAPTER"} --n "$N" --seed "$r" --out "$OUT/r$r.samples.jsonl" || die "generation r$r"
  step "round $r: score on the training pool"
  $PY training/mlx/score.py "$OUT/r$r.samples.jsonl" "$OUT/r$r.train.jsonl" --hill train --rounds 50 || die "scoring r$r"
  [ "$r" = "$ROUNDS" ] && break
  step "round $r: select (top $TOP per archetype, all rounds so far)"
  $PY training/mlx/pick.py "$OUT"/r*.train.jsonl --top "$TOP" --out "$OUT/sft_r$r/train.jsonl" || die "selection r$r"
  K=$(wc -l < "$OUT/sft_r$r/train.jsonl" | tr -d ' '); [ "$K" -gt 0 ] || die "nothing to train on in round $r"
  BS=$(( K < 4 ? K : 4 )); ITERS=$(( (2 * K + BS - 1) / BS )); [ "$ITERS" -lt 20 ] && ITERS=20
  step "round $r: LoRA on $K samples, $ITERS iterations"
  $PY -m mlx_lm lora --model "$MODEL" --train --data "$OUT/sft_r$r" --adapter-path "$OUT/adapter_r$((r + 1))" \
    --iters "$ITERS" --batch-size "$BS" --num-layers 16 --learning-rate "$LR" --mask-prompt --max-seq-length 2048 \
    --grad-checkpoint --steps-per-report 10 --steps-per-eval 100000 --save-every 100000 --seed "$r" || die "LoRA r$r"
  ADAPTER="$OUT/adapter_r$((r + 1))"
done

step "held-out evaluation: base model, $NEVAL fresh samples, hidden hill"
$PY training/mlx/gen.py --model "$MODEL" --n "$NEVAL" --seed 1000 --out "$OUT/base.eval.samples.jsonl" || die "eval generation (base)"
$PY training/mlx/score.py "$OUT/base.eval.samples.jsonl" "$OUT/base.eval.jsonl" --hill eval --rounds 100 || die "eval scoring (base)"
step "held-out evaluation: final adapter, $NEVAL fresh samples, hidden hill"
$PY training/mlx/gen.py --model "$MODEL" --adapter "$ADAPTER" --n "$NEVAL" --seed 1000 --out "$OUT/final.eval.samples.jsonl" || die "eval generation (final)"
$PY training/mlx/score.py "$OUT/final.eval.samples.jsonl" "$OUT/final.eval.jsonl" --hill eval --rounds 100 || die "eval scoring (final)"
$PY training/mlx/report.py "$OUT" > "$OUT/REPORT.md"
cat "$OUT/REPORT.md"
step "RUN_DONE"
