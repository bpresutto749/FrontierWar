#!/usr/bin/env python3
"""The demo's scenes: one real Harbor + OpenCode run (C5), replayed from its logs.
Each scene is a factory taking the header's kicker, so the same drawing serves the short demo
(this file's SCENES: the test, the run, the result, why the gap) and the full video (demo_full.py).
The side-by-side game is replayed by mars.py and each outcome is asserted against pMARS.
Every number on screen comes from runs/harbor/ and results/ (trajectories_harbor_v4.md, the verifier's details.json).
usage: python video/demo.py [all | <scene name>]   -> video/build/<scene>.mp4"""
import bisect, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
from style import (W, H, F, M, BG, LINE, FG, MUTED, DIM, TRACK, RED, GREEN, RED_L, GREEN_L, ACC, ACC_L,
                   CARD, CODE_BG, LOSS, RUN_BAR, OPP_FILL, OPP_LINE, BLUE_T, CELL_EMPTY, CELL_GAP, RED_C, GREEN_C,
                   clamp, ramp, mix, fade, text, panel, arrow, render, base, head, ROOT,
                   terminal, term_line, TERM_GREEN, TERM_DIM)
from style import BLUE, BLUE_C as BLUE_L
sys.path.insert(0, ROOT)
from arena import core
import mars

CMD = "$ harbor run -p harbor/corewar-hill -a opencode -m anthropic/claude-opus-5-5 -k 5 -o jobs"
PARTS = ["The test", "The run", "The result", "Why the gap"]

def part(i, extra=""):
    return f"PART {i} OF 4  ·  {PARTS[i - 1].upper()}" + (f"  ·  {extra}" if extra else "")

# ---------------------------------------------------------------- one real game, replayed (checked against pMARS)
OPP = os.path.join(ROOT, "data", "hill", "blizzard.red")          # the secret opponent where the gap is largest
AI_SRC = os.path.join(ROOT, "runs", "harbor", "final-v4", "run_C5.red")   # the AI's final submission (run C5)
EX_SRC = os.path.join(ROOT, "data", "reference_toxic.red")         # the human reference (Toxic)
FPOS = 7253                                                         # same start position for both games
COLS, ROWS, CELL = 100, 80, 7
FIGHTS = None

def run_fight(src):
    out = subprocess.run([str(core.PMARS), "-r", "1", "-F", str(FPOS), src, OPP], capture_output=True, text=True).stdout
    ws = mars.parse_listing(out)
    m = mars.Mars(ws[0], ws[1], FPOS); snaps = []
    def cb(mm, ex):
        snaps.append((mm.cycle, np.array(mm.owner, np.uint8), list(mm.q[0])[:300], list(mm.q[1])[:300], len(mm.q[0]), len(mm.q[1])))
    w = m.run(cb)
    assert w == mars.pmars_round(src, OPP, str(core.PMARS), FPOS)
    return snaps, w

def fights():
    global FIGHTS
    if FIGHTS is None:
        FIGHTS = (run_fight(AI_SRC), run_fight(EX_SRC))
        assert FIGHTS[0][1] == 2 and FIGHTS[1][1] == 1
    return FIGHTS

def grid(owner, pa, pb, prog_l, prog_d, cell=CELL):
    pal = np.array([CELL_EMPTY, prog_l, BLUE_L], np.uint8)
    cells = pal[owner].copy()
    for p in pb: cells[p] = BLUE
    for p in pa: cells[p] = prog_d
    img = np.repeat(np.repeat(cells.reshape(ROWS, COLS, 3), cell, 0), cell, 1)
    msk = np.ones((cell, cell), bool); msk[cell - 2:, :] = False; msk[:, cell - 2:] = False
    img = np.where(np.tile(msk, (ROWS, COLS))[..., None], img, np.array(CELL_GAP, np.uint8))
    return Image.fromarray(img.astype(np.uint8), "RGB")

_STEPS = {}
def pick(snaps, c):
    """The last snapshot at or before step c."""
    steps = _STEPS.setdefault(id(snaps), [s_[0] for s_ in snaps])
    return snaps[max(0, bisect.bisect_right(steps, c) - 1)]

# ---------------------------------------------------------------- the test
def title(t, dur):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img, "RGBA"); k = fade(t, dur, 0.3, 0.5)
    text(d, (W / 2, 290), "DEMO", F("InterDisplay-Black.otf", 190), FG, ramp(t, 0.3, 0.7) * k, "mm")
    text(d, (W / 2, 440), "One real AI run, replayed from its own logs", F("Inter-Bold.otf", 50), ACC, ramp(t, 0.9, 0.7) * k, "mm")
    text(d, (W / 2, 520), "The question: can a top AI agent write a game program as strong as a human expert's?",
         F("Inter-SemiBold.otf", 36), FG, ramp(t, 1.6, 0.7) * k, "mm")
    text(d, (W / 2, 585), "run C5  ·  Claude Opus 5.5  ·  the challenge's official harness (Harbor + OpenCode)  ·  14 Nov 2026  ·  sped up",
         F("Inter-Medium.otf", 26), MUTED, ramp(t, 2.2, 0.7) * k, "mm")
    for i, name in enumerate(PARTS):
        a = ramp(t, 3.0 + i * 0.45, 0.5) * k
        cx = 300 + i * 440
        panel(d, (cx - 190, 720, cx + 190, 830), a, r=18)
        d.ellipse((cx - 160, 751, cx - 112, 799), fill=mix(ACC, a))
        text(d, (cx - 136, 775), str(i + 1), F("Inter-Black.otf", 26), BG, a, "mm")
        text(d, (cx - 92, 775), name, F("Inter-Bold.otf", 34), FG, a, "lm")
    return img

GAME_IMG = None
def game(kicker):
    def scene(t, dur):
        global GAME_IMG
        img, d, k = base(t, dur, set())
        head(d, t, kicker, "First, the game: Core War", k)
        if GAME_IMG is None:
            cyc, owner, pa, pb, na, nb = pick(fights()[0][0], 3021)
            GAME_IMG = grid(owner, pa, pb, RED_C, RED)
        a = ramp(t, 0.4, 0.6) * k
        img.paste(GAME_IMG, (120, 300), Image.new("L", GAME_IMG.size, int(255 * a)))
        d = ImageDraw.Draw(img, "RGBA")
        text(d, (120, 890), "a real game, mid-way: one program in red, the other in blue", F("Inter-SemiBold.otf", 24), MUTED, a)
        B, S = F("Inter-Bold.otf", 36), F("Inter-Medium.otf", 31)
        groups = [[("Two programs share one memory", B, FG), ("of 8,000 cells.", S, MUTED)],
                  [("Each runs its own code and tries", B, FG), ("to crash the other, for instance", S, MUTED), ("by writing over its code.", S, MUTED)],
                  [("A program loses when none", B, FG), ("of its code is still running.", S, MUTED)],
                  [("Both still running at the time", B, FG), ("limit: a draw.", S, MUTED)]]
        y = 320
        for gi, rows in enumerate(groups):
            for s, f, c in rows:
                text(d, (920, y), s, f, c, ramp(t, 1.0 + gi * 0.17 * dur, 0.5) * k); y += 48
            y += 30
        return img
    return scene

def test(kicker):
    def scene(t, dur):
        img, d, k = base(t, dur, {"diff", "integ"})
        head(d, t, kicker, "What the AI has to do", k)
        t1, t2 = max(3.8, 0.30 * dur), max(6.0, 0.50 * dur)
        text(d, (120, 290), "The AI writes one program. That program then takes the test:", F("Inter-SemiBold.otf", 32), FG, ramp(t, 0.5, 0.6) * k)
        a1 = ramp(t, 1.2, 0.7) * k
        panel(d, (120, 350, 520, 490), a1, fill=RED_L, outline=RED, r=18)
        text(d, (320, 420), "the AI's program", F("Inter-Bold.otf", 34), RED, a1, "mm")
        a2 = ramp(t, 1.8, 0.7) * k
        arrow(d, (540, 420), (660, 420), MUTED, a2, width=6)
        text(d, (600, 378), "plays", F("Inter-SemiBold.otf", 24), MUTED, a2, "mm")
        for i in range(30):
            r, c = divmod(i, 10)
            x, y = 690 + c * 108, 345 + r * 50
            aa = ramp(t, 2.0 + i * 0.04, 0.4) * k
            d.rounded_rectangle((x, y, x + 96, y + 42), 10, fill=mix(OPP_FILL, aa), outline=mix(OPP_LINE, aa), width=2)
            text(d, (x + 48, y + 21), "?", F("Inter-Bold.otf", 22), OPP_LINE, aa, "mm")
        text(d, (1230, 520), "30 secret opponents, 500 games against each", F("Inter-Bold.otf", 28), BLUE_T, ramp(t, 3.0) * k, "mm")
        if t > t1:
            aa = ramp(t, t1, 0.6) * k
            text(d, (120, 575), "Each game:  win = 3 points,  draw = 1,  loss = 0.", F("Inter-Bold.otf", 38), FG, aa)
            text(d, (120, 630), "So the game score = points won ÷ points possible, from 0 to 1.", F("Inter-SemiBold.otf", 32), MUTED, aa)
        if t > t2:
            aa = ramp(t, t2, 0.6) * k
            panel(d, (120, 700, 1800, 935), aa, fill=GREEN_L, outline=GREEN, r=18)
            text(d, (160, 748), "For comparison, a human expert's program takes exactly the same test.", F("Inter-Bold.otf", 34), GREEN, aa, "lm")
            text(d, (160, 805), "“Toxic”, by John Metcalf: rated #1 of 264 human-written programs (Elo, CodeClash ladder).", F("Inter-SemiBold.otf", 29), FG, aa, "lm")
            text(d, (160, 865), "Its game score: 0.487. Against opponents this strong, about 0.5 is top level.", F("Inter-SemiBold.otf", 29), FG,
                 ramp(t, t2 + max(1.4, 0.13 * dur), 0.6) * k, "lm")
        return img
    return scene

def rules(kicker):
    steps = [("1", "It writes a program", "a small text file in Redcode, the game's assembly language"),
             ("2", "It practises", "against 30 practice opponents, and gets a practice score"),
             ("3", "It submits", "as often as it wants; only the last submission counts"),
             ("4", "It decides when to stop", "every reply from its tools shows a clock with the minutes left")]
    def scene(t, dur):
        img, d, k = base(t, dur, {"diff"})
        head(d, t, kicker, "To prepare: 45 minutes and practice", k)
        step = max(1.3, 0.115 * dur); t1 = 0.8 + 3 * step + max(1.7, 0.14 * dur)
        for i, (n, h, sub) in enumerate(steps):
            a = ramp(t, 0.8 + i * step, 0.7) * k
            y = 280 + i * 136
            panel(d, (120, y, 1800, y + 118), a, r=18)
            d.ellipse((150, y + 29, 210, y + 89), fill=mix(FG, a))
            text(d, (180, y + 59), n, F("Inter-Black.otf", 30), BG, a, "mm")
            text(d, (240, y + 40), h, F("Inter-Bold.otf", 38), FG, a, "lm")
            text(d, (240, y + 88), sub, F("Inter-Medium.otf", 30), MUTED, a, "lm")
        if t > t1:
            aa = ramp(t, t1, 0.7) * k
            panel(d, (120, 832, 1800, 950), aa, fill=RED_L, outline=RED, r=18)
            text(d, (W / 2, 870), "But the practice opponents are not the secret ones.", F("Inter-Bold.otf", 36), RED, aa, "mm")
            text(d, (W / 2, 920), "Only at the end does a referee program run the real test. The AI never sees that score.",
                 F("Inter-SemiBold.otf", 28), FG, ramp(t, t1 + max(1.0, 0.09 * dur), 0.6) * k, "mm")
        return img
    return scene

# ---------------------------------------------------------------- the run
def term(kicker, last):
    def scene(t, dur):
        img, d, k = base(t, dur, {"craft"})
        head(d, t, kicker, "Five runs of the same AI, one command", k)
        a = ramp(t, 0.3) * k
        x, y = terminal(d, (120, 280, 1800, 470), a, "zsh — harbor")
        n = int(clamp((t - 0.6) / 1.4) * (len(CMD) - 2))
        term_line(d, (x, y), CMD, a, 25, typed=n, cursor=t < 2.3)
        prog = clamp((t - 2.3) / 4.2)
        if t > 2.3:
            secs = int(round(prog * (42 * 60 + 47)))
            f = M(25); bar = 48; done = int(prog * bar)
            line = f"{min(5, int(prog * 5.2))}/5 runs  "
            term_line(d, (x, y + 52), line, a, 25)
            bx = x + d.textlength(line, font=f)
            text(d, (bx, y + 52), "━" * done, f, TERM_GREEN, a, "lm")
            text(d, (bx + d.textlength("━" * done, font=f), y + 52), "━" * (bar - done), f, (60, 66, 76), a, "lm")
            text(d, (bx + d.textlength("━" * bar, font=f) + 24, y + 52), f"{secs // 3600}:{secs // 60 % 60:02d}:{secs % 60:02d}", f, TERM_DIM, a, "lm")
            text(d, (120, 525), "5 runs, up to 4 at a time, each alone in its own sealed box, each with 45 minutes.", F("Inter-Medium.otf", 30), MUTED, a)
            text(d, (120, 575), "Real time for all five: 42 min 47.", F("Inter-Medium.otf", 30), MUTED, a)
        if t > 6.6:
            text(d, (W / 2, 760), last, F("InterDisplay-Bold.otf", 46), FG, ramp(t, 6.6, 0.6) * k, "mm")
        return img
    return scene

# (minute, what it did, why / what it means, a real line from its log)
FEED = [(0.0, "Reads the rules and the strategy notes", "Everything it needs is provided.", "$ ls /app/doc; head -50 /app/doc/strategy_primer.md"),
        (0.2, "Writes its first program: a stone", "A stone drops bombs (code that crashes whoever runs it) over memory.", ";name Pebble Clear   (its own file, stone.red)"),
        (1.1, "Tries six different bombing distances", "The distance between bombs decides where they land.", "$ for st in 3315 2365 3044 5363 1871 3359; do ..."),
        (2.2, "Submits the stone", "Practice score 0.311. An early submission counts even if time runs out.", "$ python3 /app/tools/spar.py --submit st2791.red"),
        (3.0, "Switches style: a scanner it calls “Glance”", "A scanner looks for the enemy, then attacks it.", ";name Glance   (sc14.red)"),
        (3.2, "Submits Glance", "Practice score jumps to 0.411.", "$ python3 /app/tools/spar.py --submit sc14.red"),
        (5.1, "Tunes the scan: dozens of variants", "Each test is real games against the 30 practice opponents.", '$ for p in "20 10" "24 12" "16 8" "28 14" "32 16"; do ...'),
        (6.0, "Submits the best version", "Practice score 0.472.", "$ python3 /app/tools/spar.py --submit best.red"),
        (7.7, "Tries switching styles from game to game", "It scores lower, so the AI drops the idea.", ";name Glance PS   (remembers past games to pick a style)"),
        (10.7, "Submits a new version", "Practice score 0.485.", "$ python3 /app/tools/spar.py --submit na.red"),
        (12.5, "Moves where the scan starts, submits again", "Practice score 0.489: almost the expert's 0.507.", "$ python3 /app/tools/spar.py --submit b2.red"),
        (13.0, "Keeps trying small changes", "None of them beats 0.489 in practice.", "$ ... spar.py x.red --rounds 300 | tail -1"),
        (16.1, "Checks its submission", "", "$ python3 /app/tools/spar.py --status"),
        (16.4, "Stops and writes its report", "“It scores 0.489 on the sparring set” (its practice opponents).", "")]
SUBS = [(2.2, 0.311), (3.2, 0.411), (6.0, 0.472), (10.7, 0.485), (12.5, 0.489)]

# The words the run's scenes use for the two programs; the full demo renames them (Claude Opus, Toxic).
# COMPACT: the replay shows only the last three events, one line each.
LABELS = {"ai": "the AI (run C5)", "expert": "the expert", "practice": "In practice", "practice_sub": "what the AI saw",
          "real": "In the real test", "real_sub": "hidden from the AI until the end", "ai_prog": "the AI's program",
          "expert_prog": "the expert's program", "ai_panel": "the AI's program (red)", "expert_panel": "the expert's program (green)",
          "chart_expert": "the expert: 0.507", "stats_note": "Scored by pMARS, the game's official simulator.", "compact": False}

def feed_minute(p, m0, m1):
    """The run's minute at progress p (0..1) through a replay scene: the clock moves so that every
    log entry between m0 and m1 stays on screen equally long before the next one arrives."""
    knots = sorted({m0, m1} | {f[0] for f in FEED if m0 <= f[0] <= m1})
    x = clamp(p) * (len(knots) - 1); i = min(int(x), len(knots) - 2)
    return knots[i] + (knots[i + 1] - knots[i]) * (x - i)

def practice_chart(d, a, m, box, caption=True, end=17.0):
    """The practice score of each submission up to minute m, drawn in `box`."""
    cx0, cy0, cx1, cy1 = box
    lo, hi = 0.28, 0.53
    X = lambda mm: cx0 + 40 + (cx1 - cx0 - 40) * mm / end
    Y = lambda v: cy1 - (cy1 - cy0) * (v - lo) / (hi - lo)
    for v in (0.3, 0.4, 0.5):
        d.line((cx0 + 40, Y(v), cx1, Y(v)), fill=mix(LINE, a), width=2)
        text(d, (cx0 + 30, Y(v)), f"{v:.1f}", F("Inter-Medium.otf", 20), MUTED, a, "rm")
    for mm in (0, 5, 10, 15):
        text(d, (X(mm), cy1 + 20), f"{mm} min" if mm == 15 else str(mm), F("Inter-Medium.otf", 20), MUTED, a, "mm")
    for xx in range(int(cx0 + 40), int(cx1) - 8, 18):
        d.line((xx, Y(0.507), xx + 9, Y(0.507)), fill=mix(GREEN, a * 0.8), width=3)
    text(d, (cx1, Y(0.507) - 8), LABELS["chart_expert"], F("Inter-SemiBold.otf", 22), GREEN, a, "rs")
    xy = [(X(s[0]), Y(s[1])) for s in SUBS if s[0] <= m]
    if len(xy) > 1: d.line(xy, fill=mix(RED, a), width=5)
    for q in xy: d.ellipse((q[0] - 8, q[1] - 8, q[0] + 8, q[1] + 8), fill=mix(RED, a))
    if caption:
        text(d, (cx0, cy1 + 58), LABELS.get("chart_caption", "red: the AI's submissions"), F("Inter-Bold.otf", 22), RED, a, "lm")

def replay_frame(t, dur, m0, m1, kicker, title_, hold=3.5):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, kicker, title_, k)
    lead = 0.8
    m = feed_minute((t - lead) / max(0.1, dur - lead - hold), m0, m1)
    a = ramp(t, 0.3) * k
    items = [f for f in FEED if m0 - 1e-6 <= f[0] <= m]
    if not items: items = [f for f in FEED if f[0] <= m][-1:]
    y = 290
    compact = LABELS["compact"]
    for mm, act, why, log in items[-LABELS.get("rows", 3):] if compact else items[-5:]:
        cur = (mm, act, why, log) == items[-1]
        text(d, (120, y), f"min {mm:4.1f}", M(26, True), ACC if cur else MUTED, a)
        text(d, (300, y - 2), act, F("Inter-Bold.otf" if cur else "Inter-SemiBold.otf", 34 if compact else 32), FG if cur else MUTED, a)
        if why and not compact:
            text(d, (300, y + 40), why, F("Inter-Medium.otf", 27), ACC if cur else MUTED, a)
        y += 80 if compact else (100 if why else 64)
    cur = items[-1]
    if cur[3] and LABELS.get("log_strip", True):
        x, y = terminal(d, (120, 832, 1180, 945), a, "run C5 — from its log")
        term_line(d, (x, y + 4), cur[3][:70], a, 23)
    panel(d, (1260, 280, 1800, 390), a, r=18)
    text(d, (1290, 312), LABELS.get("clock", "the AI's clock"), F("Inter-SemiBold.otf", 24), MUTED, a, "lm")
    text(d, (1290, 358), f"minute {m:4.1f} of 45", F("InterDisplay-Black.otf", 44), FG, a, "lm")
    panel(d, (1260, 415, 1800, 945), a, r=18)
    text(d, (1290, 447), "practice score of each submission", F("Inter-Bold.otf", 24), FG, a, "lm")
    practice_chart(d, a, m, (1290, 500, 1770, 838))
    return img, d, k, m

def replay(kicker, title_, m0, m1):
    return lambda t, dur: replay_frame(t, dur, m0, m1, kicker, title_)[0]

END_TXT = ("It stops at minute 16.5, with 28.5 of its 45 minutes left.", "In practice, it is almost as good as the expert.",
           "But practice is not the test. Now the referee runs the real test.")

def replay_end(kicker, words=END_TXT):
    def scene(t, dur):
        hold = 7.0
        img, d, k, m = replay_frame(t, dur, 12.5, 16.5, kicker, "Finally, it stops", hold=hold)
        t_box = dur - hold + 0.3
        if t > t_box:
            aa = ramp(t, t_box, 0.6) * k
            d.rounded_rectangle((120, 680, 1180, 790), 16, fill=mix(RED_L, aa), outline=mix(RED, aa), width=3)
            text(d, (150, 718), words[0], F("Inter-Bold.otf", 31), RED, aa, "lm")
            text(d, (150, 765), words[1], F("Inter-Medium.otf", 28), FG, aa, "lm")
        if t > t_box + 2.4:
            text(d, (120, 880), words[2], F("Inter-Bold.otf", 30), FG,
                 ramp(t, t_box + 2.4, 0.6) * k, "lm")
        return img
    return scene

# ---------------------------------------------------------------- the result
REVEAL_TXT = ("The AI's last submission plays the 30 secret opponents, 500 games each.",
              "In practice, the AI was almost as good as the expert: 0.018 behind.", "In the real test, it is clearly behind: 0.089.")

def reveal(kicker, words=REVEAL_TXT):
    def scene(t, dur):
        img, d, k = base(t, dur, {"gap"})
        head(d, t, kicker, LABELS.get("reveal_title", "Then the referee runs the real test"), k)
        text(d, (120, 290), words[0], F("Inter-SemiBold.otf", 32), FG, ramp(t, 0.5, 0.6) * k)
        a0 = ramp(t, 1.2, 0.6) * k
        c1, c2 = 1150, 1560
        text(d, (c1, 385), LABELS["ai"], F("Inter-Bold.otf", 34), RED, a0, "mm")
        text(d, (c2, 385), LABELS["expert"], F("Inter-Bold.otf", 34), GREEN, a0, "mm")
        rows = ((LABELS["practice"], LABELS["practice_sub"], "0.489", "0.507"),
                (LABELS["real"], LABELS["real_sub"], "0.398", "0.487"))
        for i, (h, sub, va, ve) in enumerate(rows):
            aa = ramp(t, 1.8 + i * 1.8, 0.6) * k
            y = 425 + i * 160
            panel(d, (120, y, 1800, y + 138), aa, r=18)
            text(d, (160, y + 50), h, F("Inter-Bold.otf", 40), FG, aa, "lm")
            text(d, (160, y + 100), sub, F("Inter-Medium.otf", 28), MUTED, aa, "lm")
            text(d, (c1, y + 69), va, F("InterDisplay-Black.otf", 56), RED, aa, "mm")
            text(d, (c2, y + 69), ve, F("InterDisplay-Black.otf", 56), GREEN, aa, "mm")
        text(d, (W / 2, 820), words[1], F("Inter-Bold.otf", 34), FG,
             ramp(t, 5.4, 0.6) * k, "mm")
        text(d, (W / 2, 880), words[2], F("Inter-Bold.otf", 34), RED, ramp(t, 7.2, 0.6) * k, "mm")
        return img
    return scene

SCALE_TXT = ("↓  the official reward rescales it: Dwarf, the textbook beginner's program = 0, the expert = 1  ↓",
             "Reward 0.74: three quarters of the way from beginner to expert, and a quarter short.")

def scale(kicker, words=SCALE_TXT):
    def scene(t, dur):
        img, d, k = base(t, dur, {"gap"})
        head(d, t, kicker, "How far behind, exactly?", k)
        x0, x1 = 240, 1680
        def axis(y, lo, hi, label, ticks, t0):
            a = ramp(t, t0, 0.6) * k
            text(d, (120, y - 76), label, F("Inter-Bold.otf", 30), FG, a)
            d.line((x0, y, x1, y), fill=mix(MUTED, a), width=4)
            for n, (v, lab, c, up) in enumerate(ticks):
                X = x0 + (x1 - x0) * (v - lo) / (hi - lo)
                aa = ramp(t, t0 + 0.4 + 0.6 * n, 0.5) * k
                d.ellipse((X - 12, y - 12, X + 12, y + 12), fill=mix(c, aa))
                text(d, (X, y + (30 if not up else -26)), lab, F("Inter-Bold.otf", 28), c, aa, "mt" if not up else "mb")
        axis(420, 0.10, 0.55, "Game score in the real test",
             [(0.1475, "beginner (Dwarf) 0.148", MUTED, False), (0.487, "the expert 0.487", GREEN, False),
              (0.398, "the AI (run C5) 0.398", RED, True)], 0.5)
        if t > 3.6:
            text(d, (W / 2, 560), words[0],
                 F("Inter-SemiBold.otf", 29), MUTED, ramp(t, 3.6, 0.6) * k, "mm")
        if t > 4.8:
            axis(720, -0.12, 1.12, "Reward",
                 [(0.0, "0  beginner", MUTED, False), (1.0, "1  the expert", GREEN, False), (0.740, "the AI 0.740", RED, True)], 4.8)
        if t > 8.0:
            aa = ramp(t, 8.0, 0.6) * k
            text(d, (W / 2, 812), words[1],
                 F("Inter-Bold.otf", 32), FG, aa, "mm")
            x, y = terminal(d, (620, 846, 1300, 966), aa, "verifier")
            term_line(d, (x, y), "$ cat /logs/verifier/reward.txt", aa, 22)
            term_line(d, (x, y + 36), "0.739615", aa, 22)
        return img
    return scene

# ---------------------------------------------------------------- why the gap: one real game
INTRO, SLOW, FAST, OUT = 9.0, 8.0, 10.0, 4.0
WIN_E = 41

def step_at(t, last):
    if t < INTRO: return 0
    if t < INTRO + SLOW: return 60 * (t - INTRO) / SLOW
    return 60 + (last - 60) * clamp((t - INTRO - SLOW) / FAST)

FIGHT_TXT = dict(
    title="Why the gap? One game of the real test",
    card=[("One game against Blizzard: the secret opponent where the gap is largest.", 0.8), ("Left: the AI's program (red). Right: the expert's (green).", 2.3),
          ("Same opponent (blue), same starting positions.", 3.8, MUTED), ("Dark squares: code running. Light squares: memory it has written.", 5.3),
          ("A program loses when none of its code is still running.", 6.8)],
    caps=["The expert starts with a quick search: it checks spots across memory to find the opponent.",
          "Found and bombed: the expert wins at step 41. The AI's program is still searching.",
          "The AI writes bombs all over memory (red), but Blizzard's code keeps running (blue counter).",
          "Then the AI's running processes drop to zero: it loses at step 9,060."],
    box=(380, 1540))

def fight(kicker, words=FIGHT_TXT):
    def scene(t, dur):
        img, d, k = base(t, dur, {"diff"})
        head(d, t, kicker, words["title"], k)
        (sa, wa), (sb, wb) = fights()
        last = sa[-1][0]
        c = step_at(t, last)
        a = ramp(t, 0.3) * k
        gy, gw, gh = 318, COLS * CELL, ROWS * CELL
        panels = [(170, sa, RED_C, RED, LABELS["ai_panel"], "Glance", False),
                  (1050, sb, GREEN_C, GREEN, LABELS["expert_panel"], "Toxic", True)]
        for x, snaps, light, dark, label, nm, win in panels:
            cyc, owner, pa, pb, na, nb = pick(snaps, c)
            g = grid(owner, pa, pb, light, dark)
            img.paste(g, (x, gy), Image.new("L", g.size, int(255 * a)))
            d = ImageDraw.Draw(img, "RGBA")
            text(d, (x, 306), label + "  vs  Blizzard (blue)", F("Inter-Bold.otf", 24), dark, a, "ls")
            if LABELS.get("counters", True): text(d, (x, gy + gh + 22), f"{nm}: {na:,} process{'es' if na != 1 else ''} running  ·  Blizzard: {nb:,}", F("Inter-Bold.otf", 23), FG,
                 a * clamp((t - INTRO + 0.5) / 0.5), "lm")                          # the counters arrive with the action
            end = snaps[-1][0]
            if win and t >= INTRO and c >= 9:
                aa = ramp(t, INTRO + SLOW * 9 / 60, 0.4) * k
                y0 = gy + 72 * CELL
                d.rounded_rectangle((x - 5, y0 - 5, x + gw + 5, y0 + 2 * CELL + 5), 8, outline=mix(GREEN, aa), width=4)
                d.rounded_rectangle((x + 90, y0 - 56, x + 610, y0 - 12), 10, fill=mix(CARD, aa), outline=mix(GREEN, aa), width=2)
                text(d, (x + 350, y0 - 34), "its bombs land on Blizzard's code", F("Inter-Bold.otf", 25), GREEN, aa, "mm")
            if t >= INTRO and c >= end:
                t_end = INTRO + (SLOW * end / 60 if end <= 60 else SLOW + FAST * (end - 60) / (last - 60))
                aa = ramp(t, t_end, 0.4) * k
                msg = f"wins at step {end:,}" if win else f"loses at step {end:,}"
                d.rounded_rectangle((x + 110, 500, x + 590, 590), 20, fill=mix(CARD, aa), outline=mix(dark, aa), width=4)
                text(d, (x + 350, 545), msg, F("InterDisplay-Black.otf", 38), dark, aa, "mm")
        ff = " · fast-forward" if 60 < c < last else ""
        text(d, (1750, 266), f"step {int(min(c, last)):,}{ff}", F("Inter-Bold.otf", 26), FG, a, "rm")
        text(d, (170, 266), LABELS.get("legend", "dark = code running   ·   light = memory it has written   ·   a program loses when none of its code runs"),
             F("Inter-SemiBold.otf", 21), MUTED, a * clamp((t - INTRO + 0.5) / 0.5), "lm")
        if t < INTRO:
            aa = ramp(t, 0.6, 0.6) * k * clamp((INTRO - t) / 0.4)
            bx0, bx1 = words["box"]; rows = words["card"]
            by1 = 460 + len(rows) * 62 + 24
            d.rounded_rectangle((bx0, 330, bx1, by1), 24, fill=mix(CARD, aa * 0.97), outline=mix(LINE, aa), width=3)
            text(d, (960, 385), "How to read this", F("Inter-Black.otf", 40), FG, aa, "mm")
            for jj, (s_, t_on, *cc) in enumerate(rows):
                text(d, (bx0 + 50, 460 + jj * 62), s_, F("Inter-SemiBold.otf", 30), (cc or [FG])[0], ramp(t, t_on, 0.5) * aa, "lm")
        elif t < INTRO + SLOW:
            if c < WIN_E:
                cap, t0 = words["caps"][0], INTRO + 0.3
            else:
                cap, t0 = words["caps"][1], INTRO + SLOW * WIN_E / 60
            text(d, (W / 2, 946), cap, F("Inter-Bold.otf", 28), GREEN, ramp(t, t0, 0.4) * k, "mm")
        else:
            if c < 8300:
                cap, t0 = words["caps"][2], INTRO + SLOW + 0.4
            else:
                cap, t0 = words["caps"][3], INTRO + SLOW + FAST * (8300 - 60) / (last - 60)
            text(d, (W / 2, 946), cap, F("Inter-Bold.otf", 28), RED, ramp(t, t0, 0.4) * k, "mm")
        return img
    return scene

STATS_TXT = "Blizzard is the opponent where the gap is largest. Over all 30, the expert does better against 22."

def stats(kicker, words=STATS_TXT):
    def scene(t, dur):
        groups = [(LABELS["ai_prog"], [(0, "wins"), (147, "draws"), (353, "losses")], RED),
                  (LABELS["expert_prog"], [(119, "wins"), (365, "draws"), (16, "losses")], GREEN)]
        img, d, k = base(t, dur, {"diff"})
        head(d, t, kicker, "Not luck: 500 games, same opponent", k)
        g = ramp(t, 0.9, 1.0)
        for gi, (lab, vals, col) in enumerate(groups):
            a = ramp(t, 0.5, 0.6) * k
            y = 290 + gi * 270
            text(d, (120, y), lab, F("Inter-Bold.otf", 38), col, a)
            x = 120; small = []
            for v, name in vals:
                w = 1680 * v / 500 * g
                c = col if name == "wins" else (DIM if name == "draws" else LOSS)
                if w > 2: d.rounded_rectangle((x, y + 62, x + w, y + 138), 10, fill=mix(c, a))
                if v > 40: text(d, (x + w / 2, y + 100), f"{v} {name}", F("Inter-Bold.otf", 28), FG if name == "draws" else BG, a * clamp((g - 0.85) / 0.15), "mm")
                else: small.append(f"{v} {name}")
                x += w
            if small:
                text(d, (120, y + 175), "  ·  ".join(small), F("Inter-Bold.otf", 28), MUTED, a * clamp((g - 0.85) / 0.15), "lm")
        if t > 3.4:
            aa = ramp(t, 3.4, 0.6) * k
            text(d, (W / 2, 860), words,
                 F("Inter-SemiBold.otf", 30), FG, aa, "mm")
            text(d, (W / 2, 915), LABELS["stats_note"], F("Inter-Medium.otf", 27), MUTED, ramp(t, 5.0, 0.6) * k, "mm")
        return img
    return scene

# ---------------------------------------------------------------- the short demo's conclusion
RUNS = [("run C1", 0.665968), ("run C2", 0.740794), ("run C3", 0.691915), ("run C4", 0.727166), ("run C5", 0.739615)]

def end(t, dur):
    img, d, k = base(t, dur, {"gap", "diff"})
    head(d, t, "CONCLUSION", "Not just this run: all five fall short", k)
    bx0, bx1 = 330, 1560
    g = ramp(t, 0.7, 0.9)
    for i, (lab, r) in enumerate(RUNS):
        a = ramp(t, 0.5, 0.5) * k
        y = 290 + i * 62; hl = lab == "run C5"
        text(d, (120, y + 22), lab, F("Inter-Bold.otf" if hl else "Inter-SemiBold.otf", 30), FG if hl else MUTED, a, "lm")
        d.rounded_rectangle((bx0, y, bx1, y + 44), 10, fill=mix(TRACK, a))
        w = (bx1 - bx0) * r * g
        if w > 2: d.rounded_rectangle((bx0, y, bx0 + w, y + 44), 10, fill=mix(RED if hl else RUN_BAR, a))
        text(d, (bx0 + w + 16, y + 22), f"{r:.3f}", F("Inter-Bold.otf", 28), RED, a * clamp((g - 0.85) / 0.15), "lm")
    ae = ramp(t, 1.8, 0.5) * k
    for yy in range(280, 590, 16):
        d.line((bx1, yy, bx1, yy + 8), fill=mix(GREEN, ae), width=4)
    text(d, (bx1 + 16, 312), "expert = 1", F("Inter-Bold.otf", 30), GREEN, ae, "lm")
    rows = [("Mean reward 0.713. None of the five reaches the expert.", F("Inter-Bold.otf", 38), FG),
            ("All five stopped with 12 to 29 of their 45 minutes unused.", F("Inter-SemiBold.otf", 32), FG),
            ("None opens with a quick search, the expert's first move.", F("Inter-SemiBold.otf", 32), FG)]
    for i, (s, f, c) in enumerate(rows):
        text(d, (W / 2, 650 + i * 56), s, f, c, ramp(t, 2.8 + i * 1.5, 0.6) * k, "mm")
    if t > 7.6:
        aa = ramp(t, 7.6, 0.6) * k
        panel(d, (220, 818, 1700, 892), aa, fill=ACC_L, outline=ACC, r=16)
        text(d, (W / 2, 855), "The AI writes working programs fast, but stops short of expert-level design.",
             F("Inter-Bold.otf", 34), ACC, aa, "mm")
        text(d, (W / 2, 935), "Every number in this demo comes from the runs' own log files.", F("Inter-Medium.otf", 26), MUTED, aa, "mm")
    return img

RUN = "  ·  RUN C5"
SCENES = [("w01_title", title, 7.5),
          ("w02_game", game(part(1)), 11.0), ("w03_test", test(part(1)), 15.0), ("w04_rules", rules(part(1)), 16.0),
          ("w05_term", term(part(2), "We follow run C5: the one that came closest to the expert in practice."), 10.0),
          ("w06_rep1", replay(part(2, "MINUTES 0 TO 3"), "First, two quick tries", 0.0, 3.2), 19.0),
          ("w07_rep2", replay(part(2, "MINUTES 3 TO 12"), "Then, it polishes one idea", 3.2, 12.5), 18.0),
          ("w08_rep3", replay_end(part(2, "MINUTES 12 TO 16")), 17.0),
          ("w09_reveal", reveal(part(3)), 13.0), ("w10_scale", scale(part(3)), 13.5),
          ("w11_fight", fight(part(4)), INTRO + SLOW + FAST + OUT), ("w12_stats", stats(part(4)), 10.0),
          ("w13_end", end, 13.5)]

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn, dur in SCENES:
        if what in ("all", name):
            render(name, fn, dur); print("rendered", name, flush=True)
