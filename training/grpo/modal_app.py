"""GRPO (training/grpo) on a Modal GPU (A100 80 GB by default; GRPO_GPU=H100 to change it at
launch: H100s need a payment method on the Modal account), 16 CPU cores for pMARS.

    pip install modal && modal setup                                      # once
    modal run training/grpo/modal_app.py::smoke                           # 2 steps of the real run
    modal run --detach training/grpo/modal_app.py::train --run qwen7b-grpo --max-steps 150
    modal app logs corewar-grpo                                           # follow a detached run
    modal run training/grpo/modal_app.py::evaluate --run qwen7b-grpo     # hidden hill, once
    modal volume get corewar-grpo qwen7b-grpo training/grpo/runs/        # download the run

Runs live on the Modal volume `corewar-grpo` (samples.jsonl, checkpoints, final adapter,
REPORT.md). The model weights are cached on the volume `corewar-hf-cache`.
"""
import os
import subprocess
import threading
from pathlib import Path

import modal

# The repository root on this machine; inside the container this file is /root/modal_app.py
# and the repository is mounted at /repo.
ROOT = Path(__file__).resolve().parents[2] if modal.is_local() else Path("/repo")
MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("gcc", "make", "libc6-dev")
    .pip_install("trl==1.17.1", "vllm==0.31.0", "peft", "datasets")
    # FlashInfer's top-p/top-k sampler is compiled at start-up and needs nvcc, which this image
    # does not have: vLLM's own sampler is used instead.
    .env({"HF_HOME": "/hf", "PYTHONUNBUFFERED": "1", "VLLM_USE_FLASHINFER_SAMPLER": "0"})
    .add_local_dir(str(ROOT), remote_path="/repo", ignore=[
        "**/.git/**", "**/*.o", "pmars/pmars", "harbor/**", "runs/**", "media/**", "video/**",
        "jobs/**", "training/grpo/runs/**", "training/mlx/runs/**", "**/.venv*/**"])
)
runs = modal.Volume.from_name("corewar-grpo", create_if_missing=True)
hf = modal.Volume.from_name("corewar-hf-cache", create_if_missing=True)
app = modal.App("corewar-grpo", image=image)
GPU = dict(gpu=os.environ.get("GRPO_GPU", "A100-80GB"), cpu=16, memory=65536, volumes={"/out": runs, "/hf": hf})


def _run(cmd):
    """Build pMARS for Linux, then run cmd while committing the volumes every 5 minutes, so a
    detached run can be read (and resumed) before it ends."""
    subprocess.run(["make", "-B", "-C", "/repo/pmars", "pmars"], check=True, capture_output=True)
    stop = threading.Event()

    def commit_loop():
        while not stop.wait(300):
            runs.commit()

    t = threading.Thread(target=commit_loop, daemon=True)
    t.start()
    try:
        subprocess.run(cmd, check=True, cwd="/repo/training/grpo")
    finally:
        stop.set()
        runs.commit()
        hf.commit()


@app.function(timeout=8 * 3600, **GPU)
def train(run: str = "qwen7b-grpo", model: str = MODEL, max_steps: int = 150, lr: float = 1e-5,
          tie_weight: float = 0.0, extra: str = ""):
    import os
    os.environ["GRPO_TIE_WEIGHT"] = str(tie_weight)
    _run(["python", "train.py", "--model", model, "--out", f"/out/{run}", "--max-steps", str(max_steps),
          "--lr", str(lr), "--workers", "16", *extra.split()])


@app.function(timeout=3600, **GPU)
def smoke(model: str = MODEL):
    """Two steps of the real configuration: checks the whole loop, gives the time per step and
    the base model's reward distribution (the first two lines of the log)."""
    import shutil
    shutil.rmtree("/out/smoke", ignore_errors=True)     # a fresh run, not a resumed one
    _run(["python", "train.py", "--model", model, "--out", "/out/smoke", "--max-steps", "2", "--save-steps", "1000",
          "--workers", "16"])


@app.function(timeout=8 * 3600, **GPU)
def train_agent(run: str = "qwen7b-agent", model: str = MODEL, max_steps: int = 100, extra: str = ""):
    """Multi-turn GRPO with the `spar` practice tool (agent.py)."""
    import shutil
    if max_steps <= 2:
        shutil.rmtree(f"/out/{run}", ignore_errors=True)      # a smoke run starts from scratch
    _run(["python", "agent.py", "--model", model, "--out", f"/out/{run}", "--max-steps", str(max_steps),
          "--workers", "16", *extra.split()])


@app.function(timeout=2 * 3600, **GPU)
def evaluate_agent(run: str = "qwen7b-agent", n: int = 64, adapter: str = ""):
    """Two-turn evaluation on the hidden hill (evaluate_agent.py): draft, spar report, final."""
    _run(["python", "evaluate_agent.py", "--run", f"/out/{run}", "--n", str(n), "--workers", "16",
          *(["--adapter", f"/out/{run}/{adapter}"] if adapter else [])])
    print(Path(f"/out/{run}/AGENT_REPORT.md").read_text())


@app.function(timeout=3600, **GPU)
def probe(n: int = 64, styles: str = "mlx,mlx_dwarf,route1", sampling: str = "1.0:1.0,0.8:0.95", model: str = MODEL):
    """Base model only: share of valid and winning samples per prompt and sampling setting."""
    _run(["python", "probe.py", "--model", model, "--n", str(n), "--styles", styles, "--sampling", sampling])


@app.function(timeout=2 * 3600, **GPU)
def evaluate(run: str = "qwen7b-grpo", n: int = 64, adapter: str = "", tag: str = ""):
    """adapter: a checkpoint directory of the run (e.g. checkpoint-50) instead of final; tag
    names the output files (e.g. step50.REPORT.md), so the evaluations of a run do not overwrite
    each other."""
    _run(["python", "evaluate.py", "--run", f"/out/{run}", "--n", str(n), "--workers", "16",
          *(["--adapter", f"/out/{run}/{adapter}"] if adapter else []), *(["--tag", tag] if tag else [])])
    print(Path(f"/out/{run}/{tag + '.' if tag else ''}REPORT.md").read_text())
