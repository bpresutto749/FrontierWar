#!/usr/bin/env python3
"""Generate the Harbor task directory harbor/corewar-hill from the sources in this repo.

Single source of truth: arena/ (rules engine), pmars/ (simulator source),
data/ (sparring pool, hidden hill, corpus, reference), task_src/ (instruction,
verifier, local battle tool). Rerun after any change: `make task`.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HARBOR = ROOT / "harbor"

PMARS_SRC = [p for p in (ROOT / "pmars").iterdir()
             if p.suffix in (".c", ".h") or p.name in ("Makefile", "COPYING", "AUTHORS", "README.pmars")]

TASK_TOML = """schema_version = "1.4"
# variant: {variant}
artifacts = [
  { source = "/results/submission.red", service = "arena", destination = "submission.red" },
  { source = "/results/events.jsonl", service = "arena", destination = "events.jsonl" },
  { source = "/results/history", service = "arena", destination = "history" },
  { source = "/app/submission.red", destination = "app_submission.red" },
]

[task]
name = "junction-afterquery/corewar-hill"
version = "1.0.0"
description = "Write an original Redcode warrior that holds its own against a hidden hill of 30 human-written King-of-the-Hill warriors."
keywords = ["core-war", "redcode", "adversarial-program-synthesis", "generalization", "open-ended-search"]

[metadata]
category = "adversarial program synthesis"
difficulty_explanation = "With an exact simulator, a strategy primer and 30 black-box sparring warriors drawn from the same ladder as the hidden hill, frontier agents converge on one tuned archetype (a lone paper, stone or scanner), abandon composites, stop with budget left, and stay below a human expert warrior even on the opponents they can see. Scores are deterministic (pMARS fixed position series)."
reference = "Toxic by John Metcalf, #1 of 264 human warriors on the CodeClash CC:Ladder Elo ranking (chosen before any agent run)"
reference_hill_score = 0.486

[verifier]
timeout_sec = 900.0
environment_mode = "separate"
{verifier_network}

[agent]
timeout_sec = 2700.0
{agent_network}
[environment]
cpus = 2
memory_mb = 4096
network_mode = "public"
build_timeout_sec = 900.0
os = "linux"

[[environment.mcp_servers]]
name = "corewar"
transport = "streamable-http"
url = "{mcp_url}"

[environment.healthcheck]
command = "python3 -c \\"import urllib.request; urllib.request.urlopen('{health_url}', timeout=3)\\""
interval_sec = 2.0
start_period_sec = 60.0
start_interval_sec = 2.0
retries = 3
"""

AGENT_NET_ALLOWLIST = """# Agent phase: only common model APIs are reachable (the MCP sidecar shares the
# agent's network namespace under Harbor's egress control and is reached on
# localhost), so an agent cannot download published warriors. If your model
# endpoint is not listed, add it at run time: harbor run ... --allow-agent-host <host>
network_mode = "allowlist"
# Exact inference hosts only: no general-purpose file hosting (no *.googleapis.com,
# no *.amazonaws.com). Vertex AI or Bedrock users add their regional host.
allowed_hosts = [
  "api.anthropic.com", "api.openai.com", "*.openai.azure.com", "openrouter.ai",
  "generativelanguage.googleapis.com", "api.mistral.ai", "api.deepseek.com",
  "api.x.ai", "api.together.xyz", "api.fireworks.ai", "api.groq.com",
  "api.moonshot.ai", "api.z.ai",
]
"""

AGENT_NET_PUBLIC = """# Public-network variant, for Docker hosts where Harbor's egress control is
# unavailable. The agent could download published warriors here: see EXPLOITS.md.
network_mode = "public"
"""

VARIANTS = {
    # name: (agent network block, MCP URL seen from the agent container)
    "corewar-hill": (AGENT_NET_ALLOWLIST, "http://localhost:8000/mcp"),
    "corewar-hill-public": (AGENT_NET_PUBLIC, "http://arena:8000/mcp"),
}

COMPOSE = """services:
  main:
    depends_on:
      arena:
        condition: service_healthy
  arena:
    build:
      context: ./arena
    environment:
      HOST: "0.0.0.0"
      PORT: "8000"
      RESULTS_DIR: /results
      ARENA_DATA: /srv/data
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"]
      interval: 2s
      timeout: 3s
      retries: 60
"""

MAIN_DOCKERFILE = """FROM python:3.12-slim
# Agent workspace: the scoring simulator, the documentation and local tools.
# Neither the hidden hill nor the sparring warriors' source is in this image.
RUN apt-get update && apt-get install -y --no-install-recommends gcc make libc6-dev \\
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir mcp==1.30.0
COPY arena/pmars /opt/pmars-src
RUN make -C /opt/pmars-src pmars && mkdir -p /app/bin && cp /opt/pmars-src/pmars /app/bin/pmars && rm -rf /opt/pmars-src
COPY doc /app/doc
COPY battle.py /app/tools/battle.py
COPY spar.py /app/tools/spar.py
ENV COREWAR_MCP_URL={mcp_url}
RUN touch /app/submission.red
WORKDIR /app
"""

ARENA_DOCKERFILE = """FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc make libc6-dev \\
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir mcp==1.30.0
COPY pmars /srv/pmars
RUN make -C /srv/pmars pmars
COPY arena /srv/arena
COPY data /srv/data
RUN chmod -R a+rX /srv
ENV PYTHONPATH=/srv
RUN mkdir -p /results/history && touch /results/submission.red /results/events.jsonl
EXPOSE 8000
CMD ["python", "-m", "arena.mcp_server"]
"""

TESTS_DOCKERFILE = """FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc make libc6-dev \\
    && rm -rf /var/lib/apt/lists/*
COPY . /tests/
RUN make -C /tests/pmars pmars && chmod -R a+rX /tests
WORKDIR /tests
"""

TEST_SH = """#!/bin/bash
# Scores the submission on the hidden hill (see verify.py). Always writes
# /logs/verifier/reward.txt (one number in [0, 1]) and details.json.
set -uo pipefail
if [ ! -x /tests/pmars/pmars ]; then make -C /tests/pmars pmars >/dev/null 2>&1; fi
python3 /tests/verify.py
"""

SOLVE_SH = """#!/bin/bash
# Reference run: the human expert warrior Toxic (John Metcalf), the #1 warrior
# of the CodeClash CC:Ladder Elo ranking of 264 human warriors. It was fixed as
# the reference before any agent run. Submitted through the same MCP tool as an
# agent would. It does NOT write /app/submission.red: if the MCP server is
# unreachable the oracle must fail visibly instead of being rescued by the fallback.
set -e
python3 /solution/submit.py /solution/reference.red
"""

SUBMIT_PY = """import asyncio, sys
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


import os


async def main(path, url=os.environ.get("COREWAR_MCP_URL", "http://localhost:8000/mcp")):
    src = open(path).read()
    async with streamablehttp_client(url) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool("submit", {"source": src})
            print(res.content[0].text)

asyncio.run(main(*sys.argv[1:]))
"""


def copy_pmars(dst):
    dst.mkdir(parents=True, exist_ok=True)
    for p in PMARS_SRC:
        shutil.copy(p, dst / p.name)


def build(OUT, agent_network, mcp_url):
    if OUT.exists():
        shutil.rmtree(OUT)
    env = OUT / "environment"
    arena_ctx = env / "arena"
    # sidecar build context
    copy_pmars(arena_ctx / "pmars")
    (arena_ctx / "arena").mkdir(parents=True)
    for f in ("__init__.py", "core.py", "mcp_server.py", "RULES.md"):
        shutil.copy(ROOT / "arena" / f, arena_ctx / "arena" / f)
    shutil.copytree(ROOT / "data" / "sparring", arena_ctx / "data" / "sparring")
    (arena_ctx / "Dockerfile").write_text(ARENA_DOCKERFILE)
    # main container
    (env / "Dockerfile").write_text(MAIN_DOCKERFILE.replace("{mcp_url}", mcp_url))
    (env / "docker-compose.yaml").write_text(COMPOSE)
    shutil.copytree(ROOT / "doc", env / "doc")
    shutil.copy(ROOT / "task_src" / "battle_local.py", env / "battle.py")
    shutil.copy(ROOT / "task_src" / "spar.py", env / "spar.py")
    # task files
    health = mcp_url.replace("/mcp", "/health")
    verifier_net = 'network_mode = "no-network"' if "allowlist" in agent_network else "# public variant: the verifier inherits the public baseline, because enforcing no-network\n# needs Harbor's egress control, which this variant exists to do without"
    (OUT / "task.toml").write_text(TASK_TOML.replace("{variant}", OUT.name).replace("{agent_network}", agent_network)
                                   .replace("{verifier_network}", verifier_net)
                                   .replace("{mcp_url}", mcp_url).replace("{health_url}", health))
    shutil.copy(ROOT / "task_src" / "instruction.md", OUT / "instruction.md")
    # verifier: hidden hill + corpus live only here
    tests = OUT / "tests"
    copy_pmars(tests / "pmars")
    (tests / "arena").mkdir(parents=True)
    for f in ("__init__.py", "core.py"):
        shutil.copy(ROOT / "arena" / f, tests / "arena" / f)
    for sub in ("hill", "sparring", "corpus"):
        shutil.copytree(ROOT / "data" / sub, tests / "data" / sub)
    shutil.copy(ROOT / "data" / "strong_short.json", tests / "data" / "strong_short.json")   # short-copy rule (core.short_copy)
    shutil.copy(ROOT / "task_src" / "verify.py", tests / "verify.py")
    (tests / "test.sh").write_text(TEST_SH)
    (tests / "Dockerfile").write_text(TESTS_DOCKERFILE)
    # reference solution
    sol = OUT / "solution"
    sol.mkdir()
    shutil.copy(ROOT / "data" / "reference_oracle.red", sol / "reference.red")   # Toxic + one comment line: the only exempt text
    (sol / "solve.sh").write_text(SOLVE_SH)
    (sol / "submit.py").write_text(SUBMIT_PY)
    for p in (tests / "test.sh", sol / "solve.sh"):
        p.chmod(0o755)
    print("wrote", OUT)


def main():
    for name, (net, url) in VARIANTS.items():
        build(HARBOR / name, net, url)


if __name__ == "__main__":
    main()
