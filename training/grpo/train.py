#!/usr/bin/env python3
"""GRPO on the Core War environment: the model writes warriors, the training pool scores them,
and the score of each sample, relative to the other samples of its prompt, is the gradient.

Same prompts as the MLX expert-iteration run (training/mlx/prompts.py): a compact Redcode
reference, the strategy primer's archetypes in a few lines (no warrior code), and one task per
archetype (stone, paper, scanner, stone/imp, free), so every step asks for every style.
Reward: training/grpo/reward.py (rounds won on the training pool; 0 for copies). The hidden
hill is used once, by evaluate.py, after training.

Every scored sample is appended to OUT/samples.jsonl (step, archetype, wins, ties, reward,
source), so the run can be read warrior by warrior.

usage: train.py --model Qwen/Qwen2.5-Coder-7B-Instruct --out runs/qwen7b-grpo --max-steps 150
"""
import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from reward import Scorer, summary  # noqa: E402  (before torch: see Scorer)
# training/mlx/prompts.py, loaded from its file: putting training/mlx on sys.path would make
# a directory named "mlx" importable, and transformers would take it for Apple's MLX library.
_spec = importlib.util.spec_from_file_location("mlx_prompts", HERE.parent / "mlx" / "prompts.py")
_prompts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_prompts)
ARCHETYPES, messages = _prompts.ARCHETYPES, _prompts.messages
PREFILL, source_of = _prompts.PREFILL, _prompts.source_of
from common import ROOT, build_prompt  # noqa: E402  (loaded by reward.py)

DWARF = (ROOT / "doc" / "example_dwarf.red").read_text().strip()


def user_text(style, arch):
    """The user message. mlx: training/mlx/prompts.py. mlx_dwarf: the same plus the
    documentation's Dwarf as a syntax example (a published warrior: a copy scores 0, retuned
    variants pass the gate). route1: route 1's prompt (task + the full Redcode reference).
    probe.py measured each on the base model (README)."""
    if style == "mlx":
        return messages(arch)[0]["content"]
    if style == "mlx_dwarf":
        return (messages(arch)[0]["content"] + "\n\nSYNTAX EXAMPLE (the documentation's Dwarf, a published warrior: "
                "a copy scores 0)\n```redcode\n" + DWARF + "\n```")
    if style == "route1":
        return build_prompt() + f"\n\nWrite a warrior of this kind: {dict(ARCHETYPES)[arch]}."
    raise ValueError(style)


def prompt_text(tok, style, arch):
    # Qwen3 thinks before answering unless told not to; the reply here starts inside a code block.
    extra = {"enable_thinking": False} if "qwen3" in (tok.name_or_path or "").lower() else {}
    return tok.apply_chat_template([{"role": "user", "content": user_text(style, arch)}], tokenize=False,
                                   add_generation_prompt=True, **extra) + PREFILL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen2.5-Coder-7B-Instruct")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-steps", type=int, default=150)
    ap.add_argument("--prompts-per-step", type=int, default=8)
    ap.add_argument("--num-generations", type=int, default=8, help="samples per prompt (the GRPO group)")
    ap.add_argument("--micro-batch", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--max-completion", type=int, default=768)
    ap.add_argument("--prompt-style", default="mlx_dwarf", choices=["mlx", "mlx_dwarf", "route1"])
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--top-k", type=int, default=512, help="TRL needs top_k > 0 when top_p < 1")
    ap.add_argument("--save-steps", type=int, default=25)
    ap.add_argument("--vllm-memory", type=float, default=0.3)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--gate-example", action="store_true", help="Dwarf variants earn 0 in training (reward.py)")
    a = ap.parse_args()
    if a.gate_example:
        os.environ["GRPO_GATE_EXAMPLE"] = "1"      # before the scoring processes fork
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    scorer = Scorer(a.workers)
    scorer.warm()

    # One process, one GPU: vLLM's colocate mode still expects a torch.distributed setup.
    for k, v in {"RANK": "0", "LOCAL_RANK": "0", "WORLD_SIZE": "1", "MASTER_ADDR": "127.0.0.1", "MASTER_PORT": "29511"}.items():
        os.environ.setdefault(k, v)
    import torch
    import transformers
    import trl
    from datasets import Dataset
    from peft import LoraConfig
    from transformers import AutoTokenizer
    from trl import GRPOConfig, GRPOTrainer

    batch = a.prompts_per_step * a.num_generations             # samples per optimiser step
    assert batch % a.micro_batch == 0
    n_rows = max(a.max_steps * a.prompts_per_step, 5 * 40)
    names = [n for n, _ in ARCHETYPES]
    # Plain-text prompts that end inside the reply's code block, as in the MLX run: the chat
    # template, then PREFILL ("```redcode\n"). The warrior is what the model writes before it
    # closes the block (source_of). TRL's conversational format cannot prefill a reply.
    tok = AutoTokenizer.from_pretrained(a.model)
    text = {n: prompt_text(tok, a.prompt_style, n) for n in names}
    ds = Dataset.from_list([{"prompt": text[names[i % len(names)]], "arch": names[i % len(names)]} for i in range(n_rows)])

    log = open(out / "samples.jsonl", "a")
    calls = {"n": 0, "t": time.time()}

    def corewar_reward(completions, arch=None, **kw):
        texts = [c[-1]["content"] if isinstance(c, list) else c for c in completions]
        srcs = [source_of(t) for t in texts]
        res = scorer(srcs)
        calls["n"] += 1
        for s, r, ar in zip(srcs, res, arch or [None] * len(srcs)):
            log.write(json.dumps({"call": calls["n"], "arch": ar, **r, "source": s}) + "\n")
        log.flush()
        print(json.dumps({"call": calls["n"], "elapsed_s": round(time.time() - calls["t"]), **summary(res)}), flush=True)
        return [r["reward"] for r in res]

    cfg = GRPOConfig(
        output_dir=str(out),
        max_steps=a.max_steps,
        learning_rate=a.lr,
        per_device_train_batch_size=a.micro_batch,
        gradient_accumulation_steps=batch // a.micro_batch,
        num_generations=a.num_generations,
        max_completion_length=a.max_completion,
        temperature=a.temperature,
        top_p=a.top_p,
        top_k=a.top_k,
        beta=0.0,
        use_vllm=True,
        vllm_mode="colocate",
        vllm_gpu_memory_utilization=a.vllm_memory,
        vllm_max_model_length=4096,
        bf16=True,
        gradient_checkpointing=True,
        logging_steps=1,
        save_steps=a.save_steps,
        report_to="none",
        seed=a.seed,
    )
    # Multimodal models (Gemma 4, Qwen3.5 and later: *ForConditionalGeneration): LoRA goes on the
    # language model only (model.language_model.*).
    from transformers import AutoConfig
    arch = (AutoConfig.from_pretrained(a.model).architectures or [""])[0]
    multimodal = "ConditionalGeneration" in arch
    targets = (r".*language_model.*\.(q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)" if multimodal else "all-linear")
    peft = LoraConfig(r=a.lora_r, lora_alpha=2 * a.lora_r, lora_dropout=0.05, target_modules=targets, task_type="CAUSAL_LM")
    (out / "config.json").write_text(json.dumps({
        **vars(a), "samples_per_step": batch,
        "reward": {"rounds": int(os.environ.get("GRPO_ROUNDS", "50")), "tie_weight": float(os.environ.get("GRPO_TIE_WEIGHT", "0"))},
        "versions": {"trl": trl.__version__, "transformers": transformers.__version__, "torch": torch.__version__},
    }, indent=1))

    trainer = GRPOTrainer(model=a.model, reward_funcs=corewar_reward, args=cfg, train_dataset=ds, peft_config=peft)
    vg = getattr(trainer, "vllm_generation", None)
    if multimodal and vg is not None:
        # The vision and audio embedders are not trained, and some of their parameter names differ
        # between transformers and vLLM (embed_vision.pos_embedding): push only the language model.
        _iter = vg._iter_named_params

        def _language_model_only():
            for name, param in _iter():
                if not any(k in name for k in ("vision", "visual", "audio")):
                    yield name, param

        vg._iter_named_params = _language_model_only
    resume = any(out.glob("checkpoint-*"))
    trainer.train(resume_from_checkpoint=True if resume else None)
    trainer.save_model(str(out / "final"))
    print("saved adapter to", out / "final", flush=True)


if __name__ == "__main__":
    main()
