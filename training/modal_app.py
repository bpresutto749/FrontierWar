"""Run the expert-iteration experiment on a Modal GPU.

    pip install modal && modal setup          # once, with the Modal credits
    modal run training/modal_app.py           # ~2-4 h on one A100/H100
    modal run training/modal_app.py --rounds 2 --n 128   # quicker

The repository is copied into the container. pMARS is built there, and
training/run_expert_iteration.sh runs unchanged. The run directory
(samples, scores, adapters, REPORT.md) is written to a Modal volume and printed at the end.
"""
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parent.parent

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("gcc", "make", "libc6-dev")
    .pip_install("vllm==0.11.0", "trl==0.24.0", "peft==0.17.1", "datasets==4.2.0", "transformers==4.57.1")
    .add_local_dir(str(ROOT), remote_path="/repo", ignore=["**/.git/**", "**/*.o", "harbor/**", "runs/**/workdirs/**"])
)
volume = modal.Volume.from_name("corewar-training", create_if_missing=True)
app = modal.App("corewar-expert-iteration", image=image)


@app.function(gpu="A100-80GB", timeout=6 * 3600, volumes={"/out": volume}, cpu=16)
def train(model: str = "Qwen/Qwen2.5-Coder-7B-Instruct", rounds: int = 3, n: int = 256) -> str:
    import os
    import shutil
    import subprocess

    subprocess.run(["make", "-C", "/repo/pmars", "pmars"], check=True)
    os.environ["ARENA_WORKERS"] = "16"          # scoring is CPU-bound: use the container's cores
    subprocess.run(["bash", "/repo/training/run_expert_iteration.sh", model, str(rounds), str(n)], check=True)
    run_dir = Path("/repo/training/runs") / Path(model).name
    dest = Path("/out") / run_dir.name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(run_dir, dest)
    volume.commit()
    return (run_dir / "REPORT.md").read_text()


@app.local_entrypoint()
def main(model: str = "Qwen/Qwen2.5-Coder-7B-Instruct", rounds: int = 3, n: int = 256):
    print(train.remote(model, rounds, n))
