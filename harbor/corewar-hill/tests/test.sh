#!/bin/bash
# Scores the submission on the hidden hill (see verify.py). Always writes
# /logs/verifier/reward.txt (one number in [0, 1]) and details.json.
set -uo pipefail
if [ ! -x /tests/pmars/pmars ]; then make -C /tests/pmars pmars >/dev/null 2>&1; fi
python3 /tests/verify.py
