#!/usr/bin/env python3
"""The 1 min 59 pitch, cut as a promo, built on one question and its answer.
Q: "Can a frontier AI agent turn practice into a design that wins against opponents it has never seen?"
A: "Not yet. They can't find a winning design, escape the traps of practice, or both."
The question -> the game -> the test (30 practice opponents, 30 it has never seen) -> the scale,
copies and fakes score 0 -> 0.71 / 0.84 -> the answer, under the question, with a table (GPT-6.1 sol:
no winning design, no traps; Claude Opus 5.5: both) -> why not, 1, the design: the chart of every run
(over 90% of both agents' gap to Toxic is already there in practice), and GPT-6.1 sol's programs
attack well but don't survive -> why not, 2, the traps of practice: Claude Opus falls into all three,
GPT-6.1 sol into none -> what it measures -> the question again, "Not yet", and the thesis.
One idea per screen, few words, long holds, calm fades. Colours: white and grey text, red for
Claude Opus, amber for GPT-6.1 sol, green for the #1 human program. Every figure comes from
results/models.json (exploits/compare_models.py), the run logs, or the README.
usage: python video/promo.py [all | <scene name>]   -> video/build/<scene>.mp4"""
import os
os.environ["VIDEO_THEME"] = "dark"           # before style.py is imported
import sys
from PIL import Image, ImageDraw
from style import (W, H, F, BG, FG, MUTED, RED, GREEN, PANEL, LINE, ease, clamp, mix, text, render, core_bg,
                   term_line, terminal, arrow, OPP_FILL, OPP_LINE)
import figures as N
import chart

BLK, BOLD, MED = "InterDisplay-Black.otf", "Inter-Bold.otf", "Inter-Medium.otf"
PAD = 30
GREY = (150, 158, 170)
AMBER = (245, 166, 35)          # GPT-6.1 sol

# ---------------------------------------------------------------- calm type
_L = {}
def layer(s, font, size, color):
    key = (s, font, size, color)
    if key not in _L:
        f = F(font, size); l, t, r, b = f.getbbox(s)
        im = Image.new("RGBA", (r - l + 2 * PAD, b - t + 2 * PAD), (0, 0, 0, 0))
        ImageDraw.ImageDraw(im).text((PAD - l, PAD - t), s, font=f, fill=color + (255,))
        _L[key] = im
    return _L[key]


def show(img, s, font, size, color, x, y, t, t0, t1=None, anchor="m"):
    """Text that rises gently into place over 0.6 s and fades out over 0.5 s before t1."""
    if t < t0 or (t1 is not None and t > t1): return
    e = ease((t - t0) / 0.6)
    a = e * (clamp((t1 - t) / 0.5) if t1 is not None else 1.0)
    if a <= 0.004: return
    lay = layer(s, font, size, color)
    if a < 0.996:
        lay = lay.copy(); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    w, h = lay.size
    ox = {"l": PAD, "m": w / 2, "r": w - PAD}[anchor]
    img.paste(lay, (round(x - ox), round(y - h / 2 + 24 * (1 - e))), lay)


def alpha(t, t0, t1=None, d=0.6):
    return ease((t - t0) / d) * (clamp((t1 - t) / 0.5) if t1 is not None else 1.0)


_V = None
def vignette():
    global _V
    if _V is None:
        import numpy as np
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _V = Image.new("RGBA", (W, H), (0, 0, 0, 0)); _V.putalpha(Image.fromarray((np.clip(r - 0.55, 0, 1) * 200).astype("uint8")))
    return _V


def bg(t, core=0.0):
    img = core_bg(t, core) if core > 0 else Image.new("RGB", (W, H), BG)
    img.paste((0, 0, 0), (0, 0), vignette())
    return img


def fade_io(img, t, dur, fin=0.6, fout=0.6):
    k = clamp(min(t / fin, (dur - t) / fout))
    return img if k >= 1 else Image.blend(Image.new("RGB", img.size, (0, 0, 0)), img, k)


def num(d, s, size, color, x, y, a, anchor="mm"):
    text(d, (x, y), s, F(BLK, size), color, a, anchor)


def check(d, x, y, a, r=24):
    d.ellipse((x - r, y - r, x + r, y + r), outline=mix(FG, a), width=4)
    d.line((x - r * 0.45, y + r * 0.02, x - r * 0.1, y + r * 0.38, x + r * 0.5, y - r * 0.35), fill=mix(FG, a), width=5, joint="curve")

HL = (88, 166, 255)                          # the key words of the question
GPT_NAME = "GPT-6.1 sol"


def cross(d, x, y, a, r=24, col=RED):
    d.ellipse((x - r, y - r, x + r, y + r), outline=mix(col, a), width=4)
    k = r * 0.42
    d.line((x - k, y - k, x + k, y + k), fill=mix(col, a), width=5)
    d.line((x - k, y + k, x + k, y - k), fill=mix(col, a), width=5)


def check_c(d, x, y, a, r=24, col=FG):
    d.ellipse((x - r, y - r, x + r, y + r), outline=mix(col, a), width=4)
    d.line((x - r * 0.45, y + r * 0.02, x - r * 0.1, y + r * 0.38, x + r * 0.5, y - r * 0.35), fill=mix(col, a), width=5, joint="curve")


def row(img, d, t, t0, y, mark, title, sub, col, x=200):
    a = alpha(t, t0)
    (cross if mark == "x" else check_c)(d, x, y, a, 26, col)
    show(img, title, BOLD, 54, FG, x + 60, y - 6, t, t0, None, "l")
    show(img, sub, MED, 34, GREY, x + 60, y + 52, t, t0 + 0.4, None, "l")


def mline(d, y, parts, size, a):
    f = F(BLK, size)
    w = sum(d.textlength(p, font=f) for p in parts)
    x = W / 2 - w / 2
    for i, p in enumerate(parts):
        text(d, (x, y), p, f, HL if i % 2 else FG, a, "lm")
        x += d.textlength(p, font=f)


def tiles(d, y, a, mark, fill, line, tcol, n=10, cw=72, gap=14):
    x0 = W / 2 - (n * cw + (n - 1) * gap) / 2
    for i in range(n):
        x = x0 + i * (cw + gap)
        d.rounded_rectangle((x, y, x + cw, y + 56), 12, fill=mix(fill, a), outline=mix(line, a), width=2)
        text(d, (x + cw / 2, y + 28), mark, F(BOLD, 28), tcol, a, "mm")

# ---------------------------------------------------------------- 1. the question (0 - 12.6 s)
Q1 = ("Can a frontier AI agent turn ", "practice", "")
Q2 = ("into a ", "design", " that wins against opponents")
Q3 = ("it has ", "never seen", "?")

def p01(t, dur):
    img = bg(t * 0.4, 0.12); d = ImageDraw.Draw(img, "RGBA")
    show(img, "Coding agents practise on the tests they can see.", BLK, 70, FG, W / 2, 430, t, 0.3, 6.0)
    if t < 3.6: tiles(d, 560, alpha(t, 0.6, 3.4), "✓", (16, 44, 27), GREEN, GREEN)
    show(img, "Then their code meets cases no one has seen.", BLK, 70, FG, W / 2, 740, t, 3.1, 6.0)
    if 3.2 < t < 6.0:
        tiles(d, 560, alpha(t, 3.4, 6.0), "?", OPP_FILL, OPP_LINE, OPP_LINE)
    if t > 5.9:
        a = alpha(t, 6.0)
        mline(d, 420, Q1, 80, a)
        mline(d, 525, Q2, 80, a)
        mline(d, 630, Q3, 80, a)
    return fade_io(img, t, dur, 0.6, 0.5)

# ---------------------------------------------------------------- 2. the game (12.6 - 19.9 s)
def p02(t, dur):
    if t < 2.4:
        img = bg(t * 0.8, 0.45); d = ImageDraw.Draw(img, "RGBA")
        d.rectangle((0, 400, W, 680), fill=BG + (int(225 * clamp(t / 0.5) * clamp((2.4 - t) / 0.4)),))
        show(img, "CORE WAR ARENA", BLK, 160, FG, W / 2, 540, t, 0.2, 2.4)
        return fade_io(img, t, dur, 0.5, 0.5)
    img = bg(t); d = ImageDraw.Draw(img, "RGBA")
    pa = alpha(t, 2.5)
    core = core_bg(t * 0.55, 1.0).resize((740, 480), Image.BILINEAR)
    img.paste(core, (1060, 300), Image.new("L", core.size, int(255 * pa)))
    d.rounded_rectangle((1056, 296, 1804, 784), 14, outline=mix(LINE, pa), width=3)
    show(img, "A game from 1984.", BOLD, 48, GREY, 140, 340, t, 2.5, None, "l")
    show(img, "Two programs.", BLK, 76, FG, 140, 450, t, 2.9, None, "l")
    show(img, "One memory.", BLK, 76, FG, 140, 545, t, 3.3, None, "l")
    show(img, "Last one running wins.", BLK, 70, HL, 140, 680, t, 4.4, None, "l")
    return fade_io(img, t, dur, 0.5, 0.5)

# ---------------------------------------------------------------- 3. the test (19.9 - 26.1 s)
def p03(t, dur):
    img = bg(t); d = ImageDraw.Draw(img, "RGBA")
    a1, a2 = alpha(t, 0.3), alpha(t, 3.0)
    for (x0, x1), a, title, sub, mark_, fill, line, tcol, t0 in (
            ((140, 920), a1, "30 practice opponents", "45 minutes · as often as it likes", "▶", PANEL, LINE, GREY, 0.5),
            ((1000, 1780), a2, "30 it has never seen", "the hidden test · 500 games each", "?", OPP_FILL, OPP_LINE, OPP_LINE, 3.2)):
        d.rounded_rectangle((x0, 240, x1, 820), 24, fill=mix(PANEL, a), outline=mix(line, a), width=3)
        text(d, ((x0 + x1) / 2, 320), title, F(BLK, 52), FG if mark_ == "▶" else (140, 180, 255), a, "mm")
        text(d, ((x0 + x1) / 2, 390), sub, F(BOLD, 36), GREY, a, "mm")
        for i in range(30):
            r_, c_ = divmod(i, 6)
            cx = (x0 + x1) / 2 - 3 * 100 + c_ * 100 + 10
            y = 450 + r_ * 70
            aa = a * clamp((t - t0 - i * 0.02) / 0.3)
            d.rounded_rectangle((cx, y, cx + 80, y + 54), 10, fill=mix(fill, aa), outline=mix(line, aa), width=2)
            text(d, (cx + 40, y + 27), mark_, F(BOLD, 24), tcol, aa, "mm")
    arrow(d, (930, 530), (990, 530), GREY, a2, width=6, head=20)
    return fade_io(img, t, dur, 0.5, 0.5)

# ---------------------------------------------------------------- 4. the scale, and copies (26.1 - 33.3 s)
def p04(t, dur):
    img = bg(t); d = ImageDraw.Draw(img, "RGBA")
    a = alpha(t, 0.3)
    x0, x1, y = 440, 1480, 400
    d.line((x0, y, x1, y), fill=mix(GREY, a), width=6)
    for v, lab, sub, col in ((0, "0", "Dwarf, a beginner's program", GREY), (1, "1", "Toxic, the #1 human program", GREEN)):
        X = x0 + (x1 - x0) * v
        d.ellipse((X - 18, y - 18, X + 18, y + 18), fill=mix(col, a))
        num(d, lab, 90, col, X, y - 80, a)
        text(d, (X, y + 60), sub, F(BOLD, 38), col, a, "mm")
    for i, (s_, t0) in enumerate((("Copy a published program  →  0", 4.2), ("Fake the score file  →  0", 4.7))):
        yy = 680 + i * 110
        cross(d, 560, yy, alpha(t, t0), 26, RED)
        show(img, s_, BOLD, 56, FG, 620, yy, t, t0, None, "l")
    return fade_io(img, t, dur, 0.5, 0.5)

# ---------------------------------------------------------------- 5. the results (33.3 - 40.1 s)
def p05(t, dur):
    img = bg(t); d = ImageDraw.Draw(img, "RGBA")
    x0, x1 = 600, 1640
    for i, (lab, v, col, t0) in enumerate((("Claude Opus 5.5", N.OPUS_MEAN, RED, 0.3), (GPT_NAME, N.GPT_MEAN, AMBER, 2.4),
                                            ("Toxic", 1.0, GREEN, 3.6))):
        a = alpha(t, t0); g = ease((t - t0) / 1.0)
        y = 280 + i * 150
        text(d, (x0 - 30, y + 40), lab, F(BOLD, 48), col, a, "rm")
        d.rounded_rectangle((x0, y, x1, y + 80), 14, fill=mix(PANEL, a))
        if g > 0.01: d.rounded_rectangle((x0, y, x0 + (x1 - x0) * v * g, y + 80), 14, fill=mix(col, a))
        num(d, f"{v * g:.2f}", 64, col, x0 + (x1 - x0) * v * g + 24, y + 40, a * clamp(g * 1.3), "lm")
    text(d, (x0, 730), "0 = a beginner's program   ·   1 = Toxic", F(MED, 32), GREY, alpha(t, 0.3), "lm")
    show(img, f"0 of {N.N_RUNS} AI runs reach 1.", BLK, 64, FG, W / 2, 880, t, 4.4)
    return fade_io(img, t, dur, 0.5, 0.5)

# ---------------------------------------------------------------- 6. the answer, under the question (40.1 - 53.4 s)
QS1 = ("Can a frontier AI agent turn ", "practice", " into a ", "design")
QS2 = ("that wins against opponents it has ", "never seen", "?")

def question_small(d, y, a, size=46):
    mline(d, y, QS1, size, a); mline(d, y + size * 1.25, QS2, size, a)


def p06(t, dur):
    img = bg(t); d = ImageDraw.Draw(img, "RGBA")
    question_small(d, 150, alpha(t, 0.1, None, 0.4) * 0.85)
    show(img, "Not yet.", BLK, 150, FG, W / 2, 360, t, 1.3)
    show(img, "They can't find a winning design, escape the traps of practice, or both.", BOLD, 42, GREY, W / 2, 500, t, 2.4)
    chart.answer_table(d, t, 1.0, (200, 580, 1720, 960), dict(head=3.6, gpt_traps=7.2, gpt_design=8.6, opus=10.6), size=40, hsize=34)
    return fade_io(img, t, dur, 0.5, 0.5)

# ---------------------------------------------------------------- 7. why not, 1: the design, run by run (53.4 - 72 s)
def why(img, t, n, label):
    show(img, f"WHY NOT · {n} · {label}", BOLD, 34, HL, 140, 90, t, 0.1, None, "l")


def p07(t, dur):
    img = bg(t); d = ImageDraw.Draw(img, "RGBA")
    why(img, t, 1, "THE DESIGN")
    chart.scatter(d, t, 1.0, (300, 200, 970, 870), dict(axes=0.3, toxic=1.0, gpt=5.6, gap=9.0, opus=12.8))
    show(img, "Each dot: one run", BOLD, 40, FG, 1260, 300, t, 0.8, None, "l")
    a = alpha(t, 15.0)
    if a > 0:
        d.rounded_rectangle((1250, 560, 1790, 900), 20, fill=mix(PANEL, a), outline=mix(HL, a), width=3)
        text(d, (1280, 610), "Gap to Toxic already", F(BOLD, 34), FG, a, "lm")
        text(d, (1280, 652), "there in practice:", F(BOLD, 34), FG, a, "lm")
        num(d, f"{N.OPUS_IN_PRACTICE:.0%}", 76, RED, 1280, 750, alpha(t, 15.4), "lm")
        text(d, (1490, 750), "Claude Opus 5.5", F(BOLD, 30), RED, alpha(t, 15.4), "lm")
        num(d, f"{N.GPT_IN_PRACTICE:.0%}", 76, AMBER, 1280, 845, alpha(t, 15.8), "lm")
        text(d, (1490, 845), GPT_NAME, F(BOLD, 30), AMBER, alpha(t, 15.8), "lm")
    return fade_io(img, t, dur, 0.5, 0.5)

# ---------------------------------------------------------------- 8. why not, 1: the design, game by game (72 - 80 s)
def p08(t, dur):
    img = bg(t); d = ImageDraw.Draw(img, "RGBA")
    why(img, t, 1, "THE DESIGN")
    show(img, GPT_NAME, BLK, 64, AMBER, 140, 200, t, 0.2, None, "l")
    show(img, "Its programs attack well, but don't survive.", BLK, 58, FG, 140, 300, t, 0.4, None, "l")
    x0, x1, vmax = 420, 1420, 6000
    X = lambda v: x0 + (x1 - x0) * v / vmax
    show(img, "15,000 games vs new opponents", BOLD, 34, GREY, 140, 410, t, 2.4, None, "l")
    for gi, (lab, tox, (lo, hi), y) in enumerate((("Wins", N.TOX_W, N.GPT_W, 470), ("Losses", N.TOX_L, N.GPT_L, 640))):
        t0 = 2.6 + gi * 1.2
        a = alpha(t, t0); g = ease((t - t0) / 1.0)
        text(d, (140, y + 48), lab, F(BLK, 56), FG, a, "lm")
        d.rounded_rectangle((x0, y, X(vmax), y + 40), 10, fill=mix(PANEL, a))
        if g > 0.01: d.rounded_rectangle((x0, y, X(tox * g), y + 40), 10, fill=mix(GREEN, a))
        text(d, (X(tox * g) + 16, y + 20), f"{tox:,}  Toxic", F(BOLD, 32), GREEN, a * clamp(g * 1.2), "lm")
        d.rounded_rectangle((x0, y + 56, X(vmax), y + 96), 10, fill=mix(PANEL, a))
        if g > 0.01:
            d.rounded_rectangle((x0, y + 56, X(hi * g), y + 96), 10, fill=mix(tuple(int(c * 0.55) for c in AMBER), a))
            d.rounded_rectangle((x0, y + 56, X(lo * g), y + 96), 10, fill=mix(AMBER, a))
        text(d, (X(hi * g) + 16, y + 76), f"{lo:,}–{hi:,}  {GPT_NAME}", F(BOLD, 32), AMBER, a * clamp(g * 1.2), "lm")
    show(img, f"Wins as often. Loses {N.LOSS_X[0]:.0f}–{N.LOSS_X[1]:.0f}× as often.", BLK, 62, AMBER, W / 2, 880, t, 4.6)
    return fade_io(img, t, dur, 0.5, 0.5)

# ---------------------------------------------------------------- 9. why not, 2: the traps of practice (80 - 93 s)
def p09(t, dur):
    img = bg(t); d = ImageDraw.Draw(img, "RGBA")
    why(img, t, 2, "THE TRAPS OF PRACTICE")
    a0 = alpha(t, 0.4)
    text(d, (1010, 220), "Claude Opus 5.5", F(BLK, 44), RED, a0, "mm")
    text(d, (1540, 220), GPT_NAME, F(BLK, 44), AMBER, a0, "mm")
    lo, hi = N.GPT_DROP
    rows = [("Stops early", f"{int(N.OPUS_UNUSED[0] + 0.5)}–{int(N.OPUS_UNUSED[1] + 0.5)} min unused", f"works to minute {N.GPT_LAST_SUB:.1f}+", 1.4),
            ("Polishes one idea", f"{N.OPUS_QSCAN} of 5 find the enemy first", f"{N.GPT_QSCAN} of {N.N_GPT} do", 4.1),
            ("Fits the practice set", f"C1, C5: up to {N.OPUS_WORST_DROP:.2f} lost", f"{lo:.2f}–{hi:.2f} lost, like Toxic", 5.4)]
    for i, (h, op, gp, t0) in enumerate(rows):
        y = 330 + i * 190
        a = alpha(t, t0)
        d.rounded_rectangle((140, y, 1800, y + 160), 20, fill=mix(PANEL, a))
        text(d, (180, y + 80), h, F(BLK, 48), FG, a, "lm")
        chart.mark(d, 790, y + 80, False, a, r=26)
        text(d, (836, y + 80), op, F(BOLD, 32), FG, a, "lm")
        ag = alpha(t, 8.2 + i * 0.3)
        chart.mark(d, 1340, y + 80, True, ag, r=26)
        text(d, (1386, y + 80), gp, F(BOLD, 32), FG, ag, "lm")
    return fade_io(img, t, dur, 0.5, 0.5)

# ---------------------------------------------------------------- 10. what it measures (93 - 102 s)
def p10(t, dur):
    img = bg(t)
    show(img, "It measures a skill real coding needs and most benchmarks miss:", BOLD, 48, FG, W / 2, 440, t, 0.3)
    show(img, "turning the cases you can test", BLK, 66, HL, W / 2, 550, t, 1.4)
    show(img, "into a design that wins on the ones you can't.", BLK, 66, HL, W / 2, 640, t, 1.4)
    return fade_io(img, t, dur, 0.5, 0.5)

# ---------------------------------------------------------------- 11. the question, the answer, the thesis (102 - 119 s)
def p11(t, dur):
    img = bg(t * 0.8, 0.3); d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 80, W, 1000), fill=BG + (int(230 * clamp(t / 0.6)),))
    question_small(d, 160, alpha(t, 0.2) * 0.85)
    show(img, "Not yet.", BLK, 130, FG, W / 2, 380, t, 0.6)
    show(img, "Practice traps on top of a deeper design gap:", BLK, 56, FG, W / 2, 560, t, 1.6)
    show(img, "Core War Arena measures both, and ranks agents", BOLD, 50, FG, W / 2, 640, t, 3.6)
    show(img, "on the one no model has closed.", BOLD, 50, FG, W / 2, 710, t, 3.6)
    if t > 9.6:
        aa = alpha(t, 9.6)
        x, y = terminal(d, (390, 830, 1530, 910), aa, "zsh")
        term_line(d, (x, y - 8), "$ harbor run -p harbor/corewar-hill -a opencode -m <your model>", aa, 25)
    return fade_io(img, t, dur, 0.5, 0.9)


SCENES = [("y01_question", p01, 12.6), ("y02_game", p02, 7.3), ("y03_test", p03, 6.2), ("y04_scale", p04, 7.2),
          ("y05_results", p05, 6.8), ("y06_answer", p06, 13.3), ("y07_design", p07, 18.6), ("y08_survive", p08, 8.0),
          ("y09_traps", p09, 13.0), ("y10_measure", p10, 9.0), ("y11_close", p11, 17.0)]
assert abs(sum(d for _, _, d in SCENES) - 119.0) < 1e-6

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn, dur in SCENES:
        if what in ("all", name):
            render(name, fn, dur); print("rendered", name, flush=True)
