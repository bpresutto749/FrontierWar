#!/usr/bin/env python3
"""Checks that a LoRA adapter's weights are finite. A run of mlx_lm lora can diverge to NaN
(run 1, round 3: loss NaN from step 21-30 on); such an adapter only writes '!!!!' (token 0).
If adapters.safetensors is not finite, falls back to the latest finite checkpoint saved by
--save-every (the NaN file is kept as adapters.safetensors.nan). Exit 0 if a finite adapter is in place.
usage: check_adapter.py ADAPTER_DIR [--no-fallback]"""
import glob, os, shutil, sys

import mlx.core as mx


def finite(path):
    return not any(mx.any(mx.isnan(v) | mx.isinf(v)).item() for v in mx.load(path).values())


def main():
    d, fallback = sys.argv[1], "--no-fallback" not in sys.argv
    main_ = os.path.join(d, "adapters.safetensors")
    if finite(main_):
        print(f"{d}: weights finite"); return 0
    print(f"{d}: NON-FINITE weights (NaN or inf): the training diverged")
    if not fallback:
        return 1
    for ck in sorted(glob.glob(os.path.join(d, "*_adapters.safetensors")), reverse=True):
        if finite(ck):
            shutil.copy(main_, main_ + ".nan"); shutil.copy(ck, main_)
            print(f"  using the latest finite checkpoint instead: {os.path.basename(ck)}"); return 0
    print("  no finite checkpoint"); return 1


if __name__ == "__main__":
    sys.exit(main())
