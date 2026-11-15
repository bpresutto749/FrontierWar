"""Core War arena: pMARS wrapper, source sanitiser, near-copy check and hill scoring.

Everything that decides a reward lives here and is shared by the MCP sidecar
(sparring feedback), the verifier (hidden hill) and the local tools, so the three
can never disagree about the rules.
"""
from __future__ import annotations

import difflib
import os
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

PMARS = Path(os.environ.get("PMARS", Path(__file__).resolve().parent.parent / "pmars" / "pmars"))

# Standard ICWS '94 hill settings (pMARS defaults): coresize 8000, 80000 cycles,
# 8000 processes, max length 100, min distance 100.  -f uses pMARS's fixed
# position series, so every score is exactly reproducible.
ROUNDS = 500                  # per opponent in the verifier (sidecar battles default to 100)
BATTLE_TIMEOUT = 120          # seconds; a hung battle scores as a loss for the submission
MAX_LINE = 200                # pMARS 0.9.4 hangs on source lines longer than ~256 chars
MAX_SOURCE = 20000            # bytes
COPY_EXACT = 0.80
COPY_STRUCT = 0.90


# pMARS is C code from the 1990s with fixed-size buffers. Defence in depth: when
# running as root (the verifier's default), run it as an unprivileged user so a
# crafted warrior that crashed or subverted the simulator still could not write
# the reward file.
def _sim_kwargs():
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        try:
            import pwd
            pwd.getpwnam("nobody")
            return {"user": "nobody", "group": "nogroup" if _group_exists("nogroup") else None}
        except KeyError:
            pass
    return {}


def _group_exists(name):
    try:
        import grp
        grp.getgrnam(name)
        return True
    except KeyError:
        return False


_UNPRIVILEGED_OK = True


def run_pmars(args, timeout):
    """Run pMARS, as `nobody` when we are root. If the unprivileged user cannot
    reach the binary or the files (e.g. a 0700 temp dir in a local test), fall back
    to the current user once and remember it, rather than scoring everything 0."""
    global _UNPRIVILEGED_OK
    cmd = [str(PMARS), *args]
    if _UNPRIVILEGED_OK:
        kw = {k: v for k, v in _sim_kwargs().items() if v is not None}
        if kw:
            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd="/tmp", **kw)
                if not ("Permission denied" in p.stderr or "can't open" in p.stderr.lower()):
                    return p
            except PermissionError:
                pass
            _UNPRIVILEGED_OK = False
            print("warning: pMARS cannot run as nobody here; running it as the current user", file=sys.stderr)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd="/tmp")


# ---------------------------------------------------------------- sanitising
def sanitize(text: str) -> str | None:
    """Return a source pMARS can safely assemble, or None if the file is invalid.
    Comment lines are cut to MAX_LINE characters; an over-long code line loses its
    inline comment; a code line still longer than MAX_LINE makes the file invalid."""
    if len(text.encode("utf-8", "replace")) > MAX_SOURCE:
        return None
    out = []
    # \r\n and a lone \r both end a line, as when the verifier reads the file (universal
    # newlines); deleting a lone \r instead would join two lines in the sidecar only (review 5)
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if len(line) > MAX_LINE:
            if line.lstrip().startswith(";"):
                line = line[:MAX_LINE]
            else:
                line = line.split(";", 1)[0].rstrip()
                if len(line) > MAX_LINE:
                    return None
        out.append(line)
    return "\n".join(out) + "\n"


class Source:
    """A sanitised warrior written to a private temp file (context manager)."""

    def __init__(self, text: str):
        self.clean = sanitize(text)
        self.path = None

    def __enter__(self):
        if self.clean is not None:
            fd, p = tempfile.mkstemp(suffix=".red")
            with os.fdopen(fd, "w") as f:
                f.write(self.clean)
            os.chmod(p, 0o644)
            self.path = p
        return self

    def __exit__(self, *exc):
        if self.path:
            os.unlink(self.path)


# ---------------------------------------------------------------- assembling
_DUMMY = ";redcode-94\n;name dummy\n        dat #0, #0\n"


def assemble(text: str, rounds: int | None = None) -> tuple[list[str], str]:
    """Assembled instructions of `text` (labels and comments removed) and pMARS's
    messages. An empty list means the warrior does not assemble.

    The warrior is assembled in exactly the context it is scored in: two warriors,
    the same round count and the same settings. pMARS predefines WARRIORS, ROUNDS,
    CORESIZE and friends for the preprocessor, so a source assembled alone with
    `-r 0` can differ from the code that actually fights (e.g. `for (WARRIORS-1)`
    blocks). The opponent is a one-line DAT, so each round ends at once."""
    rounds = ROUNDS if rounds is None else rounds
    with Source(text) as s, Source(_DUMMY) as d:
        if s.path is None:
            return [], f"invalid source: a code line is longer than {MAX_LINE} characters or the file exceeds {MAX_SOURCE} bytes"
        try:
            p = run_pmars(["-r", str(rounds), "-f", s.path, d.path], 60)
        except subprocess.TimeoutExpired:
            return [], "pMARS timed out while assembling"
    msgs = (p.stdout + p.stderr)
    ins, block = [], 0
    for line in p.stdout.splitlines():
        if line.startswith("Program "):
            block += 1
            continue
        if block == 1:
            t = line.strip()
            m = re.search(r"([A-Z]{3}\.[A-Z]{1,2})\s+(.*)$", t)
            if m and not t.startswith("ORG"):
                ins.append(m.group(1) + " " + re.sub(r"\s+", "", m.group(2)))
    if block < 2:          # the submission did not assemble, so no listings were printed
        return [], msgs.strip()[-1500:]
    return ins, msgs.strip()[-1500:]


# ---------------------------------------------------------------- copy check
EMPTY = "DAT.F $0,$0"           # identical to an empty core cell: padding, not code


def _strip(ins):
    return [x for x in ins if x != EMPTY]


def _loose(x):
    """An instruction without its numbers, with forms that behave the same written the same
    way: CMP is SEQ; SUB of an immediate is ADD of its negation; the modifier of SPL, JMP,
    NOP and DAT and the A mode # or $ of SPL and JMP change nothing (`spl #0` and `spl $0`
    both split to the line itself)."""
    m = re.match(r"([A-Z]{3})(?:\.([A-Z]{1,2}))?\s*(.*)$", x)
    if not m:
        return re.sub(r"-?\d+", "", x)
    op, mod, ops = m.group(1), m.group(2) or "", re.sub(r"-?\d+", "", m.group(3))
    op = "SEQ" if op == "CMP" else op
    if op == "SUB" and ops[:1] == "#":          # sub #14, x is add #-14, x (judge review 4)
        op = "ADD"
    if op == "DAT":                             # a DAT's modifier never matters
        mod = ""
    if op in ("SPL", "JMP", "NOP"):
        mod = ""
        if op != "NOP" and ops[:1] == "#":
            ops = "$" + ops[1:]
    return f"{op}.{mod} {ops}"


def _structure(ins):
    """Opcode, modifier and addressing modes only (_loose), with runs of identical lines
    collapsed: an unrolled copy loop (12 x `MOV.I $,$`) is generic, not a fingerprint."""
    out = []
    for x in ins:
        t = _loose(x)
        if not out or out[-1] != t:
            out.append(t)
    return out


FRAGMENT_SHARE = 0.5


def _block_containment(a, b, min_block, whole_only=False):
    """Containment by contiguous common runs of at least `min_block` instructions (order
    preserved) between the submission `a` and the published warrior `b`.

    Default: share of the shorter sequence covered, so a copy pasted inside a bigger file
    and a verbatim piece of a bigger warrior are both caught.

    whole_only=True (used for the structural test, where constants are removed and the
    standard building blocks of Core War look alike): `b` inside `a`, or `a` being most of
    `b`, counted only when `a` reproduces at least FRAGMENT_SHARE of `b`. A short
    submission whose structure matches one building block of a much longer published
    warrior, such as the silk paper inside a paper/stone switcher, uses a published
    technique; it is not a copy of that warrior."""
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    covered = sum(bl.size for bl in sm.get_matching_blocks() if bl.size >= min_block)
    if not whole_only:
        return covered / min(len(a), len(b))
    of_b, of_a = covered / len(b), covered / len(a)
    return max(of_b, of_a if of_b >= FRAGMENT_SHARE else 0.0)


def copy_match(ins: list[str], ref: list[str]) -> tuple[bool, float, float]:
    """Near-copy test on assembled code with empty-cell padding removed.

    exact : instructions with their constants. max(ratio, containment), so a copy
            pasted inside a bigger file, or a verbatim piece of a bigger warrior, is
            caught. Flag at >= 0.8.
    struct: opcodes, modifiers and addressing modes, constants removed, repeated
            lines collapsed. max(ratio, containment by contiguous runs of >= 3),
            for programs with >= 8 distinct structural steps. Flag at >= 0.9. The
            contiguous-run and collapse rules keep decoy blocks and unrolled loops
            from "containing" a short or repetitive warrior by chance. The
            containment counts only when the submission contains the published
            warrior or is at least half of it: matching the structure of one building
            block of a larger warrior is using a published technique (_block_containment)."""
    a, b = _strip(ins), _strip(ref)
    if not a or not b:
        return False, 0.0, 0.0
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    exact = sm.ratio()
    if min(len(a), len(b)) >= 6:
        exact = max(exact, _block_containment(a, b, 1))
    struct = 0.0
    sa, sb = _structure(a), _structure(b)
    if min(len(sa), len(sb)) >= 8:
        struct = max(difflib.SequenceMatcher(None, sa, sb, autojunk=False).ratio(), _block_containment(sa, sb, 3, whole_only=True))
    return (exact >= COPY_EXACT or struct >= COPY_STRUCT), exact, struct


# Short published warriors. Below 8 distinct structural steps the structural test is off
# (short stones and clears all look alike), so a short published warrior was protected by the
# exact ratio alone: pasted with 3 extra DAT lines, or with 2 constants changed, Gymnosperm
# Trickery (5 instructions) earned 0.52 and 0.57 (judge review 3, EXPLOITS.md). For the short
# published warriors that are strong on their own (strong_short.json next to the warrior
# folders: hidden-hill score >= 0.20 ungated, built by exploits/strong_short.py), a submission
# is a copy when it holds, anywhere, a block with the same instructions line for line (opcode,
# modifier, addressing modes) whose numbers are mostly the same: at least SHORT_CLOSE of them
# within SHORT_TOL modulo the core size, its step size included. Nudging the step (3432 -> 3436)
# or padding it is a copy; the same technique with a step of one's own is not.
CORESIZE = 8000
SHORT_TOL, SHORT_CLOSE, SHORT_GAPS = 16, 0.6, 2


def _shape(x):
    return re.sub(r"-?\d+", "", x)


def _nums(x):
    return [int(v) for v in re.findall(r"-?\d+", x)]


def short_copy(ins: list[str], ref: list[str]) -> bool:
    """`ref` (a short published warrior) appears in `ins`: its instructions in order, with
    at most SHORT_GAPS extra lines slipped in between (a NOP in the loop), same _loose shapes,
    at least SHORT_CLOSE of the matched numbers within SHORT_TOL (modulo the core size), and
    one of its large constants (its step size) among them."""
    a, b = _strip(ins), _strip(ref)
    if len(b) < 3 or len(a) < len(b):
        return False
    sb, nb = [_loose(x) for x in b], [_nums(x) for x in b]
    sa, na = [_loose(x) for x in a], [_nums(x) for x in a]
    for i in range(len(a)):
        if sa[i] != sb[0]:
            continue
        pos, k, gaps = [i], 1, 0
        for j in range(i + 1, len(a)):
            if k == len(b) or gaps > SHORT_GAPS:
                break
            if sa[j] == sb[k]:
                pos.append(j); k += 1
            else:
                gaps += 1
        if k < len(b) or gaps > SHORT_GAPS:
            continue
        tot = ok = big = 0
        for j, p in enumerate(pos):
            for u, v in zip(na[p], nb[j]):
                d = (u - v) % CORESIZE
                close = min(d, CORESIZE - d) <= SHORT_TOL
                tot += 1; ok += close
                big += close and min(v % CORESIZE, -v % CORESIZE) >= 100     # a step size, not an offset
        # small offsets always match (a generic stone uses -1..-12 like any other), so the
        # published warrior's own large constants decide: one of them (its step size) must be
        # within tolerance. An original warrior that reuses the technique with its own step is
        # not a copy (judge review 5: an honest stone/imp with step 2000 was zeroed as s4b).
        # A warrior with no large constant at all is a copy only if every number matches.
        has_big = any(min(v % CORESIZE, -v % CORESIZE) >= 100 for row in nb for v in row)
        if (tot == 0 or ok / tot >= SHORT_CLOSE) and (big > 0 if has_big else ok == tot):
            return True
    return False


_ASM_CACHE: dict[str, list[str]] = {}
_STRONG: dict[str, set] = {}


def strong_short(d: Path) -> set:
    """Keys ("corpus/drq/x.red") of the strong short published warriors, from the
    strong_short.json next to the warrior folder `d` (empty set if there is none)."""
    root = Path(d).parent
    if str(root) not in _STRONG:
        f = root / "strong_short.json"
        _STRONG[str(root)] = set(json.loads(f.read_text())["warriors"]) if f.exists() else set()
    return _STRONG[str(root)]


def nearest_published(ins: list[str], corpus_dirs: list[Path]) -> dict:
    best = {"copy": False, "exact": 0.0, "struct": 0.0, "warrior": None}
    for d in corpus_dirs:
        strong = strong_short(d)
        for f in sorted(Path(d).rglob("*.red")):
            key = str(f)
            if key not in _ASM_CACHE:
                _ASM_CACHE[key] = assemble(f.read_text(errors="replace"))[0]
            c, e, s = copy_match(ins, _ASM_CACHE[key])
            short = f"{Path(d).name}/{f.relative_to(d)}" in strong and short_copy(ins, _ASM_CACHE[key])
            c = c or short
            if (c, max(e, s)) > (best["copy"], max(best["exact"], best["struct"])):
                best = {"copy": c, "exact": round(e, 3), "struct": round(s, 3), "warrior": f.stem}
                if short:
                    best["rule"] = "short published warrior, same instructions, numbers within tolerance"
    return best


# ---------------------------------------------------------------- battles
@dataclass
class Result:
    opponent: str
    wins: int
    losses: int
    ties: int
    rounds: int
    error: str | None = None

    @property
    def points(self) -> float:            # KotH points per round / 3, in [0, 1]
        return (3 * self.wins + self.ties) / (3 * self.rounds)


def battle(a_path: str, b_path: str, name: str, rounds: int = ROUNDS) -> Result:
    args = ["-b", "-k", "-r", str(rounds), "-f", a_path, b_path]
    try:
        p = run_pmars(args, BATTLE_TIMEOUT)
    except subprocess.TimeoutExpired:
        try:   # a slow machine is not the warrior's fault: retry once with a long timeout
            p = run_pmars(args, 4 * BATTLE_TIMEOUT)
        except subprocess.TimeoutExpired:
            return Result(name, 0, rounds, 0, rounds, "timeout")
    lines = [l for l in p.stdout.strip().splitlines() if l.split() and l.split()[0].lstrip("-").isdigit()]
    if len(lines) < 2:
        return Result(name, 0, rounds, 0, rounds, (p.stdout + p.stderr).strip()[-300:] or "no result")
    w1, t1 = map(int, lines[-2].split()[:2])
    w2, _ = map(int, lines[-1].split()[:2])
    return Result(name, w1, w2, t1, rounds)


def play_hill(text: str, opponents: list[Path], rounds: int = ROUNDS, workers: int | None = None) -> list[Result]:
    """Battle a warrior source against every opponent file. Opponents are trusted
    files shipped with the task; they are sanitised too, for safety."""
    # os.cpu_count() reports the host's CPUs inside a CPU-limited container, so the
    # pool size comes from ARENA_WORKERS (default 2, the task's CPU allocation).
    workers = workers or max(1, min(len(opponents), int(os.environ.get("ARENA_WORKERS", "2"))))
    with Source(text) as s:
        if s.path is None:
            return [Result(o.stem, 0, rounds, 0, rounds, "invalid source") for o in opponents]
        opp_srcs = [Source(o.read_text(errors="replace")) for o in opponents]
        for o in opp_srcs:
            o.__enter__()
        try:
            with ThreadPoolExecutor(workers) as ex:
                return list(ex.map(lambda io: battle(s.path, io[1].path, io[0].stem, rounds),
                                   zip(opponents, opp_srcs)))
        finally:
            for o in opp_srcs:
                o.__exit__(None, None, None)


def hill_score(results: list[Result]) -> float:
    return sum(r.points for r in results) / len(results) if results else 0.0


def table(results: list[Result]) -> str:
    rows = [f"{'opponent':28s} {'win':>4s} {'loss':>4s} {'tie':>4s}  points"]
    for r in results:
        extra = f"  ({r.error})" if r.error else ""
        rows.append(f"{r.opponent:28s} {r.wins:4d} {r.losses:4d} {r.ties:4d}  {r.points:.3f}{extra}")
    rows.append(f"{'MEAN':28s} {'':14s}  {hill_score(results):.3f}")
    return "\n".join(rows)
