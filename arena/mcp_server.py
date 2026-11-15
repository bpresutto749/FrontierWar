"""MCP sidecar for the Core War task.

Tools (streamable HTTP on :8000/mcp):
  get_rules()                  - the scoring rules and settings
  list_sparring()              - ids of the sparring warriors (s01..s30)
  battle(source, opponents, rounds) - play a warrior against sparring warriors
  battle_custom(source, opponent_source, rounds) - play two sources of your own
  submit(source)               - set your final submission (last accepted one counts)
  status()                     - what is currently submitted, and the clock

Every tool reports the clock: minutes used and left of the 45-minute budget, counted from
the agent's first call to this server (the sidecar cannot see when the agent process
started; its first call comes within seconds of it).

The sparring warriors are black boxes: the agent can battle them but never sees
their source or their names (so it cannot copy them, or recall or download them
by name). The hidden hill never enters this container: the verifier scores the
submission in its own container. This service keeps the submission and an event
log under /results, which Harbor collects as artifacts after the run.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from arena import core

DATA = Path(os.environ.get("ARENA_DATA", "/srv/data"))
SPARRING = DATA / "sparring"
RESULTS = Path(os.environ.get("RESULTS_DIR", "/results"))
RULES = (Path(__file__).resolve().parent / "RULES.md").read_text()
MAX_ROUNDS = 500
BUDGET_MIN = float(os.environ.get("ARENA_BUDGET_MIN", "45"))

_lock = threading.Lock()
_t0: float | None = None
mcp = FastMCP(
    "corewar",
    instructions="Core War arena. Read get_rules, test warriors with battle, and set your final warrior with submit.",
    host=os.environ.get("HOST", "0.0.0.0"),
    port=int(os.environ.get("PORT", "8000")),
)


def _sparring():
    """(public id, path) pairs; ids are assigned in file-name order."""
    return [(f"s{i:02d}", p) for i, p in enumerate(sorted(SPARRING.glob("*.red")), 1)]


def _log(event: dict):
    RESULTS.mkdir(parents=True, exist_ok=True)
    event["t"] = round(time.time(), 3)
    with (RESULTS / "events.jsonl").open("a") as f:
        f.write(json.dumps(event) + "\n")


def _clock() -> str:
    """Start the clock on the first call; return the time used and left."""
    global _t0
    with _lock:
        if _t0 is None:
            _t0 = time.time()
            _log({"event": "clock_start"})
        used = (time.time() - _t0) / 60
    left = max(0.0, BUDGET_MIN - used)
    return (f"[clock: {used:.1f} of {BUDGET_MIN:.0f} min used, {left:.1f} min left; counted from your "
            f"first call to this server]")


@mcp.tool()
def get_rules() -> str:
    """Scoring rules, simulator settings and what counts as a valid submission."""
    return RULES + "\n" + _clock() + "\n"


@mcp.tool()
def list_sparring() -> str:
    """Ids of the 30 sparring warriors (none of them is on the hidden hill). Their
    source code is not available; play them with `battle`."""
    return "\n".join(i for i, _ in _sparring()) + "\n" + _clock()


@mcp.tool()
def battle(source: str, opponents: list[str] | None = None, rounds: int = 100) -> str:
    """Play your warrior (Redcode source) against sparring warriors (all of them by
    default, or a list of ids like ["s01", "s07"]) with the scoring settings.
    Returns wins/losses/ties and KotH points per opponent (1.0 = every round won)."""
    clock = _clock()
    rounds = max(1, min(int(rounds), MAX_ROUNDS))
    want = set(opponents or [])
    pairs = [(i, p) for i, p in _sparring() if not want or i in want]
    if not pairs:
        return "no such sparring warrior; call list_sparring"
    ins, msgs = core.assemble(source, rounds)
    if not ins:
        return "does not assemble:\n" + msgs
    res = core.play_hill(source, [p for _, p in pairs], rounds)
    for (i, _), r in zip(pairs, res):
        r.opponent = i
    _log({"event": "battle", "sha": hashlib.sha256(source.encode()).hexdigest()[:16],
          "opponents": [i for i, _ in pairs], "rounds": rounds, "mean": core.hill_score(res)})
    return core.table(res) + "   " + clock


@mcp.tool()
def battle_custom(source: str, opponent_source: str, rounds: int = 100) -> str:
    """Play two warriors of your own against each other (e.g. a new version against an old one)."""
    clock = _clock()
    rounds = max(1, min(int(rounds), MAX_ROUNDS))
    for s in (source, opponent_source):
        ins, msgs = core.assemble(s, rounds)
        if not ins:
            return "does not assemble:\n" + msgs
    with core.Source(source) as a, core.Source(opponent_source) as b:
        r = core.battle(a.path, b.path, "opponent", rounds)
    return core.table([r]) + "   " + clock


@mcp.tool()
def submit(source: str) -> str:
    """Set your final submission. You may submit many times; the last accepted
    submission is the one that is scored on the hidden hill. Any warrior that
    assembles is accepted here; originality is checked by the verifier."""
    clock = _clock()
    with _lock:
        ins, msgs = core.assemble(source)
        if not ins:
            _log({"event": "submit", "accepted": False, "reason": "does not assemble"})
            return "rejected: does not assemble\n" + msgs + "\n" + clock
        RESULTS.mkdir(parents=True, exist_ok=True)
        tmp = RESULTS / "submission.red.tmp"
        tmp.write_text(source)
        tmp.replace(RESULTS / "submission.red")
        sha = hashlib.sha256(source.encode()).hexdigest()[:16]
        hist = RESULTS / "history"
        hist.mkdir(exist_ok=True)
        n = len(list(hist.glob("*.red"))) + 1
        (hist / f"{n:03d}_{sha}.red").write_text(source)
        _log({"event": "submit", "accepted": True, "sha": sha, "length": len(ins), "history": f"{n:03d}_{sha}.red"})
        return f"accepted ({len(ins)} instructions, sha {sha}). This is now your final submission.\n{clock}"


@mcp.tool()
def status() -> str:
    """The clock (minutes used and left), whether a submission is set, and its first lines."""
    clock = _clock()
    p = RESULTS / "submission.red"
    if not p.exists():
        return clock + "\nno submission yet"
    return clock + "\ncurrent submission:\n" + "\n".join(p.read_text().splitlines()[:12])


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request):
    return JSONResponse({"ok": True})


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
