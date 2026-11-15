PY ?= python3
HARBOR ?= harbor
MODEL ?= anthropic/claude-opus-5-5
TASK = harbor/corewar-hill
STOP_EARLY_RUNS = $(shell cat runs/final-env/start_times.txt 2>/dev/null)
STOP_EARLY_RUNS_V2 = $(shell cat runs/v2-small-pool/start_times.txt 2>/dev/null)
HARBOR_RUNS = $(shell cat runs/harbor/start_times.txt 2>/dev/null)
HARBOR_RUNS_V4 = $(shell cat runs/harbor/start_times_v4.txt 2>/dev/null)

.PHONY: all pmars task lint test eval baselines exploits trajectories overfit videos harbor-reference harbor-nop harbor-agent harbor-all clean

all: pmars task test eval

pmars:
	$(MAKE) -C pmars pmars

# Generate the Harbor task directory from the sources (single source of truth).
task:
	$(PY) build_task.py

lint: task
	$(HARBOR) lint harbor/corewar-hill
	$(HARBOR) lint harbor/corewar-hill-public

# Unit and regression tests: scoring anchors, sanitiser, copy gate, exploit regressions.
test: pmars
	$(PY) -m pytest -q tests

# One command, no Docker needed: reference, baselines, recorded agent runs -> results/eval.md
eval: pmars
	$(PY) eval.py --markdown results/eval.md --json results/eval.json \
	  "reference=data/reference_toxic.red" \
	  "final-env-opus-5.5=runs/final-env/opus-5.5/*.red" \
	  "harbor-v4-opencode-opus-5.5=runs/harbor/final-v4/*.red" \
	  "harbor-opencode-opus-5.5=runs/harbor/final/*.red" \
	  "v2-small-pool-opus-5.5=runs/v2-small-pool/opus-5.5/*.red" \
	  "v1-opus-5.5=runs/opus-5.5/*.red" \
	  "v1-opus-5.5-lessons=runs/opus-5.5-lessons/*.red" \
	  "v1-sonnet-5.5=runs/sonnet-5.5/*.red" \
	  "codeclash-ladder-2026-07=runs/codeclash-ladder-2026-07/*.red" \
	  "baselines=baselines/*.red"
	@cat results/eval.md

# The exploit and simple-strategy sweep behind EXPLOITS.md
exploits: pmars
	$(PY) exploits/run_exploits.py
	$(PY) exploits/stop_early.py --out results/stop_early.md $(STOP_EARLY_RUNS)
	$(PY) exploits/stop_early.py --out results/stop_early_v2.md $(STOP_EARLY_RUNS_V2)

# Every submission of every recorded run, scored on its visible pool and on the hidden hill
trajectories: pmars
	$(PY) exploits/trajectories.py --spar data/sparring --out trajectories $(STOP_EARLY_RUNS)
	$(PY) exploits/trajectories.py --spar data/sparring_small --out trajectories_v2 $(STOP_EARLY_RUNS_V2)
	$(PY) exploits/trajectories.py --spar data/sparring --out trajectories_harbor $(HARBOR_RUNS)
	$(PY) exploits/trajectories.py --spar data/sparring --out trajectories_harbor_v4 $(HARBOR_RUNS_V4)
	$(MAKE) overfit

# Is the gap just overfitting? Splits it into the visible-pool gap and the excess visible->hidden drop
overfit: pmars
	$(PY) exploits/overfit_check.py "v4 Harbor (shipped)=results/trajectories_harbor_v4.json" \
	  "v3 Harbor=results/trajectories_harbor.json" "v3 local=results/trajectories.json"

# Harbor runs (need Docker). Judges' protocol: reference, do-nothing, 3+ agent runs.
harbor-reference: task
	$(HARBOR) run -p $(TASK) -a oracle
harbor-nop: task
	$(HARBOR) run -p $(TASK) -a nop
harbor-agent: task
	$(HARBOR) run -p $(TASK) -a opencode -m $(MODEL) -k 3 $(HARBOR_ARGS)
harbor-all: harbor-reference harbor-nop harbor-agent

clean:
	$(MAKE) -C pmars clean
	rm -rf harbor

# The videos (video/README.md): the drawing simulator is checked against pMARS, the two main videos are
# checked for text out of frame, overlapping or shown too briefly, then every scene is drawn and joined
videos: pmars
	$(PY) video/check_mars.py
	$(PY) video/audit.py pitch 4.0
	$(PY) video/audit.py demo_full 5.5
	$(PY) video/build.py all
