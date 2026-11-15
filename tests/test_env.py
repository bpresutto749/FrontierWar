"""Regression tests for the Core War environment (run with `make test`)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from arena import core  # noqa: E402

HILL = sorted((ROOT / "data" / "hill").glob("*.red"))
SPAR = sorted((ROOT / "data" / "sparring").glob("*.red"))
REF = (ROOT / "data" / "reference_toxic.red").read_text()
IMP = ";redcode-94\n        mov.i #0, 1\n"


def test_split_is_disjoint_and_as_documented():
    split = json.loads((ROOT / "data" / "split.json").read_text())
    assert len(HILL) == 30 and len(SPAR) == 30
    assert {p.stem for p in HILL} == set(split["hill"])
    assert {p.stem for p in SPAR} == set(split["sparring"])
    assert not ({p.stem for p in HILL} & {p.stem for p in SPAR})
    assert split["reference"] not in split["hill"] + split["sparring"]


def test_reference_is_elo_number_one():
    rank = json.loads((ROOT / "data" / "elo_ranking.json").read_text())["ranking"]
    assert rank[-1][0] == "toxic"


def test_reward_anchors_match_the_simulator():
    verify = (ROOT / "task_src" / "verify.py").read_text()
    assert "DWARF = 6637 / 45000" in verify and "REF = 21899 / 45000" in verify
    # 30 opponents x 500 rounds x 3 points = 45000: scores are exact multiples of 1/45000
    dwarf = (ROOT / "doc" / "example_dwarf.red").read_text()
    assert round(core.hill_score(core.play_hill(dwarf, HILL)) * 45000) == 6637
    assert round(core.hill_score(core.play_hill(REF, HILL)) * 45000) == 21899


def test_scores_are_deterministic():
    a = core.hill_score(core.play_hill(REF, HILL[:5]))
    b = core.hill_score(core.play_hill(REF, HILL[:5]))
    assert a == b


def test_sanitizer_blocks_the_long_line_hang():
    assert core.sanitize(";" + "x" * 300 + "\n") is not None
    assert len(core.sanitize(";" + "x" * 300 + "\n").splitlines()[0]) == core.MAX_LINE
    assert core.sanitize("mov 0, 1 " + "+0" * 200 + "\n") is None
    assert core.sanitize(";" * 30000) is None


def test_copy_gate_catches_published_copies_but_not_originals():
    gate = [ROOT / "data" / "corpus", ROOT / "data" / "hill", ROOT / "data" / "sparring"]
    for p in SPAR[:3] + HILL[:3]:
        ins = core.assemble(p.read_text())[0]
        assert core.nearest_published(ins, gate)["copy"]
    placeholder = core.assemble((ROOT / "doc" / "example_dwarf.red").read_text())[0]
    reference = core.assemble((ROOT / "data" / "reference_toxic.red").read_text())[0]
    flagged = set()
    for p in sorted((ROOT / "runs").rglob("*.red")):
        ins = core.assemble(p.read_text())[0]
        if ins == placeholder:      # some agents submitted the documentation's dwarf as a placeholder
            continue
        if ins == reference:        # the Harbor oracle run submits the reference (exempt by sha in the verifier)
            continue
        if core.nearest_published(ins, gate)["copy"]:
            flagged.add(p.relative_to(ROOT).as_posix())
    # No recorded agent submission is flagged. Until v4.1 one was: run C1's first, a 12-instruction
    # silk paper whose structure matched the paper block of Jack in the Box II (DECISIONS.md).
    assert flagged == set(), sorted(flagged)


def test_structural_fragment_is_a_technique_but_verbatim_pieces_and_half_copies_are_copies():
    import re
    gate = [ROOT / "data" / "corpus", ROOT / "data" / "hill", ROOT / "data" / "sparring"]
    c1 = ROOT / "runs/harbor/v4-opencode-opus-5.5/corewar-hill__vYa5MUj/artifacts/history/001_a8f68575be385b01.red"
    assert not core.nearest_published(core.assemble(c1.read_text())[0], gate)["copy"]
    # a long published warrior with varied structure
    big = None
    for p in sorted((ROOT / "data" / "corpus").rglob("*.red")):
        ins = [i for i in core.assemble(p.read_text())[0] if i != "DAT.F $0,$0"]
        if len(ins) >= 40 and len(set(core._structure(ins))) >= 30:
            big = ins
            break
    assert big

    def src(lines):
        return ";redcode-94\n" + "\n".join(lines) + "\n"

    def retune(lines):          # every constant shifted: defeats the exact test, keeps the structure
        return [re.sub(r"-?\d+", lambda m: str(int(m.group()) + 7), l) for l in lines]

    piece = big[5:17]
    assert core.nearest_published(core.assemble(src(piece))[0], gate)["copy"]                 # verbatim piece
    half = retune(big[: int(len(big) * 0.6)])
    assert core.nearest_published(core.assemble(src(half))[0], gate)["copy"]                  # retuned 60 %
    whole = retune(big)
    assert core.nearest_published(core.assemble(src(whole))[0], gate)["copy"]                 # retuned whole


def test_task_keeps_hill_and_sparring_source_out_of_the_agent_image():
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "build_task.py")], check=True, capture_output=True)
    task = ROOT / "harbor" / "corewar-hill"
    env_files = {p.name for p in (task / "environment").rglob("*.red")}
    assert not env_files & {p.name for p in HILL}
    dockerfile = (task / "environment" / "Dockerfile").read_text()
    assert "sparring" not in dockerfile.replace("sparring warriors' source", "")
    assert (task / "tests" / "data" / "hill").exists()
    toml = (task / "task.toml").read_text()
    assert 'network_mode = "allowlist"' in toml and 'url = "http://localhost:8000/mcp"' in toml
    pub = (ROOT / "harbor" / "corewar-hill-public" / "task.toml").read_text()
    assert 'network_mode = "public"' in pub and 'url = "http://arena:8000/mcp"' in pub


def test_assembly_uses_the_battle_context():
    # a source that is an imp when assembled alone and something else in a 2-warrior battle
    src = ";redcode-94\nfor (2-WARRIORS)\n        mov.i #0, 1\nrof\nfor (WARRIORS-1)\n        spl #0, #0\n        jmp -1\nrof\n"
    ins, _ = core.assemble(src)
    assert ins == ["SPL.B #0,#0", "JMP.B $-1,$0"], ins


def test_padding_and_retuning_do_not_escape_the_gate():
    gate = [ROOT / "data" / "corpus", ROOT / "data" / "hill", ROOT / "data" / "sparring"]
    for f in sorted((ROOT / "exploits" / "cases").glob("*.red")):
        if f.name.startswith(("d2_", "ok_")):        # ok_: cases that must NOT be gated
            continue
        ins = core.assemble(f.read_text())[0]
        assert core.nearest_published(ins, gate)["copy"], f.name


def test_honest_reuse_of_a_short_technique_is_not_a_copy():
    gate = [ROOT / "data" / "corpus", ROOT / "data" / "hill", ROOT / "data" / "sparring"]
    for f in sorted((ROOT / "exploits" / "cases").glob("ok_*.red")):
        ins = core.assemble(f.read_bytes().decode("utf-8", "replace"))[0]
        assert ins and not core.nearest_published(ins, gate)["copy"], f.name


def test_lone_carriage_return_is_a_line_break_on_both_sides():
    raw = (ROOT / "exploits" / "cases" / "ok_lone_cr.red").read_bytes().decode("utf-8", "replace")
    assert "\r" in raw.replace("\r\n", "")
    assert core.assemble(raw)[0] == core.assemble(raw.replace("\r\n", "\n").replace("\r", "\n"))[0]


def test_clock_starts_on_first_call_and_is_in_every_reply(tmp_path, monkeypatch):
    monkeypatch.setenv("RESULTS_DIR", str(tmp_path))
    monkeypatch.setenv("ARENA_DATA", str(ROOT / "data"))
    import importlib
    import arena.mcp_server as srv
    srv = importlib.reload(srv)
    assert srv._t0 is None
    dwarf = (ROOT / "doc" / "example_dwarf.red").read_text()
    assert "[clock: 0.0 of 45 min used, 45.0 min left" in srv.status()
    out = srv.battle(dwarf, ["s01"], 5)
    assert out.splitlines()[-1].startswith("MEAN") and "min left" in out.splitlines()[-1]
    assert "min left" in srv.submit(dwarf) and "min left" in srv.battle_custom(dwarf, dwarf, 5)
    assert "min left" in srv.get_rules() and "min left" in srv.list_sparring()
    srv._t0 -= 50 * 60      # past the budget: never negative
    assert "45.0 min left" not in srv.status() and "0.0 min left" in srv.status()
