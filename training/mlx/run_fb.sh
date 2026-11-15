#!/bin/bash
# Run 2: expert iteration WITH the environment's feedback. Each episode is what the agent does in
# the task, cut to one step: write a warrior, run the battle tool on it (the same per-opponent table
# against the 30 sparring warriors, or the assembler's messages), read that output, write a revision.
# Training keeps the best drafts and the revisions that beat their draft (training pool only).
# The hidden hill is touched once, at the end: base model vs final adapter, same episodes.
#   bash training/mlx/run_fb.sh       -> starts in the background (keeps the Mac awake), returns at once
#   WAIT_FOR=training/mlx/runs/<run 1> bash training/mlx/run_fb.sh   -> same, but first waits for that run to end
# Settings (environment): MODEL ROUNDS N NEVAL TOP TOP_REV LR. Log: training/mlx/runs/<name>/run.log
set -uo pipefail
cd "$(dirname "$0")/../.."
ROOT=$(pwd)
NAME=${NAME:-fb-qwen7b-$(date +%m%d-%H%M)}
OUT=training/mlx/runs/$NAME
if [ -z "${INNER:-}" ]; then
  mkdir -p "$OUT"
  INNER=1 NAME=$NAME nohup caffeinate -ims bash "$0" > "$OUT/run.log" 2>&1 &
  echo "started in the background (pid $!). Log: $ROOT/$OUT/run.log"
  echo "The Mac stays awake while it runs; keep it plugged in. You can close this window."
  exit 0
fi

if [ -n "${WAIT_FOR:-}" ]; then
  echo "waiting for $WAIT_FOR to finish (RUN_DONE or FAILED in its run.log) ..."
  until grep -qE "RUN_DONE|FAILED" "$WAIT_FOR/run.log" 2>/dev/null; do sleep 30; done
  echo "$(date +%H:%M:%S) it has finished; starting"
fi

PY=.venv-mlx/bin/python
MODEL=${MODEL:-mlx-community/Qwen2.5-Coder-7B-Instruct-4bit}
ROUNDS=${ROUNDS:-3}; N=${N:-192}; NEVAL=${NEVAL:-120}; TOP=${TOP:-0.25}; TOP_REV=${TOP_REV:-0.5}; LR=${LR:-1e-5}
export ARENA_WORKERS=1 PYTHONUNBUFFERED=1
step() { echo; echo "=== $(date +%H:%M:%S) $*"; }
die() { echo "FAILED: $*"; exit 1; }
cat > "$OUT/config.json" <<CFG
{"model": "$MODEL", "rounds": $ROUNDS, "episodes_per_round": $N, "eval_episodes": $NEVAL,
 "episode": "draft -> battle tool output (30 sparring warriors, 100 rounds each, as in the task) -> revision",
 "keep_top_drafts_per_archetype": $TOP, "keep_top_improving_revisions_per_archetype": $TOP_REV,
 "lora": "rank 8, scale 10, 16 layers, lr $LR, 2 epochs (at least 20 steps), batch 2, max 3072 tokens, fresh from the base model each round; a diverged (NaN) adapter falls back to its latest finite checkpoint (every 10 steps)",
 "temperature": 0.9, "top_p": 0.95, "train_rounds_per_opponent": 50, "eval_rounds_per_opponent": 100}
CFG

# LoRA scale 10 instead of mlx_lm's 20: run 1 (round 3) and the first run-2 attempt (round 1) both
# diverged to NaN after ~20 steps; a smaller LoRA output keeps the half-precision activations in range
printf 'lora_parameters:\n  rank: 8\n  dropout: 0.0\n  scale: 10.0\n' > "$OUT/lora.yaml"

# one episode batch: drafts, battle tool, revisions, scores.  episode TAG SEED N HILL ROUNDS [ADAPTER]
episode() {
  local T=$1 SEED=$2 NN=$3 HILL=$4 RR=$5 AD=${6:-}
  $PY training/mlx/gen.py --model "$MODEL" ${AD:+--adapter "$AD"} --n "$NN" --seed "$SEED" --out "$OUT/$T.drafts.jsonl" || return 1
  $PY training/mlx/feedback.py "$OUT/$T.drafts.jsonl" "$OUT/$T.fb.jsonl" --tag draft || return 1
  $PY training/mlx/revise.py --model "$MODEL" ${AD:+--adapter "$AD"} --inp "$OUT/$T.fb.jsonl" --seed "$SEED" --out "$OUT/$T.revs.jsonl" || return 1
  $PY training/mlx/score.py "$OUT/$T.drafts.jsonl" "$OUT/$T.drafts.$HILL.jsonl" --hill "$HILL" --rounds "$RR" || return 1
  $PY training/mlx/score.py "$OUT/$T.revs.jsonl" "$OUT/$T.revs.$HILL.jsonl" --hill "$HILL" --rounds "$RR" || return 1
}

step "smoke test: 6 episodes, selection, 2 LoRA steps"
S=$OUT/smoke; mkdir -p $S
(OUT=$S; episode s 99 6 train 10) || die "smoke episode"
$PY training/mlx/pick_fb.py --dir $S --rounds s --top 1 --top-rev 1 --out $S/sft/train.jsonl || die "smoke selection"
if [ -s $S/sft/train.jsonl ]; then
  $PY -m mlx_lm lora --model "$MODEL" --train --data $S/sft --adapter-path $S/adapter --iters 2 --batch-size 1 \
    --num-layers 16 --mask-prompt --max-seq-length 3072 --grad-checkpoint --steps-per-report 1 --steps-per-eval 1000 \
    --save-every 1000 || die "smoke LoRA"
fi

ADAPTER=""; DONE=""
for r in $(seq 0 "$ROUNDS"); do
  step "round $r: $N episodes (draft, battle tool, revision), scored on the training pool"
  episode "r$r" "$r" "$N" train 50 "$ADAPTER" || die "episodes r$r"
  DONE="$DONE r$r"
  [ "$r" = "$ROUNDS" ] && break
  step "round $r: select (best drafts and improving revisions per archetype, all rounds so far)"
  $PY training/mlx/pick_fb.py --dir "$OUT" --rounds $DONE --top "$TOP" --top-rev "$TOP_REV" --out "$OUT/sft_r$r/train.jsonl" || die "selection r$r"
  K=$(wc -l < "$OUT/sft_r$r/train.jsonl" | tr -d ' '); [ "$K" -gt 0 ] || die "nothing to train on in round $r"
  BS=$(( K < 2 ? K : 2 )); ITERS=$(( (2 * K + BS - 1) / BS )); [ "$ITERS" -lt 20 ] && ITERS=20
  step "round $r: LoRA on $K examples, $ITERS iterations"
  AD="$OUT/adapter_r$((r + 1))"
  lora() {
    $PY -m mlx_lm lora --model "$MODEL" --train --data "$OUT/sft_r$r" --adapter-path "$AD" \
      --iters "$ITERS" --batch-size "$BS" --num-layers 16 --learning-rate "$1" --mask-prompt --max-seq-length 3072 \
      --grad-checkpoint --steps-per-report 10 --steps-per-eval 100000 --save-every 10 --seed "$2" --config "$OUT/lora.yaml"
  }
  lora "$LR" "$r" || die "LoRA r$r"
  if ! $PY training/mlx/check_adapter.py "$AD"; then        # diverged, and no finite checkpoint
    mv "$AD" "$AD.nan"
    step "round $r: LoRA again at half the learning rate"
    lora "$(awk "BEGIN{print $LR / 2}")" "$((r + 100))" || die "LoRA r$r (retry)"
    if ! $PY training/mlx/check_adapter.py "$AD"; then
      echo "round $r: still not finite; the next round keeps the previous adapter"; continue
    fi
  fi
  ADAPTER="$AD"
done

step "held-out evaluation: base model, $NEVAL episodes, hidden hill"
episode base 1000 "$NEVAL" eval 100 || die "eval (base)"
$PY training/mlx/feedback.py "$OUT/base.revs.eval.jsonl" "$OUT/base.episodes.jsonl" --tag rev || die "eval practice score (base)"
step "held-out evaluation: final adapter, $NEVAL episodes, hidden hill"
episode final 1000 "$NEVAL" eval 100 "$ADAPTER" || die "eval (final)"
$PY training/mlx/feedback.py "$OUT/final.revs.eval.jsonl" "$OUT/final.episodes.jsonl" --tag rev || die "eval practice score (final)"
$PY training/mlx/report_fb.py "$OUT" > "$OUT/REPORT.md"
cat "$OUT/REPORT.md"
step "RUN_DONE"
