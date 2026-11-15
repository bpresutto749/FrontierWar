#!/bin/bash
# One-time setup of the MLX training run on this Mac (Apple Silicon). Log: training/mlx/setup.log
set -uo pipefail
cd "$(dirname "$0")/../.."                 # the repository root
mkdir -p training/mlx
exec > >(tee training/mlx/setup.log) 2>&1
echo "== $(date)  $(sysctl -n machdep.cpu.brand_string), $(sysctl -n hw.ncpu) cores, $(( $(sysctl -n hw.memsize) / 1073741824 )) GB"
echo "== pMARS, native build"
make -C pmars clean >/dev/null && make -C pmars pmars >/dev/null || { echo "PMARS BUILD FAILED"; exit 1; }
echo "expected 'Results: 46 7 147' -> $(./pmars/pmars -r 200 -b -f data/reference_toxic.red data/hill/blizzard.red | tail -1)"
echo "== Python environment (.venv-mlx)"
if command -v uv >/dev/null; then
  uv venv -q --python 3.12 .venv-mlx && uv pip install -q --python .venv-mlx/bin/python mlx-lm
else
  python3 -m venv .venv-mlx && .venv-mlx/bin/pip install -q mlx-lm
fi
.venv-mlx/bin/python -c "import mlx.core as mx, mlx_lm; print('mlx', mx.__version__, '| mlx_lm', mlx_lm.__version__, '|', mx.default_device())" || { echo "MLX INSTALL FAILED"; exit 1; }
echo "== model download (about 4.3 GB)"
.venv-mlx/bin/python -c "from huggingface_hub import snapshot_download as s; print(s('mlx-community/Qwen2.5-Coder-7B-Instruct-4bit'))" || { echo "DOWNLOAD FAILED"; exit 1; }
echo "== speed check"
.venv-mlx/bin/python -m mlx_lm generate --model mlx-community/Qwen2.5-Coder-7B-Instruct-4bit --max-tokens 200 \
  --prompt "Write a Core War imp in Redcode, then explain it in two sentences." 2>&1 | tail -6
echo "== scoring check: the reference on the hidden hill, 100 rounds (expect about 0.49)"
.venv-mlx/bin/python -c "
import sys, os, time; sys.path.insert(0, '.'); os.environ.setdefault('ARENA_WORKERS', str(os.cpu_count()))
from pathlib import Path; from arena import core
t = time.time(); s = core.hill_score(core.play_hill(Path('data/reference_toxic.red').read_text(), sorted(Path('data/hill').glob('*.red')), 100))
print(f'hill score {s:.4f} in {time.time() - t:.1f} s')"
echo SETUP_DONE
