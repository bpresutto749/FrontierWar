#!/usr/bin/env python3
"""The full demo video (about 8 minutes, no voice), built on one question and its answer.
Q: "Can a frontier AI agent turn practice into a design that wins against opponents it has never seen?"
A: "Not yet. They can't find a winning design, escape the traps of practice, or both."
Five chapters, named on a bar at the bottom: 1 the test (the game, practice vs hidden opponents, the
scale, no brute force, no cheating, the oracle and do-nothing runs), 2 the answer (both agents' runs,
0.71 / 0.84, then the answer under the question, with a table: GPT-6.1 sol misses the design and
escapes the traps; Claude Opus 5.5 misses both), 3 why not: the design (the chart of every run: over
90% of both agents' gap to Toxic is already there in practice; GPT-6.1 sol wins as often as Toxic and
loses 3-5x as often; Claude Opus too), 4 why not: the traps of practice (Claude Opus 5.5: run C5
replayed from its logs, then each trap up close; GPT-6.1 sol avoids them), 5 why it matters (everyday
coding, scope, the brief point by point, training), then the question and the answer again, and the
thesis. Full-screen slides in a dark theme; the two terminal scenes sit in a terminal window. Each
slide lasts as long as audit.py's reader needs at 4 words per second.
usage: python video/demo_full.py [all | <scene name>]   -> video/build/<scene>.mp4"""
import os
os.environ["VIDEO_THEME"] = "dark"           # before style.py is imported, by this file or by the scenes
import sys
from functools import partial
from PIL import Image, ImageDraw, ImageFilter
from math import hypot, sin, pi
from style import (W, H, M, F, BG, LINE, FG, MUTED, RED, ACC, BLUE, ramp, mix, text, render, base, head, core_bg,
                   fade, clamp, term_line, TERM_BG, TERM_DIM, TERM_FG, TERM_GREEN, GREEN, PANEL, panel, arrow, terminal,
                   ACC_L, RED_L, GREEN_L, OPP_FILL, OPP_LINE, BLUE_T, tick, DWARF, TRACK, TERM_RED)
import explainer as ex
import demo as dm
import pitch as pt
import figures as N
import chart

# here part 3 also explains how the test runs, so the presentation's part-3 scenes take its name
# the parts follow the question: the test, the game, how it works, the answer, then the two reasons
P3, P4, P5, P6, P7 = ("3 · HOW THE TEST WORKS", "4 · THE ANSWER", "5 · REASON 1: THREE CLASSIC MISTAKES",
                      "6 · REASON 2: DESIGN", "7 · CAN THE SCORE BE TRUSTED?")
RUN = P5 + "  ·  CLAUDE OPUS, RUN C5"
RUN6 = P6 + "  ·  CLAUDE OPUS, RUN C5"
part3 = lambda scene: partial(scene, kicker=P3)

# ---------------------------------------------------------------- the spoken slides
# In the style of the 1:59 pitch: one message per slide, a title of at most 7 words, 3 items
# (4 for steps), short sentences, and only numbers that were already on screen.
def s_title(t, dur):
    img = core_bg(t * 0.9, 0.9); d = ImageDraw.Draw(img, "RGBA"); k = fade(t, dur, 0.3, 0.6)
    d.rectangle((0, 300, W, 790), fill=BG + (int(235 * k),))
    text(d, (W / 2, 450), "CORE WAR ARENA", F("InterDisplay-Black.otf", 156), FG, ramp(t, 0.5, 0.7) * k, "mm")
    text(d, (W / 2, 600), "AI agents write code all day.", F("Inter-Bold.otf", 52), FG, ramp(t, 1.3, 0.6) * k, "mm")
    text(d, (W / 2, 665), "We found a game where they lose.", F("Inter-Bold.otf", 52), ACC, ramp(t, 2.9, 0.6) * k, "mm")
    text(d, (W / 2, 745), "Break the Agent  ·  AfterQuery  ·  Junction 2026", F("Inter-Medium.otf", 30), MUTED, ramp(t, 4.8, 0.6) * k, "mm")
    return img

def s_question(t, dur):
    img, d, k = base(t, dur, set())
    a = ramp(t, 0.3, 0.7) * k
    text(d, (W / 2, 310), "THE QUESTION", F("Inter-Bold.otf", 30), ACC, a, "mm")
    text(d, (W / 2, 440), "Can AI agents write code that holds up", F("InterDisplay-Black.otf", 76), FG, a, "mm")
    text(d, (W / 2, 535), "against cases it has never seen?", F("InterDisplay-Black.otf", 76), FG, a, "mm")
    steps = ["The test", "The game", "The answer", "Two reasons", "Can we trust it?"]
    fnt = F("Inter-Bold.otf", 32)
    widths = [70 + d.textlength(s_, font=fnt) for s_ in steps]
    gap = 84
    x = (W - sum(widths) - (len(steps) - 1) * gap) / 2
    for i, s_ in enumerate(steps):
        aa = ramp(t, (3.5, 4.2, 4.8, 5.7, 6.0)[i], 0.5) * k
        d.ellipse((x, 704, x + 54, 758), fill=mix(ACC, aa))
        text(d, (x + 27, 731), str(i + 1), F("Inter-Black.otf", 28), BG, aa, "mm")
        text(d, (x + 70, 731), s_, fnt, FG, aa, "lm")
        x += widths[i] + gap
    return img

def s_game(t, dur):
    img, d, k = base(t, dur, set())
    head(d, t, "2 · THE GAME: CORE WAR", "A game where programs fight", k)
    for s_, y, t0 in (("Two programs,", 340, 0.8), ("one shared memory.", 402, 0.8), ("Each tries to crash", 512, 2.4), ("the other.", 574, 2.4)):
        text(d, (120, y), s_, F("Inter-SemiBold.otf", 50), FG, ramp(t, t0, 0.6) * k)
    text(d, (120, 704), "The last one running wins.", F("InterDisplay-Black.otf", 54), ACC, ramp(t, 3.8, 0.6) * k)
    text(d, (120, 784), "Both still running at the time limit: a draw.", F("Inter-Medium.otf", 32), MUTED, ramp(t, 5.2, 0.6) * k)
    pa = ramp(t, 0.6, 0.8) * k
    if pa > 0:
        core = core_bg(t * 0.55, 1.0).resize((820, 462), Image.BILINEAR)
        img.paste(core, (980, 320), Image.new("L", core.size, int(255 * pa)))
        d.rounded_rectangle((976, 316, 1804, 786), 14, outline=mix(LINE, pa), width=3)
        for j, (c, lab) in enumerate(((RED, "program A drops bombs"), (BLUE, "program B copies itself"))):
            d.rounded_rectangle((980 + j * 410, 812, 1004 + j * 410, 836), 5, fill=mix(c, pa))
            text(d, (1016 + j * 410, 824), lab, F("Inter-SemiBold.otf", 26), FG, pa, "lm")
    return img

def s_player(t, dur):
    img, d, k = base(t, dur, set())
    head(d, t, "2 · THE GAME: CORE WAR", "You don't play. You write the player.", k)
    boxes = [(120, "You write a program", LINE, PANEL, FG), (720, "It fights alone", LINE, PANEL, FG), (1340, "It gets a score", ACC, ACC_L, ACC)]
    for i, (x, s_, line, fill, col) in enumerate(boxes):
        a = ramp(t, (1.8, 2.9, 3.8)[i], 0.6) * k
        w = 460 if i != 1 else 480
        panel(d, (x, 380, x + w, 560), a, fill=fill, outline=line)
        text(d, (x + w / 2, 470), s_, F("Inter-Bold.otf", 38), col, a, "mm")
        if i: arrow(d, (x - 120, 470), (x - 20, 470), MUTED, a, width=6)
    text(d, (W / 2, 720), "That is exactly what AI coding agents do.", F("InterDisplay-Bold.otf", 54), FG, ramp(t, 4.9, 0.6) * k, "mm")
    return img

def s_lang(t, dur):
    img, d, k = base(t, dur, set())
    head(d, t, "2 · THE GAME: CORE WAR", "Easy to learn, very hard to master", k)
    a = ramp(t, 0.6, 0.7) * k
    text(d, (120, 250), "A complete program:", F("Inter-SemiBold.otf", 30), MUTED, a)
    x, y = terminal(d, (120, 300, 1060, 660), a, "dwarf.red")
    term_line(d, (x, y), "$ cat dwarf.red", a, 26)
    for i, (code, note) in enumerate(DWARF):
        aa = ramp(t, 1.2 + i * 0.8, 0.6) * k
        term_line(d, (x, y + 64 + i * 58), f"{code:<26s} ; {note}", aa, 28)
    for i, (n, lab) in enumerate((("about 20", "commands"), ("1 page", "of rules"))):
        aa = ramp(t, 4.6 + i * 0.6, 0.6) * k
        text(d, (1180, 380 + i * 130), n, F("InterDisplay-Black.otf", 64), FG, aa, "lm")
        text(d, (1180, 440 + i * 130), lab, F("Inter-SemiBold.otf", 32), MUTED, aa, "lm")
    if t > 6.4:
        text(d, (120, 760), "Human experts have refined their programs for 30 years.", F("InterDisplay-Bold.otf", 46), FG, ramp(t, 6.4, 0.8) * k)
    return img

def s_rps(t, dur):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, "2 · THE GAME: NO PERFECT PROGRAM", "Like rock, paper, scissors", k)
    cx, cy, R = 560, 630, 230
    pts = {"SCANNER": (cx, cy - R), "PAPER": (cx + R * 0.95, cy + R * 0.55), "STONE": (cx - R * 0.95, cy + R * 0.55)}
    for i, (name, p) in enumerate(pts.items()):
        a = ramp(t, 0.6 + i * 0.3, 0.6) * k
        d.ellipse((p[0] - 92, p[1] - 92, p[0] + 92, p[1] + 92), fill=mix(PANEL, a), outline=mix(FG, a), width=4)
        text(d, p, name, F("Inter-Black.otf", 27), FG, a, "mm")
    fam = [("Scanner:", "hunts the enemy"), ("Paper:", "copies itself everywhere"), ("Stone:", "bombs everything")]
    for i, ((w, l), (h, s_)) in enumerate(zip([("SCANNER", "PAPER"), ("PAPER", "STONE"), ("STONE", "SCANNER")], fam)):
        a = ramp(t, (3.6, 5.2, 6.4)[i], 0.6) * k
        arrow(d, pts[w], pts[l], MUTED, a, width=5, head=24, shrink=104)
        mx, my = (pts[w][0] + pts[l][0]) / 2, (pts[w][1] + pts[l][1]) / 2
        ox, oy = mx - cx, my - cy; n = (ox * ox + oy * oy) ** 0.5 or 1
        text(d, (mx + ox / n * 44, my + oy / n * 44), "beats", F("Inter-SemiBold.otf", 24), MUTED, a, "mm")
        fb = F("Inter-Bold.otf", 40)
        text(d, (1040, 380 + i * 100), h, fb, FG, a, "lm")
        text(d, (1040 + d.textlength(h, font=fb) + 14, 380 + i * 100), s_, F("Inter-Medium.otf", 40), FG, a, "lm")
    a = ramp(t, 7.2, 0.6) * k
    panel(d, (1020, 700, 1800, 820), a, fill=ACC_L, outline=ACC)
    text(d, (1050, 760), "Every style can be beaten.", F("Inter-Bold.otf", 40), ACC, a, "lm")
    return img

def s_test(t, dur):
    img, d, k = base(t, dur, {"diff", "integ"})
    head(d, t, P3, "One program, 30 secret opponents", k)
    a1 = ramp(t, 0.6, 0.6) * k
    panel(d, (120, 316, 520, 452), a1, fill=RED_L, outline=RED, r=18)
    text(d, (320, 384), "the AI's program", F("Inter-Bold.otf", 34), RED, a1, "mm")
    a2 = ramp(t, 1.1, 0.6) * k
    arrow(d, (540, 384), (660, 384), MUTED, a2, width=6)
    text(d, (600, 344), "plays", F("Inter-SemiBold.otf", 24), MUTED, a2, "mm")
    for i in range(30):
        r, c = divmod(i, 10)
        x, y = 690 + c * 108, 312 + r * 50
        aa = ramp(t, 1.3 + i * 0.03, 0.4) * k
        d.rounded_rectangle((x, y, x + 96, y + 42), 10, fill=mix(OPP_FILL, aa), outline=mix(OPP_LINE, aa), width=2)
        text(d, (x + 48, y + 21), "?", F("Inter-Bold.otf", 22), OPP_LINE, aa, "mm")
    text(d, (1230, 496), "500 games against each.", F("Inter-Bold.otf", 34), BLUE_T, ramp(t, 2.4, 0.6) * k, "mm")
    text(d, (120, 640), "Win 3  ·  draw 1  ·  loss 0   →   a score from 0 to 1.", F("Inter-Bold.otf", 44), FG, ramp(t, 3.6, 0.6) * k, "lm")
    aa = ramp(t, 6.4, 0.6) * k
    panel(d, (120, 760, 1800, 880), aa, fill=GREEN_L, outline=GREEN, r=18)
    text(d, (160, 820), "A human expert's program takes the same test: Toxic, rated #1 of 264.", F("Inter-Bold.otf", 36), GREEN, aa, "lm")
    return img

RULES = ["Write a program", "Practise against 30 practice opponents", "Submit as often as it wants: the last one counts",
         "Decide when to stop: a clock shows the time left"]

def s_rules(t, dur):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, P3, "45 minutes to prepare", k)
    t_on = [0.8, 1.8, 3.4, 5.9]
    for i, h in enumerate(RULES):
        a = ramp(t, t_on[i], 0.6) * k
        y = 290 + i * 118
        panel(d, (120, y, 1800, y + 100), a, r=18)
        d.ellipse((150, y + 22, 206, y + 78), fill=mix(FG, a))
        text(d, (178, y + 50), str(i + 1), F("Inter-Black.otf", 30), BG, a, "mm")
        text(d, (236, y + 50), h, F("Inter-Bold.otf", 38), FG, a, "lm")
    aa = ramp(t, 8.5, 0.6) * k
    panel(d, (120, 790, 1800, 950), aa, fill=RED_L, outline=RED, r=18)
    text(d, (W / 2, 840), "Practice opponents are not the secret ones.", F("Inter-Bold.otf", 38), RED, aa, "mm")
    text(d, (W / 2, 900), "The AI never sees its real score.", F("Inter-Bold.otf", 38), FG, ramp(t, 10.0, 0.6) * k, "mm")
    return img

WORKS = [("A human reference:", "30 years of expert programs", {"gap"}),
         ("An exact score:", "the real simulator counts the wins", {"integ"}),
         ("No shortcuts:", "copies score zero", {"diff", "integ"})]
WORKS_ON = [0.8, 3.0, 5.2]

def s_works(t, dur):
    i_now = max([i for i, t0 in enumerate(WORKS_ON) if t > t0] or [0])
    img, d, k = base(t, dur, WORKS[i_now][2] if t > WORKS_ON[0] else set())
    head(d, t, P3, "Why Core War works", k)
    for i, (h, s_, _) in enumerate(WORKS):
        a = ramp(t, WORKS_ON[i], 0.6) * k
        y = 320 + i * 190
        panel(d, (120, y, 1800, y + 150), a, r=20)
        tick(d, 164, y + 53, a)
        fb = F("Inter-Bold.otf", 46)
        text(d, (244, y + 75), h, fb, FG, a, "lm")
        text(d, (244 + d.textlength(h, font=fb) + 16, y + 75), s_, F("Inter-Medium.otf", 46), FG, a, "lm")
    return img

def s_nobrute(t, dur):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, P3, "No brute force", k)
    a = ramp(t, 0.6, 0.7) * k
    f1, f2 = F("InterDisplay-Black.otf", 190), F("InterDisplay-Black.otf", 92)
    w = d.textlength("10", font=f1) + 8 + d.textlength("140", font=f2)
    x0 = (W - w) / 2
    text(d, (x0, 290), "10", f1, FG, a)
    text(d, (x0 + d.textlength("10", font=f1) + 8, 290), "140", f2, FG, a)
    text(d, (W / 2, 570), "possible 12-line programs.", F("Inter-SemiBold.otf", 44), FG, a, "mm")
    text(d, (W / 2, 660), f"An AI run tries at most about {N.about(N.GPT_TESTED[1])}.", F("Inter-Medium.otf", 40), MUTED, ramp(t, 2.0, 0.6) * k, "mm")
    text(d, (W / 2, 830), "What wins is good design, not compute.", F("InterDisplay-Black.otf", 60), ACC, ramp(t, 4.4, 0.6) * k, "mm")
    return img

TRUST = ["34 cheats and shortcuts tested: at most 0.24", "Scored in a separate, sealed box"]

def s_trust(t, dur):
    img, d, k = base(t, dur, {"integ", "craft"})
    head(d, t, P7, "Cheating scores zero", k)
    for i, s_ in enumerate(["Copy a published program", "Fake the score file"]):
        x = 120 + i * 855
        a = ramp(t, 0.7 + i * 0.8, 0.5) * k
        panel(d, (x, 300, x + 825, 440), a, r=16)
        text(d, (x + 30, 345), s_, F("Inter-SemiBold.otf", 32), FG, a, "lm")
        text(d, (x + 30, 399), "score 0.000", F("Inter-Black.otf", 34), RED, ramp(t, 1.0 + i * 0.8, 0.4) * k, "lm")
    for i, s_ in enumerate(TRUST):
        a = ramp(t, 3.2 + i * 2.4, 0.6) * k
        tick(d, 130, 568 + i * 140, a)
        text(d, (204, 590 + i * 140), s_, F("Inter-SemiBold.otf", 46), FG, a, "lm")
    return img

s_clock = partial(ex.s_clock, top="An earlier version had no clock. Minutes used, out of 45:", title="More time alone changed nothing",
                  kicker="3 · THE TRAPS  ·  CLAUDE OPUS")

WANT = [("Opponents it has never seen", {"diff"}), ("Good ideas win, not brute force", {"diff"}),
        ("An exact score, against the #1 human program", {"gap", "integ"})]

def s_want(t, dur):
    step = 1.8
    shown = [w for i, w in enumerate(WANT) if t > 0.8 + i * step]
    img, d, k = base(t, dur, set().union(*[w[1] for w in shown]) if shown else set())
    head(d, t, "1 · THE TEST WE WANT", "A test of code against the unseen", k)
    for i, (h, _) in enumerate(WANT):
        a = ramp(t, 0.8 + i * step, 0.6) * k
        y = 320 + i * 190
        panel(d, (120, y, 1800, y + 150), a, r=20)
        tick(d, 164, y + 53, a)
        text(d, (244, y + 75), h, F("Inter-Bold.otf", 50), FG, a, "lm")
    return img
s_train = partial(ex.s_train, title="It can also train a small model", punch="It learned a little. Lots left to learn.", kicker="5 · WHY IT MATTERS  ·  TRAINING",
                  intro="Qwen2.5-Coder-7B practised and kept its best attempts.")

bridge = ex.bridge

# ---------------------------------------------------------------- the two terminal scenes, as a real terminal session
# In the Terminal window the scene is the terminal itself: the same words, the slide's title and
# notes as comment lines, the commands typed at the prompt.
TX, TY, TL, TS = 64, 84, 54, 30             # left margin, first line, line height, font size

def tcom(d, i, s, a, col=TERM_DIM):
    text(d, (TX, TY + i * TL), "# " + s, M(TS), col, a, "lm")

def tprompt(d, i, t, a):
    term_line(d, (TX, TY + i * TL), "$ ", a, TS, cursor=int(t * 2) % 2 == 0)

GPT_CMD = "$ harbor run -p harbor/corewar-hill -a opencode -m openai/gpt-6.1-sol -k 5 -o jobs"

def t_runs(t, dur):
    img = Image.new("RGB", (W, H), TERM_BG); d = ImageDraw.Draw(img, "RGBA"); k = fade(t, dur)
    tcom(d, 0, "4 · the answer: two agents, five runs each, one command each", k)
    for row, cmd, wall, t0 in ((2, dm.CMD, 42 * 60 + 47, 0.6), (5, GPT_CMD, 1 * 3600 + 32 * 60 + 54, 5.4)):
        n = int(clamp((t - t0) / 1.4) * (len(cmd) - 2))
        if t > t0: term_line(d, (TX, TY + row * TL), cmd, k, TS, typed=n, cursor=t < t0 + 1.7)
        if t > t0 + 1.7:
            prog = clamp((t - t0 - 1.7) / 3.0); secs = int(round(prog * wall))
            f = M(TS); bar = 48; done = int(prog * bar); y = TY + (row + 1) * TL
            line = f"{min(5, int(prog * 5.2))}/5 runs  "
            term_line(d, (TX, y), line, k, TS)
            bx = TX + d.textlength(line, font=f)
            text(d, (bx, y), "━" * done, f, TERM_GREEN, k, "lm")
            text(d, (bx + d.textlength("━" * done, font=f), y), "━" * (bar - done), f, (60, 66, 76), k, "lm")
            text(d, (bx + d.textlength("━" * bar, font=f) + 24, y), f"{secs // 3600}:{secs // 60 % 60:02d}:{secs % 60:02d}", f, TERM_DIM, k, "lm")
    if t > 10.2:
        tcom(d, 8, "Each run in its own sealed box, 45 minutes each.", ramp(t, 10.2, 0.4) * k)
    if t > 11.6:
        tcom(d, 10, "How did they score?", ramp(t, 11.6, 0.6) * k, TERM_FG)
        tprompt(d, 11, t, ramp(t, 11.6, 0.6) * k)
    return img

def t_craft(t, dur):
    img = Image.new("RGB", (W, H), TERM_BG); d = ImageDraw.Draw(img, "RGBA"); k = fade(t, dur)
    tcom(d, 0, "7 · can the score be trusted? Anyone can check it, with one command", k)
    for i, (cmd, out, c, note) in enumerate(ex.TERM):
        row, t0 = 2 + 3 * i, 0.8 + i * 1.5
        if t < t0: continue
        n = int(clamp((t - t0) / 0.8) * (len(cmd) - 2))
        term_line(d, (TX, TY + row * TL), cmd, k, TS, typed=n, cursor=t < t0 + 0.9)
        if t > t0 + 0.9:
            term_line(d, (TX, TY + (row + 1) * TL), f"{out}   # {note}", ramp(t, t0 + 0.9, 0.4) * k, TS, color=c)
    if t > 6.0:
        tcom(d, 11, "Same program, same score, every time.", ramp(t, 6.0, 0.6) * k, TERM_FG)
        tprompt(d, 12, t, ramp(t, 6.0, 0.6) * k)
    return img

# ---------------------------------------------------------------- two models
AMBER = (245, 166, 35)                      # GPT-6.1; red stays Claude Opus, green the #1 human program
r2 = lambda x: f"{x:.2f}"

def s_result(t, dur):
    img, d, k = base(t, dur, {"gap"})
    head(d, t, P4, "Both agents fall short of the expert", k)
    x0, x1 = 760, 1650
    text(d, (120, 296), "Reward:   0 = the beginner's program   ·   1 = the #1 human program", F("Inter-SemiBold.otf", 28), MUTED, ramp(t, 0.4) * k)
    ex.hbar(d, t, x0, x1, 360, 50, 0.0, ex.DIM, 0.6, "Doing nothing", lambda g: "0.000", lab_col=MUTED)
    ex.hbar(d, t, x0, x1, 450, 50, N.OPUS_MEAN, RED, 1.6, "Claude Opus 5.5, 5 runs", lambda g: f"{N.OPUS_MEAN * g:.3f}")
    ex.hbar(d, t, x0, x1, 560, 50, N.GPT_MEAN, AMBER, 3.0, f"GPT-6.1 sol, {N.N_GPT} runs", lambda g: f"{N.GPT_MEAN * g:.3f}")
    ex.hbar(d, t, x0, x1, 670, 50, 1.0, GREEN, 4.4, "The #1 human program", lambda g: f"{1.0 * g:.3f}")
    for runs, y, col, t0 in ((N.OPUS, 450, RED, 2.6), (N.GPT, 560, AMBER, 4.0)):
        da = ramp(t, t0, 0.5) * k
        xs = sorted(x0 + (x1 - x0) * r["reward"] for r in runs)
        for j, cx in enumerate(xs):
            dy = 0 if j == 0 or cx - xs[j - 1] > 18 else (-9 if j % 2 else 9)
            d.ellipse((cx - 9, y + 66 + dy - 9, cx + 9, y + 66 + dy + 9), fill=mix(col, da), outline=mix(BG, da), width=2)
    text(d, (x0, 754), "each dot is one run", F("Inter-Medium.otf", 22), MUTED, ramp(t, 4.4) * k, "lt")
    aa = ramp(t, 6.4, 0.7) * k
    panel(d, (120, 810, 1800, 945), aa, fill=RED_L, outline=RED)
    text(d, (960, 858), f"0 of {N.N_RUNS} AI runs reached the #1 human program's score.", F("InterDisplay-Black.otf", 44), RED, aa, "mm")
    text(d, (960, 912), f"these {5 + N.N_GPT}, and 22 Opus runs on earlier versions", F("Inter-SemiBold.otf", 28), FG, ramp(t, 7.4, 0.6) * k, "mm")
    return img

def s_levels(t, dur):
    """GPT-6.1 against the #1 human program, over the 15,000 games of the real test."""
    img, d, k = base(t, dur, {"gap", "diff"})
    head(d, t, P6 + "  ·  GPT-6.1", "Even the stronger agent loses more", k)
    a = ramp(t, 0.8, 0.6) * k
    text(d, (120, 280), "15,000 games of the real test", F("Inter-Bold.otf", 34), FG, a, "lm")
    x0, x1, vmax = 300, 880, 10000
    X = lambda v: x0 + (x1 - x0) * v / vmax
    for gi, (lab, tox, (lo, hi)) in enumerate((("wins", N.TOX_W, N.GPT_W), ("losses", N.TOX_L, N.GPT_L), ("draws", N.TOX_T, N.GPT_T))):
        t0 = 1.4 + gi * 1.2
        aa = ramp(t, t0, 0.6) * k; g = ramp(t, t0, 1.0)
        y = 340 + gi * 130
        text(d, (120, y + 40), lab, F("Inter-Bold.otf", 34), FG, aa, "lm")
        d.rounded_rectangle((x0, y, x0 + max(4, (X(tox) - x0) * g), y + 34), 8, fill=mix(GREEN, aa))
        text(d, (X(tox * g) + 12, y + 17), f"{tox:,}", F("Inter-Bold.otf", 26), GREEN, aa, "lm")
        d.rounded_rectangle((x0, y + 44, x0 + max(4, (X(hi) - x0) * g), y + 78), 8, fill=mix(tuple(int(c * 0.55) for c in AMBER), aa))
        d.rounded_rectangle((x0, y + 44, x0 + max(4, (X(lo) - x0) * g), y + 78), 8, fill=mix(AMBER, aa))
        text(d, (X(hi * g) + 12, y + 61), f"{lo:,}–{hi:,}", F("Inter-Bold.otf", 26), AMBER, aa, "lm")
    la = ramp(t, 1.4, 0.6) * k
    for j, (col, s_) in enumerate(((GREEN, "the #1 human program (Toxic)"), (AMBER, f"GPT-6.1, lowest to highest of {N.N_GPT} runs"))):
        d.rounded_rectangle((120 + j * 430, 720, 142 + j * 430, 742), 5, fill=mix(col, la))
        text(d, (154 + j * 430, 731), s_, F("Inter-SemiBold.otf", 24), col, la, "lm")
    a2 = ramp(t, 6.0, 0.6) * k
    text(d, (1060, 280), "Its 3 worst opponents (mean losses of 500)", F("Inter-Bold.otf", 34), FG, a2, "lm")
    text(d, (1560, 330), "Toxic", F("Inter-Bold.otf", 24), GREEN, a2, "mm")
    text(d, (1700, 330), "GPT-6.1", F("Inter-Bold.otf", 24), AMBER, a2, "mm")
    for i, gp in enumerate(N.WORST3):
        aa = ramp(t, 6.6 + i * 1.4, 0.6) * k
        y = 360 + i * 120
        panel(d, (1060, y, 1800, y + 104), aa, r=14)
        text(d, (1086, y + 36), gp["name"], F("Inter-Bold.otf", 32), FG, aa, "lm")
        st = gp["strategy"] if len(gp["strategy"]) <= 40 else gp["strategy"][:40].rsplit(" ", 1)[0] + " …"
        text(d, (1086, y + 76), st, F("Inter-Medium.otf", 22), MUTED, aa, "lm")
        text(d, (1560, y + 52), str(gp["toxic_losses"]), F("InterDisplay-Black.otf", 40), GREEN, aa, "mm")
        text(d, (1700, y + 52), str(gp["gpt_mean_losses"]), F("InterDisplay-Black.otf", 40), AMBER, aa, "mm")
    text(d, (W / 2, 830), f"It wins as often, and loses {N.LOSS_X[0]:.0f} to {N.LOSS_X[1]:.0f} times as often.", F("InterDisplay-Bold.otf", 50), AMBER,
         ramp(t, 11.6, 0.6) * k, "mm")
    text(d, (W / 2, 910), "Its programs attack well, but don't survive.", F("InterDisplay-Bold.otf", 46), FG, ramp(t, 14.0, 0.6) * k, "mm")
    return img

def s_answer(t, dur):
    img, d, k = base(t, dur, {"gap", "diff"})
    a = ramp(t, 0.3, 0.6) * k
    text(d, (W / 2, 200), P4, F("Inter-Bold.otf", 30), ACC, a, "mm")
    text(d, (W / 2, 360), "Not yet.", F("InterDisplay-Black.otf", 170), FG, a, "mm")
    text(d, (W / 2, 560), "One agent makes three classic mistakes.", F("InterDisplay-Bold.otf", 54), RED, ramp(t, 1.6, 0.6) * k, "mm")
    text(d, (W / 2, 660), "A stronger one avoids them all,", F("InterDisplay-Bold.otf", 54), AMBER, ramp(t, 3.8, 0.6) * k, "mm")
    text(d, (W / 2, 740), "and still loses three to five times as often", F("InterDisplay-Bold.otf", 54), FG, ramp(t, 5.6, 0.6) * k, "mm")
    text(d, (W / 2, 815), "as the #1 human program.", F("InterDisplay-Bold.otf", 54), FG, ramp(t, 5.6, 0.6) * k, "mm")
    return img

def cross_mark(d, x, y, a, col=RED, r=20):
    d.ellipse((x - r, y - r, x + r, y + r), fill=mix(col, a))
    q = r * 0.42
    d.line((x - q, y - q, x + q, y + q), fill=mix(BG, a), width=5); d.line((x - q, y + q, x + q, y - q), fill=mix(BG, a), width=5)

def tick_mark(d, x, y, a, col, r=20):
    d.ellipse((x - r, y - r, x + r, y + r), fill=mix(col, a))
    d.line((x - r * 0.45, y + r * 0.02, x - r * 0.1, y + r * 0.38, x + r * 0.5, y - r * 0.35), fill=mix(BG, a), width=5, joint="curve")

def s_why(t, dur):
    img, d, k = base(t, dur, {"gap", "diff"})
    head(d, t, P5, "Three classic mistakes", k)
    a0 = ramp(t, 0.6, 0.6) * k
    text(d, (1050, 290), "Claude Opus 5.5", F("Inter-Bold.otf", 32), RED, a0, "mm")
    text(d, (1530, 290), "GPT-6.1", F("Inter-Bold.otf", 32), AMBER, a0, "mm")
    lo, hi = N.GPT_DROP
    rows = [("Trusts the score it can see", f"real up to {N.OPUS_WORST_DROP:.2f} below practice", f"{lo:.2f} to {hi:.2f} below (expert {-N.REF['drop']:.2f})"),
            ("Polishes one idea", f"{N.OPUS_QSCAN} of 5 open with a quick scan", f"{N.GPT_QSCAN} of {N.N_GPT} open with a quick scan"),
            ("Stops too early", f"{int(N.OPUS_UNUSED[0] + 0.5)} to {int(N.OPUS_UNUSED[1] + 0.5)} minutes unused",
             f"last submission at minute {N.GPT_LAST_SUB:.1f}+")]
    for i, (h, op, gp) in enumerate(rows):
        t0 = 1.0 + i * 3.6
        a = ramp(t, t0, 0.6) * k
        y = 330 + i * 170
        panel(d, (120, y, 1800, y + 140), a, r=18)
        text(d, (150, y + 70), h, F("Inter-Bold.otf", 36), FG, a, "lm")
        a1 = ramp(t, t0 + 0.8, 0.6) * k
        cross_mark(d, 830, y + 70, a1)
        text(d, (862, y + 70), op, F("Inter-SemiBold.otf", 26), FG, a1, "lm")
        a2 = ramp(t, t0 + 1.8, 0.6) * k
        tick_mark(d, 1330, y + 70, a2, AMBER)
        text(d, (1362, y + 70), gp, F("Inter-SemiBold.otf", 26), FG, a2, "lm")
    text(d, (W / 2, 900), "Opus makes all three. GPT-6.1 avoids them.", F("InterDisplay-Bold.otf", 48), FG, ramp(t, 11.4, 0.6) * k, "mm")
    return img

REAL = [("It stops early", "says “done” while there is still time to improve"),
        ("It polishes one idea", "tunes one design instead of rethinking it"),
        ("It fits the practice set", "passes the shown tests, fails in real use")]

def s_real(t, dur):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, K3 + "  ·  WHY IT MATTERS", "Three classic coding traps", k)
    text(d, (120, 296), "The three traps of practice, in everyday coding:", F("Inter-SemiBold.otf", 34), MUTED, ramp(t, 0.4, 0.6) * k)
    for i, (game, work) in enumerate(REAL):
        t0 = 1.6 + i * 2.6
        a = ramp(t, t0, 0.6) * k
        y = 360 + i * 140
        panel(d, (120, y, 860, y + 112), a, fill=RED_L, outline=RED, r=16)
        text(d, (150, y + 56), game, F("Inter-Bold.otf", 32), RED, a, "lm")
        a2 = ramp(t, t0 + 0.8, 0.6) * k
        arrow(d, (880, y + 56), (980, y + 56), MUTED, a2, width=6)
        panel(d, (1000, y, 1800, y + 112), a2, r=16)
        text(d, (1030, y + 56), work, F("Inter-SemiBold.otf", 32), FG, a2, "lm")
    a3 = ramp(t, 10.0, 0.7) * k
    text(d, (W / 2, 850), "Each one looks like progress, and ships code that fails later.", F("InterDisplay-Bold.otf", 44), ACC, a3, "mm")
    return img

def s_close(t, dur):
    img = core_bg(8 + t * 0.5, 0.6); d = ImageDraw.Draw(img, "RGBA"); k = fade(t, dur, 0.5, 1.0)
    d.rectangle((0, 150, W, 990), fill=BG + (int(238 * k),))
    for x, v, lab, col, t0 in ((520, r2(N.OPUS_MEAN), "Claude Opus 5.5", RED, 0.4), (960, r2(N.GPT_MEAN), "GPT-6.1", AMBER, 1.2),
                               (1400, "1.00", "the #1 human program", GREEN, 2.0)):
        a = ramp(t, t0, 0.6) * k
        text(d, (x, 300), v, F("InterDisplay-Black.otf", 130), col, a, "mm")
        text(d, (x, 390), lab, F("Inter-Bold.otf", 32), col, a, "mm")
    a2 = ramp(t, 3.4, 0.7) * k
    text(d, (960, 520), "Surface mistakes on top of a deeper design gap:", F("InterDisplay-Black.otf", 52), FG, a2, "mm")
    text(d, (960, 590), "the benchmark measures both, and ranks agents", F("Inter-Bold.otf", 44), FG, a2, "mm")
    text(d, (960, 648), "on the one no model has closed.", F("Inter-Bold.otf", 44), FG, a2, "mm")
    a3 = ramp(t, 9.4, 0.7) * k
    text(d, (960, 770), "Try it:", F("Inter-SemiBold.otf", 30), MUTED, a3, "mm")
    x, y = terminal(d, (390, 800, 1530, 900), a3)
    term_line(d, (x, y), "$ harbor run -p harbor/corewar-hill -a opencode -m <your model>", a3, 25)
    return img

# ---------------------------------------------------------------- mistakes 1 and 3, up close
# Same layout as mistake 2: the AI on the left, the contrast on the right, two lines below.
# Every number and quotation comes from the v4 runs (results/trajectories_harbor_v4.md, FAILURES.md,
# and the runs' own trajectories and verifier logs in runs/harbor/v4-opencode-opus-5.5/).
C1_MIN = [0.4, 18.8, 21.1, 28.0, 30.5]                      # run C1's five submissions
C1_SEEN = [0.390, 0.395, 0.418, 0.427, 0.437]               # practice (sparring) score
C1_REAL = [0.391, 0.387, 0.367, 0.365, 0.373]               # real test (hidden hill) score

def s_seen(t, dur):
    """Run C1 raises its practice score and lowers its real one, and says why in its report."""
    img, d, k = base(t, dur, {"diff", "gap"})
    head(d, t, "3 · THE TRAPS  ·  CLAUDE OPUS, RUN C1", "Not just C5: practice up, hidden down", k)
    a = ramp(t, 0.8, 0.6) * k
    text(d, (120, 280), "Claude Opus, run C1", F("Inter-Bold.otf", 38), RED, a, "lm")
    panel(d, (120, 320, 980, 520), a, r=16)
    X = lambda m: 160 + 560 * m / 31
    Y = lambda v: 500 - 160 * (v - 0.36) / 0.085
    g = ramp(t, 1.2, 2.4)
    n = 1 + int(g * 4.999)
    for vals, col, lab in ((C1_SEEN, ACC, f"practice {C1_SEEN[-1]:.3f}"), (C1_REAL, RED, f"hidden {C1_REAL[-1]:.3f}")):
        pts = [(X(m), Y(v)) for m, v in zip(C1_MIN[:n], vals[:n])]
        if len(pts) > 1: d.line(pts, fill=mix(col, a), width=5)
        for q in pts: d.ellipse((q[0] - 7, q[1] - 7, q[0] + 7, q[1] + 7), fill=mix(col, a))
        text(d, (X(31) + 24, Y(vals[-1])), lab, F("Inter-Bold.otf", 28), col, a * clamp((g - 0.9) / 0.1), "lm")
    text(d, (X(0) + 4, Y(0.39) - 30), "both 0.39", F("Inter-SemiBold.otf", 22), MUTED, a, "lm")
    text(d, (120, 552), "its 5 submissions, in order", F("Inter-Medium.otf", 30), MUTED, ramp(t, 3.4, 0.6) * k, "lm")
    a2 = ramp(t, 5.0, 0.6) * k
    text(d, (1040, 280), "Its last message", F("Inter-Bold.otf", 38), FG, a2, "lm")
    panel(d, (1040, 320, 1800, 520), a2, outline=RED, r=18, width=3)
    for i, s_ in enumerate(("“I tuned the constants on the [practice set],", "so some of that 0.437 is overfitting.”")):
        text(d, (1072, 388 + i * 56), s_, F("Inter-SemiBoldItalic.otf", 32), FG, a2, "lm")
    text(d, (1040, 560), "It knew, and kept tuning on the practice set.", F("Inter-SemiBold.otf", 30), MUTED, ramp(t, 8.6, 0.6) * k, "lm")
    text(d, (W / 2, 720), "Practice goes up. The hidden score goes down.", F("InterDisplay-Bold.otf", 50), RED, ramp(t, 10.6, 0.6) * k, "mm")
    text(d, (W / 2, 800), "Toxic: 0.507 in practice, 0.487 on the hidden test.", F("InterDisplay-Bold.otf", 46), GREEN,
         ramp(t, 12.8, 0.6) * k, "mm")
    return img

C_USED = [("C1", 32.7), ("C2", 22.9), ("C3", 29.8), ("C4", 24.1), ("C5", 16.5)]   # agent minutes, out of 45

def s_stop(t, dur):
    """Every run stops with minutes left; run C2 names its next idea, then stops."""
    img, d, k = base(t, dur, {"diff"})
    head(d, t, "3 · THE TRAPS  ·  CLAUDE OPUS", "It names its next idea, then stops", k)
    a = ramp(t, 0.8, 0.6) * k
    text(d, (120, 280), "Claude Opus, 5 runs", F("Inter-Bold.otf", 38), RED, a, "lm")
    x0, x1, y = 120, 960, 400
    X = lambda m: x0 + (x1 - x0) * m / 45
    g = ramp(t, 1.2, 1.2)
    d.rounded_rectangle((x0, y, x1, y + 70), 12, fill=mix(TRACK, a))
    d.rounded_rectangle((x0, y, x0 + (X(16.5) - x0) * g, y + 70), 12, fill=mix(RED, a))
    if g >= 1: d.rectangle((X(16.5), y, X(32.7), y + 70), fill=mix(tuple(int(c * 0.6) for c in RED), a))
    for m, lab in ((0, "0"), (45, "45 min")):
        text(d, (X(m), y + 100), lab, F("Inter-SemiBold.otf", 26), MUTED, a, "mm")
    text(d, (X(24.6), y - 30), "every run stopped here", F("Inter-SemiBold.otf", 26), RED, ramp(t, 2.4, 0.6) * k, "mm")
    text(d, (120, 590), "12 to 29 of its 45 minutes left unused", F("Inter-Bold.otf", 36), FG, ramp(t, 3.4, 0.6) * k, "lm")
    a2 = ramp(t, 8.6, 0.6) * k
    text(d, (1040, 280), "Run C2, its last message", F("Inter-Bold.otf", 38), FG, a2, "lm")
    panel(d, (1040, 320, 1800, 722), a2, outline=RED, r=18, width=3)
    q = [("“...a stronger second strategy ... would be", 8.6, 390), ("the next thing to try.", 8.6, 444),
         ("...with about 22 minutes left on the clock.”", 12.4, 540)]
    for s_, t0, y in q:
        text(d, (1072, y), s_, F("Inter-SemiBoldItalic.otf", 32), FG, ramp(t, t0, 0.6) * k, "lm")
    text(d, (1072, 656), "Then the run ends.", F("Inter-Bold.otf", 32), RED, ramp(t, 14.4, 0.6) * k, "lm")
    text(d, (W / 2, 840), "Every reply showed it the minutes left.", F("InterDisplay-Bold.otf", 46), ACC, ramp(t, 15.4, 0.6) * k, "mm")
    return img

# ---------------------------------------------------------------- mistake 2, up close
def s_polish(t, dur):
    """The AI tunes one scanner; the expert program opens with a quick scan, then attacks."""
    img, d, k = base(t, dur, {"diff"})
    head(d, t, "3 · THE TRAPS  ·  CLAUDE OPUS, RUN C5", "It polishes one idea", k)
    a = ramp(t, 0.8, 0.6) * k
    text(d, (120, 280), "Claude Opus (run C5)", F("Inter-Bold.otf", 38), RED, a, "lm")
    for i in range(18):
        ai = ramp(t, 1.2 + i * 0.1, 0.3) * k
        r_, c_ = divmod(i, 6); x0, y0 = 120 + c_ * 124, 320 + r_ * 66
        d.rounded_rectangle((x0, y0, x0 + 108, y0 + 52), 10, fill=mix(PANEL, ai), outline=mix(RED, ai * 0.8), width=2)
        text(d, (x0 + 54, y0 + 26), "scan", F("Inter-Medium.otf", 24), MUTED, ai, "mm")
    text(d, (120, 552), "one scanner, dozens of small variants", F("Inter-Medium.otf", 30), MUTED, ramp(t, 3.0, 0.6) * k, "lm")
    at = ramp(t, 3.6, 0.5) * k
    x, y = terminal(d, (120, 600, 980, 722), at, "run C5 — from its log")
    term_line(d, (x, y + 15), '$ for p in "20 10" "24 12" "16 8" "28 14" "32 16"; do ...', at, 18)
    a2 = ramp(t, 7.6, 0.6) * k
    text(d, (1040, 280), "Toxic, the #1 human program", F("Inter-Bold.otf", 38), GREEN, a2, "lm")
    for (x0, y0, x1, y1), h, sub, t0 in (((1040, 320, 1390, 520), "1. Quick scan", "find the enemy", 8.4),
                                          ((1450, 320, 1800, 520), "2. Attack", "copy and spread", 10.0)):
        ab = ramp(t, t0, 0.6) * k
        panel(d, (x0, y0, x1, y1), ab, outline=GREEN, r=18, width=3)
        text(d, ((x0 + x1) / 2, y0 + 80), h, F("InterDisplay-Bold.otf", 40), GREEN, ab, "mm")
        text(d, ((x0 + x1) / 2, y0 + 136), sub, F("Inter-Medium.otf", 30), MUTED, ab, "mm")
    arrow(d, (1396, 420), (1444, 420), MUTED, ramp(t, 9.8, 0.5) * k, width=5, head=16)
    at2 = ramp(t, 11.2, 0.5) * k
    x, y = terminal(d, (1040, 600, 1800, 722), at2, "zsh")
    term_line(d, (x, y - 2), "$ grep -m1 strategy toxic.red", at2, 18)
    term_line(d, (x, y + 32), ";strategy qscan -> paper/imp", at2, 18)
    text(d, (W / 2, 820), "None of the 5 Opus programs finds the enemy first.", F("InterDisplay-Bold.otf", 50), RED, ramp(t, 12.6, 0.6) * k, "mm")
    text(d, (W / 2, 900), "Toxic does: find the enemy, then attack.", F("InterDisplay-Bold.otf", 50), GREEN, ramp(t, 15.2, 0.6) * k, "mm")
    return img


FIGHT = dict(dm.FIGHT_TXT, title="One hidden opponent: Blizzard", box=(250, 1670),
             card=[("A program loses when none of its code runs.", 0.8)],
             caps=["Toxic scans first.", "Toxic wins at step 41.",
                   "Opus's program bombs everywhere. Blizzard keeps running.", "Opus's code stops: it loses at step 9,060."])

# ================================================================ the storyline (v3)
# Built with three reviews (narration, logic, clarity): one question, a test that is fair and hard,
# the answer, then the two levels of the gap, then why it matters and the thesis.
# Names everywhere: Claude Opus (red), GPT-6.1 sol (amber), Toxic, the #1 human program (green),
# Dwarf, the beginner's program; practice opponents / hidden opponents; practice score / hidden score;
# reward only for the 0-1 number.
Q1 = ("Can a frontier AI agent turn ", "practice", "")
Q2 = ("into a ", "design", " that wins against opponents")
Q3 = ("it has ", "never seen", "?")
STOPS = ["The test", "The answer", "The traps of practice", "The design", "Conclusion"]
K1, K2, K3, K4, K5 = ("1 · THE TEST", "2 · THE ANSWER", "3 · THE TRAPS OF PRACTICE", "4 · THE DESIGN", "5 · CONCLUSION")
ANSWER = "They can't escape the traps of practice, find a winning design, or both."
GPT_NAME = "GPT-6.1 sol"

dm.LABELS.update({"ai": "Claude Opus (run C5)", "expert": "Toxic", "practice": "Practice", "practice_sub": "the score it could see",
                  "real": "Hidden test", "real_sub": "never shown to it", "ai_prog": "Claude Opus, run C5",
                  "expert_prog": "Toxic, the #1 human program", "ai_panel": "Claude Opus, run C5 (red)",
                  "expert_panel": "Toxic (green)", "chart_expert": "Toxic: 0.507", "stats_note": "Scored by the game's official simulator.",
                  "compact": True, "counters": False, "log_strip": False, "rows": 4, "legend": "dark = code running   ·   light = memory it has written", "chart_caption": "red: Opus's submissions", "clock": "its clock"})
dm.FEED = [(m, act.replace("the expert's", "Toxic's"), why.replace("the expert's", "Toxic's"), log) for m, act, why, log in dm.FEED]


def mline(d, y, parts, font, a, hl=ACC):
    """One centred line in several colours: parts alternate plain, highlighted, plain..."""
    w = sum(d.textlength(p, font=font) for p in parts)
    x = W / 2 - w / 2
    for i, p in enumerate(parts):
        text(d, (x, y), p, font, hl if i % 2 else FG, a, "lm")
        x += d.textlength(p, font=font)


def v_title(t, dur):
    img = core_bg(t * 0.9, 0.9); d = ImageDraw.Draw(img, "RGBA"); k = fade(t, dur, 0.3, 0.6)
    d.rectangle((0, 300, W, 790), fill=BG + (int(235 * k),))
    text(d, (W / 2, 440), "CORE WAR ARENA", F("InterDisplay-Black.otf", 156), FG, ramp(t, 0.4, 0.7) * k, "mm")
    text(d, (W / 2, 590), "Coding agents practise on the tests they can see.", F("Inter-Bold.otf", 50), FG, ramp(t, 1.2, 0.6) * k, "mm")
    text(d, (W / 2, 655), "Then their code meets cases no one has seen.", F("Inter-Bold.otf", 50), MUTED, ramp(t, 2.6, 0.6) * k, "mm")
    text(d, (W / 2, 745), "Break the Agent  ·  AfterQuery  ·  Junction 2026", F("Inter-Medium.otf", 30), MUTED, ramp(t, 4.4, 0.6) * k, "mm")
    return img


def v_question(t, dur):
    img, d, k = base(t, dur, set())
    a = ramp(t, 0.3, 0.7) * k
    text(d, (W / 2, 200), "THE QUESTION", F("Inter-Bold.otf", 30), ACC, a, "mm")
    f = F("InterDisplay-Black.otf", 74)
    mline(d, 320, Q1, f, a); mline(d, 415, Q2, f, a); mline(d, 510, Q3, f, a)
    for i in range(10):
        aa = ramp(t, 2.6 + i * 0.05, 0.4) * k
        x = W / 2 - 5 * 76 + i * 76
        d.rounded_rectangle((x, 600, x + 64, 650), 10, fill=mix(OPP_FILL, aa), outline=mix(OPP_LINE, aa), width=2)
        text(d, (x + 32, 625), "?", F("Inter-Bold.otf", 24), OPP_LINE, aa, "mm")
    fnt = F("Inter-Bold.otf", 26)
    widths = [58 + d.textlength(s_, font=fnt) for s_ in STOPS]
    gap = 34
    x = (W - sum(widths) - (len(STOPS) - 1) * gap) / 2
    for i, s_ in enumerate(STOPS):
        aa = ramp(t, 3.6 + i * 0.35, 0.5) * k
        d.ellipse((x, 756, x + 44, 800), fill=mix(ACC, aa))
        text(d, (x + 22, 778), str(i + 1), F("Inter-Black.otf", 24), BG, aa, "mm")
        text(d, (x + 56, 778), s_, fnt, FG, aa, "lm")
        x += widths[i] + gap
    return img


def v_game(t, dur):
    img, d, k = base(t, dur, set())
    head(d, t, K1, "A 1984 game: programs fight", k)
    for s_, y, t0 in (("Two programs,", 340, 0.8), ("one shared memory.", 402, 0.8), ("Each tries to crash", 512, 2.4), ("the other.", 574, 2.4)):
        text(d, (120, y), s_, F("Inter-SemiBold.otf", 50), FG, ramp(t, t0, 0.6) * k)
    text(d, (120, 704), "The last one running wins.", F("InterDisplay-Black.otf", 54), ACC, ramp(t, 3.8, 0.6) * k)
    text(d, (120, 784), "Both still running at the time limit: a draw.", F("Inter-Medium.otf", 32), MUTED, ramp(t, 5.2, 0.6) * k)
    pa = ramp(t, 0.6, 0.8) * k
    if pa > 0:
        core = core_bg(t * 0.55, 1.0).resize((820, 462), Image.BILINEAR)
        img.paste(core, (980, 320), Image.new("L", core.size, int(255 * pa)))
        d.rounded_rectangle((976, 316, 1804, 786), 14, outline=mix(LINE, pa), width=3)
        text(d, (980, 300), "one memory of 8,000 cells", F("Inter-SemiBold.otf", 24), MUTED, pa, "ls")
    return img


def v_lang(t, dur):
    img, d, k = base(t, dur, set())
    head(d, t, K1, "You write the player, not the moves", k)
    a = ramp(t, 0.6, 0.7) * k
    text(d, (120, 250), "Dwarf, the beginner's program, in full:", F("Inter-SemiBold.otf", 30), MUTED, a)
    x, y = terminal(d, (120, 300, 1060, 660), a, "dwarf.red")
    term_line(d, (x, y), "$ cat dwarf.red", a, 26)
    for i, (code, note) in enumerate(DWARF):
        aa = ramp(t, 1.2 + i * 0.8, 0.6) * k
        term_line(d, (x, y + 64 + i * 58), f"{code:<26s} ; {note}", aa, 28)
    for i, (n, lab) in enumerate((("about 20", "commands"), ("1 page", "of rules"))):
        aa = ramp(t, 4.6 + i * 0.6, 0.6) * k
        text(d, (1180, 380 + i * 130), n, F("InterDisplay-Black.otf", 64), FG, aa, "lm")
        text(d, (1180, 440 + i * 130), lab, F("Inter-SemiBold.otf", 32), MUTED, aa, "lm")
    text(d, (120, 760), "Experts have refined their programs for 30 years.", F("InterDisplay-Bold.otf", 46), FG, ramp(t, 6.4, 0.8) * k)
    return img


def v_rps(t, dur):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, K1, "No perfect program", k)
    cx, cy, R = 560, 630, 230
    pts = {"SCANNER": (cx, cy - R), "PAPER": (cx + R * 0.95, cy + R * 0.55), "STONE": (cx - R * 0.95, cy + R * 0.55)}
    for i, (name, p) in enumerate(pts.items()):
        a = ramp(t, 0.6 + i * 0.3, 0.6) * k
        d.ellipse((p[0] - 92, p[1] - 92, p[0] + 92, p[1] + 92), fill=mix(PANEL, a), outline=mix(FG, a), width=4)
        text(d, p, name, F("Inter-Black.otf", 27), FG, a, "mm")
    fam = [("Scanner:", "finds the enemy, then attacks"), ("Paper:", "copies itself everywhere"), ("Stone:", "bombs blindly")]
    for i, ((w, l), (h, s_)) in enumerate(zip([("SCANNER", "PAPER"), ("PAPER", "STONE"), ("STONE", "SCANNER")], fam)):
        a = ramp(t, (3.0, 4.6, 6.0)[i], 0.6) * k
        arrow(d, pts[w], pts[l], MUTED, a, width=5, head=24, shrink=104)
        mx, my = (pts[w][0] + pts[l][0]) / 2, (pts[w][1] + pts[l][1]) / 2
        ox, oy = mx - cx, my - cy; n = (ox * ox + oy * oy) ** 0.5 or 1
        text(d, (mx + ox / n * 44, my + oy / n * 44), "beats", F("Inter-SemiBold.otf", 24), MUTED, a, "mm")
        fb = F("Inter-Bold.otf", 38)
        text(d, (1000, 380 + i * 100), h, fb, FG, a, "lm")
        text(d, (1000 + d.textlength(h, font=fb) + 14, 380 + i * 100), s_, F("Inter-Medium.otf", 38), FG, a, "lm")
    a = ramp(t, 7.0, 0.6) * k
    panel(d, (980, 700, 1800, 820), a, fill=ACC_L, outline=ACC)
    text(d, (1010, 760), "Every design can be beaten.", F("Inter-Bold.otf", 40), ACC, a, "lm")
    return img


def grid30(d, x0, y0, cols, cw, ch, a, mark, fill, line, txtcol, t=None, t0=0.0):
    for i in range(30):
        r_, c_ = divmod(i, cols)
        x, y = x0 + c_ * (cw + 10), y0 + r_ * (ch + 10)
        aa = a if t is None else a * clamp((t - t0 - i * 0.03) / 0.3)
        d.rounded_rectangle((x, y, x + cw, y + ch), 8, fill=mix(fill, aa), outline=mix(line, aa), width=2)
        text(d, (x + cw / 2, y + ch / 2), mark, F("Inter-Bold.otf", 20), txtcol, aa, "mm")


def v_split(t, dur):
    """The one picture of the test: practice opponents it can play, hidden opponents it never sees."""
    img, d, k = base(t, dur, {"diff"})
    head(d, t, K1, "Practice opponents, then hidden ones", k)
    a1 = ramp(t, 0.8, 0.6) * k
    panel(d, (120, 280, 940, 720), a1, r=20)
    text(d, (160, 330), "30 practice opponents", F("Inter-Bold.otf", 40), FG, a1, "lm")
    text(d, (160, 380), "it can play them as often as it likes", F("Inter-Medium.otf", 30), MUTED, a1, "lm")
    grid30(d, 160, 430, 10, 64, 44, a1, "▶", PANEL, LINE, MUTED, t, 1.0)
    text(d, (160, 670), "and sees its practice score", F("Inter-SemiBold.otf", 30), FG, a1, "lm")
    a2 = ramp(t, 4.2, 0.6) * k
    arrow(d, (950, 500), (1000, 500), MUTED, a2, width=6, head=20)
    panel(d, (1010, 280, 1800, 720), a2, r=20, outline=OPP_LINE)
    text(d, (1050, 330), "30 hidden opponents", F("Inter-Bold.otf", 40), BLUE_T, a2, "lm")
    text(d, (1050, 380), "never seen, 500 games each", F("Inter-Medium.otf", 30), MUTED, a2, "lm")
    grid30(d, 1050, 430, 10, 62, 44, a2, "?", OPP_FILL, OPP_LINE, OPP_LINE, t, 4.4)
    text(d, (1050, 670), "this is the score that counts", F("Inter-SemiBold.otf", 30), FG, a2, "lm")
    a3 = ramp(t, 7.8, 0.6) * k
    panel(d, (120, 770, 1800, 880), a3, fill=GREEN_L, outline=GREEN, r=18)
    text(d, (160, 825), "Toxic, the #1 of 264 human programs, takes the same test.", F("Inter-Bold.otf", 38), GREEN, a3, "lm")
    return img


RULES3 = ["Write one program", "Practise against the 30 practice opponents", "Submit as often as it wants: the last one counts",
          "Decide when to stop: a clock shows the minutes left"]

def v_rules(t, dur):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, K1, "45 minutes to prepare", k)
    for i, h in enumerate(RULES3):
        a = ramp(t, (0.8, 1.8, 3.4, 5.9)[i], 0.6) * k
        y = 290 + i * 118
        panel(d, (120, y, 1800, y + 100), a, r=18)
        d.ellipse((150, y + 22, 206, y + 78), fill=mix(FG, a))
        text(d, (178, y + 50), str(i + 1), F("Inter-Black.otf", 30), BG, a, "mm")
        text(d, (236, y + 50), h, F("Inter-Bold.otf", 38), FG, a, "lm")
    aa = ramp(t, 8.5, 0.6) * k
    panel(d, (120, 790, 1800, 950), aa, fill=RED_L, outline=RED, r=18)
    text(d, (W / 2, 845), "It never sees its hidden score.", F("Inter-Bold.otf", 40), RED, aa, "mm")
    text(d, (W / 2, 905), "It must judge for itself when its design is good.", F("Inter-SemiBold.otf", 34), FG, ramp(t, 10.0, 0.6) * k, "mm")
    return img


def v_scale(t, dur):
    img, d, k = base(t, dur, {"gap"})
    head(d, t, K1, "One number: the reward", k)
    text(d, (120, 300), "Each game: win 3, draw 1, loss 0. Over the 15,000 hidden games:", F("Inter-SemiBold.otf", 34), FG, ramp(t, 0.6, 0.6) * k)
    a = ramp(t, 2.6, 0.6) * k
    x0, x1, y = 400, 1520, 520
    d.line((x0, y, x1, y), fill=mix(MUTED, a), width=6)
    for v, lab, sub, col in ((0.0, "0", "Dwarf, the beginner's program", MUTED), (1.0, "1", "Toxic, the #1 human program", GREEN)):
        X = x0 + (x1 - x0) * v
        d.ellipse((X - 16, y - 16, X + 16, y + 16), fill=mix(col, a))
        text(d, (X, y - 40), lab, F("InterDisplay-Black.otf", 56), col, a, "mb")
        text(d, (X, y + 36), sub, F("Inter-Bold.otf", 30), col, a, "mt")
    text(d, (W / 2, 700), "Capped at 1. The raw score is not:", F("Inter-SemiBold.otf", 36), FG, ramp(t, 6.0, 0.6) * k, "mm")
    text(d, (W / 2, 760), "the benchmark doesn't saturate yet.", F("InterDisplay-Bold.otf", 44), ACC, ramp(t, 6.0, 0.6) * k, "mm")
    return img


def v_nobrute(t, dur):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, K1, "No brute force", k)
    a = ramp(t, 0.6, 0.7) * k
    f1, f2 = F("InterDisplay-Black.otf", 190), F("InterDisplay-Black.otf", 92)
    w = d.textlength("10", font=f1) + 8 + d.textlength("140", font=f2)
    x0 = (W - w) / 2
    text(d, (x0, 290), "10", f1, FG, a)
    text(d, (x0 + d.textlength("10", font=f1) + 8, 290), "140", f2, FG, a)
    text(d, (W / 2, 570), "possible 12-line programs.", F("Inter-SemiBold.otf", 44), FG, a, "mm")
    text(d, (W / 2, 660), f"A run tests at most about {N.about(N.GPT_TESTED[1])}.", F("Inter-Medium.otf", 40), MUTED, ramp(t, 2.0, 0.6) * k, "mm")
    text(d, (W / 2, 830), "What wins is design, not compute.", F("InterDisplay-Black.otf", 60), ACC, ramp(t, 4.4, 0.6) * k, "mm")
    return img


def v_trust(t, dur):
    img, d, k = base(t, dur, {"integ", "craft"})
    head(d, t, K1, "Cheats don't pay", k)
    for i, s_ in enumerate(["Copy a published program", "Fake the score file"]):
        x = 120 + i * 855
        a = ramp(t, 0.7 + i * 0.8, 0.5) * k
        panel(d, (x, 300, x + 825, 440), a, r=16)
        text(d, (x + 30, 345), s_, F("Inter-SemiBold.otf", 32), FG, a, "lm")
        text(d, (x + 30, 399), "reward 0.000", F("Inter-Black.otf", 34), RED, ramp(t, 1.0 + i * 0.8, 0.4) * k, "lm")
    for i, s_ in enumerate(["34 cheats and shortcuts tested: at most 0.24", "Scored in a separate, sealed box"]):
        a = ramp(t, 3.2 + i * 2.4, 0.6) * k
        tick(d, 130, 568 + i * 140, a)
        text(d, (204, 590 + i * 140), s_, F("Inter-SemiBold.otf", 46), FG, a, "lm")
    return img


CALIB = [("$ harbor run -p harbor/corewar-hill -a oracle", "Mean: 1.000", TERM_GREEN, "Toxic, the #1 human program"),
         ("$ harbor run -p harbor/corewar-hill -a nop", "Mean: 0.000", None, "doing nothing")]

def t_calib(t, dur):
    img = Image.new("RGB", (W, H), TERM_BG); d = ImageDraw.Draw(img, "RGBA"); k = fade(t, dur)
    tcom(d, 0, "1 · the test: anyone can check the scale, one command each", k)
    for i, (cmd, out, c, note) in enumerate(CALIB):
        row, t0 = 2 + 3 * i, 0.6 + i * 2.2
        if t < t0: continue
        term_line(d, (TX, TY + row * TL), cmd, ramp(t, t0, 0.3) * k, TS)
        if t > t0 + 0.9:
            term_line(d, (TX, TY + (row + 1) * TL), f"{out}   # {note}", ramp(t, t0 + 0.9, 0.4) * k, TS, color=c)
    if t > 5.6:
        tcom(d, 8, "Now the agents.", ramp(t, 5.6, 0.6) * k, TERM_FG)
        tprompt(d, 9, t, ramp(t, 5.6, 0.6) * k)
    return img


AGENTS = [(dm.CMD, f"Mean: {N.OPUS_MEAN:.3f}", TERM_RED, "Claude Opus 5.5, 5 runs"), (GPT_CMD, f"Mean: {N.GPT_MEAN:.3f}", AMBER, f"GPT-6.1 sol, {N.N_GPT} runs")]

def t_agents(t, dur):
    img = Image.new("RGB", (W, H), TERM_BG); d = ImageDraw.Draw(img, "RGBA"); k = fade(t, dur)
    tcom(d, 0, "2 · the answer: two agents, five runs each, each run in its own sealed box", k)
    for i, (cmd, out, c, note) in enumerate(AGENTS):
        row, t0 = 2 + 4 * i, 0.6 + i * 3.6
        if t < t0: continue
        term_line(d, (TX, TY + row * TL), cmd, ramp(t, t0, 0.3) * k, TS)
        prog = clamp((t - t0 - 0.6) / 1.8)
        f = M(TS); bar = 48; done = int(prog * bar); y = TY + (row + 1) * TL
        line = f"{min(5, int(prog * 5.2))}/5 runs  "
        term_line(d, (TX, y), line, k, TS)
        bx = TX + d.textlength(line, font=f)
        text(d, (bx, y), "━" * done, f, TERM_GREEN, k, "lm")
        text(d, (bx + d.textlength("━" * done, font=f), y), "━" * (bar - done), f, (60, 66, 76), k, "lm")
        if prog >= 1:
            term_line(d, (TX, TY + (row + 2) * TL), f"{out}   # {note}", ramp(t, t0 + 2.6, 0.4) * k, TS, color=c)
    return img


def v_result(t, dur):
    img, d, k = base(t, dur, {"gap"})
    head(d, t, K2, "Both agents fall short of Toxic", k)
    x0, x1 = 760, 1650
    text(d, (120, 296), "Reward:   0 = Dwarf, the beginner's program   ·   1 = Toxic, the #1 human program", F("Inter-SemiBold.otf", 28), MUTED, ramp(t, 0.4) * k)
    ex.hbar(d, t, x0, x1, 380, 56, N.OPUS_MEAN, RED, 1.2, "Claude Opus 5.5", lambda g: f"{N.OPUS_MEAN * g:.2f}", 36, 44)
    ex.hbar(d, t, x0, x1, 500, 56, N.GPT_MEAN, AMBER, 2.4, "GPT-6.1 sol", lambda g: f"{N.GPT_MEAN * g:.2f}", 36, 44)
    ex.hbar(d, t, x0, x1, 620, 56, 1.0, GREEN, 3.6, "Toxic", lambda g: f"{1.0 * g:.2f}", 36, 44)
    for runs, y, col, t0 in ((N.OPUS, 380, RED, 2.2), (N.GPT, 500, AMBER, 3.4)):
        da = ramp(t, t0, 0.5) * k
        xs = sorted(x0 + (x1 - x0) * r["reward"] for r in runs)
        for j, cx in enumerate(xs):
            dy = 0 if j == 0 or cx - xs[j - 1] > 18 else (-9 if j % 2 else 9)
            d.ellipse((cx - 9, y + 74 + dy - 9, cx + 9, y + 74 + dy + 9), fill=mix(col, da), outline=mix(BG, da), width=2)
    text(d, (x0, 700), "each dot: one run of 45 minutes", F("Inter-Medium.otf", 24), MUTED, ramp(t, 3.6) * k, "lt")
    aa = ramp(t, 5.4, 0.7) * k
    panel(d, (120, 790, 1800, 930), aa, fill=RED_L, outline=RED)
    text(d, (960, 838), f"0 of {N.N_RUNS} AI runs reached 1.", F("InterDisplay-Black.otf", 48), RED, aa, "mm")
    text(d, (960, 894), f"these {5 + N.N_GPT}, and 22 earlier Claude Opus runs", F("Inter-SemiBold.otf", 28), FG, ramp(t, 6.4, 0.6) * k, "mm")
    return img


def levels_diagram(d, box, a, lit=None):
    """The two layers of the gap: the traps of practice on top of the design."""
    x0, y0, x1, y1 = box
    h = y1 - y0; ys = y0 + h * 0.36
    for (t0, b0), label, right, key in (((y0, ys - 10), "On top: the traps of practice", f"Claude Opus ✗    {GPT_NAME} ✓", "traps"),
                                         ((ys + 10, y1), "Underneath: the design", "both behind Toxic, even in practice", "design")):
        on = lit in (None, key)
        aa = a * (1.0 if on else 0.35)
        panel(d, (x0, t0, x1, b0), aa, fill=ACC_L if lit == key else PANEL, outline=ACC if lit == key else LINE, r=18, width=3 if lit == key else 2)
        text(d, (x0 + 36, (t0 + b0) / 2), label, F("Inter-Bold.otf", 40), FG, aa, "lm")
        text(d, (x1 - 36, (t0 + b0) / 2), right, F("Inter-SemiBold.otf", 32), MUTED, aa, "rm")


def question_small(d, y, a, size=46):
    f = F("InterDisplay-Black.otf", size)
    mline(d, y, ("Can a frontier AI agent turn ", "practice", " into a ", "design", ""), f, a)
    mline(d, y + size * 1.25, ("that wins against opponents it has ", "never seen", "?"), f, a)


def v_answer(t, dur):
    img, d, k = base(t, dur, {"gap", "diff"})
    question_small(d, 130, ramp(t, 0.1, 0.4) * k * 0.9)
    text(d, (W / 2, 330), "Not yet.", F("InterDisplay-Black.otf", 140), FG, ramp(t, 1.0, 0.6) * k, "mm")
    text(d, (W / 2, 470), ANSWER, F("InterDisplay-Bold.otf", 40), MUTED, ramp(t, 2.2, 0.6) * k, "mm")
    chart.answer_table(d, t, k, (200, 560, 1720, 920), dict(head=4.0, gpt_traps=5.6, gpt_design=6.4, opus=7.4), size=40, hsize=34, traps_first=True)
    return img


def v_opener(kicker, lit, line1, line2):
    def scene(t, dur):
        img, d, k = base(t, dur, {"diff"} if lit == "traps" else {"gap"})
        a = ramp(t, 0.2, 0.6) * k
        text(d, (W / 2, 170), kicker, F("Inter-Bold.otf", 30), ACC, a, "mm")
        chart.answer_table(d, t, k, (200, 240, 1720, 620), dict(head=0.2, gpt_traps=0.2, gpt_design=0.2, opus=0.2), lit=lit, size=40, hsize=34, traps_first=True)
        text(d, (W / 2, 760), line1, F("InterDisplay-Bold.otf", 52), FG, ramp(t, 1.0, 0.6) * k, "mm")
        if line2: text(d, (W / 2, 840), line2, F("Inter-SemiBold.otf", 36), MUTED, ramp(t, 2.2, 0.6) * k, "mm")
        return img
    return scene


def v_chart(t, dur):
    """Every run's final program: practice score across, hidden-test score up."""
    img, d, k = base(t, dur, {"gap", "diff"})
    head(d, t, K4, "Both behind Toxic, even in practice", k)
    chart.scatter(d, t, k, (300, 290, 900, 890), dict(axes=0.6, toxic=1.4, gpt=4.0, gap=7.4, opus=10.4, drops=13.4))
    fb, fs = F("Inter-Bold.otf", 32), F("Inter-SemiBold.otf", 30)
    lines = [(0.8, "Practice: the 30 opponents it could see.", fs, MUTED, 370), (1.0, "Hidden test: 30 it never saw.", fs, MUTED, 414),
             (4.4, f"{GPT_NAME} holds up on new opponents,", fb, AMBER, 500), (4.4, "but trails Toxic even in practice.", fb, AMBER, 544),
             (10.8, "Claude Opus 5.5 trails further.", fb, RED, 620), (13.8, "Two runs fall below the line: the traps.", fb, RED, 664)]
    for t0, s_, f, col, y in lines:
        text(d, (1180, y), s_, f, col, ramp(t, t0, 0.6) * k, "lm")
    a = ramp(t, 17.0, 0.7) * k
    panel(d, (1180, 720, 1800, 960), a, fill=ACC_L, outline=ACC, r=18, width=3)
    text(d, (1210, 764), "Gap to Toxic already there in practice:", F("Inter-Bold.otf", 30), FG, a, "lm")
    text(d, (1210, 842), f"{N.OPUS_IN_PRACTICE:.0%}", F("InterDisplay-Black.otf", 72), RED, ramp(t, 17.6, 0.6) * k, "lm")
    text(d, (1400, 842), "Claude Opus 5.5", F("Inter-Bold.otf", 30), RED, ramp(t, 17.6, 0.6) * k, "lm")
    text(d, (1210, 920), f"{N.GPT_IN_PRACTICE:.0%}", F("InterDisplay-Black.otf", 72), AMBER, ramp(t, 18.4, 0.6) * k, "lm")
    text(d, (1400, 920), GPT_NAME, F("Inter-Bold.otf", 30), AMBER, ramp(t, 18.4, 0.6) * k, "lm")
    return img


def v_table(t, dur):
    img, d, k = base(t, dur, {"gap", "diff"})
    head(d, t, K4, f"Claude Opus: all three. {GPT_NAME}: none.", k)
    a0 = ramp(t, 0.6, 0.6) * k
    text(d, (1050, 290), "Claude Opus 5.5", F("Inter-Bold.otf", 32), RED, a0, "mm")
    text(d, (1530, 290), GPT_NAME, F("Inter-Bold.otf", 32), AMBER, a0, "mm")
    lo, hi = N.GPT_DROP
    rows = [("Stops early", f"{int(N.OPUS_UNUSED[0] + 0.5)}–{int(N.OPUS_UNUSED[1] + 0.5)} minutes unused", f"works to minute {N.GPT_LAST_SUB:.1f}+"),
            ("Polishes one idea", f"{N.OPUS_QSCAN} of 5 find the enemy first", f"{N.GPT_QSCAN} of {N.N_GPT} find the enemy first"),
            ("Fits the practice set", f"up to {N.OPUS_WORST_DROP:.2f} lower on the test", f"{lo:.2f}–{hi:.2f} lower (Toxic {-N.REF['drop']:.2f})")]
    for i, (h, op, gp) in enumerate(rows):
        t0 = 1.0 + i * 3.6
        a = ramp(t, t0, 0.6) * k
        y = 330 + i * 170
        panel(d, (120, y, 1800, y + 140), a, r=18)
        text(d, (150, y + 70), h, F("Inter-Bold.otf", 36), FG, a, "lm")
        a1 = ramp(t, t0 + 0.8, 0.6) * k
        cross_mark(d, 830, y + 70, a1)
        text(d, (862, y + 70), op, F("Inter-SemiBold.otf", 26), FG, a1, "lm")
        a2 = ramp(t, t0 + 1.8, 0.6) * k
        tick_mark(d, 1330, y + 70, a2, AMBER)
        text(d, (1362, y + 70), gp, F("Inter-SemiBold.otf", 26), FG, a2, "lm")
    text(d, (W / 2, 900), f"{GPT_NAME} avoids all three, and still trails Toxic: the design gap.", F("InterDisplay-Bold.otf", 44), FG, ramp(t, 11.4, 0.6) * k, "mm")
    return img


def v_wld(t, dur):
    img, d, k = base(t, dur, {"gap"})
    head(d, t, K4 + "  ·  " + GPT_NAME.upper(), "Wins as often, loses 3–5× more", k)
    text(d, (120, 290), "The 15,000 hidden games: Toxic, and GPT-6.1 sol's lowest to highest run", F("Inter-SemiBold.otf", 32), MUTED, ramp(t, 0.6, 0.6) * k)
    x0, x1, vmax = 420, 1560, 10000
    X = lambda v: x0 + (x1 - x0) * v / vmax
    for gi, (lab, tox, (lo, hi)) in enumerate((("wins", N.TOX_W, N.GPT_W), ("losses", N.TOX_L, N.GPT_L), ("draws", N.TOX_T, N.GPT_T))):
        t0 = 1.6 + gi * 1.6
        aa = ramp(t, t0, 0.6) * k; g = ramp(t, t0, 1.0)
        y = 370 + gi * 160
        text(d, (120, y + 50), lab, F("Inter-Bold.otf", 44), FG, aa, "lm")
        d.rounded_rectangle((x0, y, x0 + max(4, (X(tox) - x0) * g), y + 44), 10, fill=mix(GREEN, aa))
        text(d, (X(tox * g) + 14, y + 22), f"{tox:,}  Toxic", F("Inter-Bold.otf", 30), GREEN, aa, "lm")
        d.rounded_rectangle((x0, y + 56, x0 + max(4, (X(hi) - x0) * g), y + 100), 10, fill=mix(tuple(int(c * 0.55) for c in AMBER), aa))
        d.rounded_rectangle((x0, y + 56, x0 + max(4, (X(lo) - x0) * g), y + 100), 10, fill=mix(AMBER, aa))
        text(d, (X(hi * g) + 14, y + 78), f"{lo:,}–{hi:,}  GPT-6.1 sol", F("Inter-Bold.otf", 30), AMBER, aa, "lm")
    text(d, (W / 2, 880), f"It wins as often, and loses {N.LOSS_X[0]:.0f} to {N.LOSS_X[1]:.0f} times as often.", F("InterDisplay-Bold.otf", 52), AMBER,
         ramp(t, 7.0, 0.6) * k, "mm")
    return img


def v_gaps(t, dur):
    img, d, k = base(t, dur, {"gap", "diff"})
    head(d, t, K4 + "  ·  " + GPT_NAME.upper(), "Where it loses: against scanners", k)
    a0 = ramp(t, 0.6, 0.6) * k
    text(d, (120, 290), "Largest gaps: games lost, of 500", F("Inter-Bold.otf", 34), FG, a0, "lm")
    text(d, (1380, 290), "Toxic", F("Inter-Bold.otf", 28), GREEN, a0, "mm")
    text(d, (1640, 290), "GPT-6.1 sol", F("Inter-Bold.otf", 28), AMBER, a0, "mm")
    for i, gp in enumerate(N.WORST3):
        aa = ramp(t, 1.4 + i * 1.6, 0.6) * k
        y = 330 + i * 120
        panel(d, (120, y, 1800, y + 104), aa, r=14)
        text(d, (150, y + 52), gp["name"], F("Inter-Bold.otf", 36), FG, aa, "lm")
        st = gp["strategy"] if len(gp["strategy"]) <= 40 else gp["strategy"][:40].rsplit(" ", 1)[0] + " …"
        text(d, (560, y + 52), st, F("Inter-Medium.otf", 28), MUTED, aa, "lm")
        text(d, (1380, y + 52), str(gp["toxic_losses"]), F("InterDisplay-Black.otf", 46), GREEN, aa, "mm")
        text(d, (1640, y + 52), str(gp["gpt_mean_losses"]), F("InterDisplay-Black.otf", 46), AMBER, aa, "mm")
    rows = [f"Opponents it loses to more than 100 times: Toxic {N.REF['over100']}, GPT-6.1 sol {N.GPT_OVER100[0]} to {N.GPT_OVER100[1]}",
            f"It still beats Toxic's result against {N.GPT_BETTER[0]} to {N.GPT_BETTER[1]} of the 30"]
    for i, s_ in enumerate(rows):
        a = ramp(t, 6.8 + i * 2.8, 0.6) * k
        tick(d, 130, 730 + i * 90, a, AMBER)
        text(d, (196, 752 + i * 90), s_, F("Inter-SemiBold.otf", 34), FG, a, "lm")
    return img


def v_survive(t, dur):
    img, d, k = base(t, dur, {"gap"})
    a = ramp(t, 0.3, 0.6) * k
    text(d, (W / 2, 200), K4, F("Inter-Bold.otf", 30), ACC, a, "mm")
    text(d, (W / 2, 380), "Its programs attack well,", F("InterDisplay-Black.otf", 90), FG, a, "mm")
    text(d, (W / 2, 490), "but don't survive.", F("InterDisplay-Black.otf", 90), AMBER, ramp(t, 0.9, 0.6) * k, "mm")
    text(d, (W / 2, 660), f"Claude Opus too: {min(r['wlt'][1] for r in N.OPUS):,} to {max(r['wlt'][1] for r in N.OPUS):,} losses, against Toxic's {N.TOX_L:,}.",
         F("Inter-SemiBold.otf", 38), RED, ramp(t, 2.6, 0.6) * k, "mm")
    text(d, (W / 2, 760), "No model has closed this gap yet.", F("InterDisplay-Bold.otf", 50), FG, ramp(t, 5.2, 0.6) * k, "mm")
    return img


def v_scope(t, dur):
    img, d, k = base(t, dur, set())
    head(d, t, K5, "What it measures, and what it doesn't", k)
    rows = [("Measures", "designing from practice · holding up on new cases · knowing when to stop", ACC),
            ("Doesn't", "large codebases · bug fixing · APIs · vague requests (programs under 100 lines)", MUTED),
            ("Not shown yet", "that it ranks models like real tasks do: two models so far", MUTED)]
    for i, (h, s_, col) in enumerate(rows):
        a = ramp(t, 0.8 + i * 3.0, 0.6) * k
        y = 330 + i * 170
        panel(d, (120, y, 1800, y + 140), a, r=18, outline=ACC if i == 0 else LINE)
        text(d, (160, y + 70), h, F("Inter-Bold.otf", 38), col if i == 0 else FG, a, "lm")
        text(d, (520, y + 70), s_, F("Inter-SemiBold.otf", 30), FG, a, "lm")
    return img


BRIEF = [("Gap", "30", f"{r2(N.OPUS_MEAN)} and {r2(N.GPT_MEAN)} against 1.00; 0 of {N.N_RUNS} AI runs reach 1"),
         ("Meaningful difficulty", "30", "every rule and tool given; over 90% of the gap shows on opponents it can see"),
         ("Reward integrity", "25", "doing nothing, copies and faked scores: 0; 34 cheats tested: at most 0.24"),
         ("Craft", "15", "one command per run; scored by pMARS in a separate, sealed box"),
         ("Tiebreaker", "training", "a 7B model learns from it: working programs 24 → 53 of 64")]

def v_brief(t, dur):
    img, d, k = base(t, dur, {"gap", "diff", "integ", "craft", "tie"})
    head(d, t, K5, "The brief, point by point", k)
    for i, (name, pts, ev) in enumerate(BRIEF):
        t0 = 0.8 + i * 2.4
        a = ramp(t, t0, 0.6) * k
        y = 290 + i * 128
        panel(d, (120, y, 1800, y + 108), a, r=16)
        text(d, (150, y + 40), name, F("Inter-Bold.otf", 32), ACC, a, "lm")
        text(d, (150, y + 78), pts, F("Inter-SemiBold.otf", 22), MUTED, a, "lm")
        text(d, (600, y + 54), ev, F("Inter-SemiBold.otf", 30), FG, ramp(t, t0 + 0.4, 0.6) * k, "lm")
    return img


def v_llm(t, dur):
    """What the missing design says about LLMs: they test and refine a lot; practice ranks what they write."""
    img, d, k = base(t, dur, {"diff"})
    head(d, t, K4, "Why they fall short on design", k)
    rows = [("They test a lot", f"up to {N.GPT_TESTED[1]:,} programs in 45 min; Opus with 3× more time: same score"),
            ("They refine one idea", "one scanner, many small variants; composites tried, then dropped"),
            ("Toxic combines ideas", "find the enemy first, then copy and spread")]
    for i, (h, s_) in enumerate(rows):
        a = ramp(t, 0.8 + i * 3.4, 0.6) * k
        y = 300 + i * 150
        panel(d, (120, y, 1800, y + 124), a, r=18)
        text(d, (160, y + 62), h, F("Inter-Bold.otf", 36), FG, a, "lm")
        text(d, (720, y + 62), s_, F("Inter-SemiBold.otf", 30), MUTED, ramp(t, 1.2 + i * 3.4, 0.6) * k, "lm")
    a2 = ramp(t, 11.4, 0.7) * k
    text(d, (W / 2, 850), "They search among variants of a design, not among designs.", F("InterDisplay-Bold.otf", 46), ACC, a2, "mm")
    return img


def v_design_matters(t, dur):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, K4 + "  ·  WHY IT MATTERS", "Tests can't write the design", k)
    text(d, (W / 2, 400), "Practice ranks the variants an agent writes.", F("InterDisplay-Black.otf", 60), FG, ramp(t, 0.6, 0.7) * k, "mm")
    text(d, (W / 2, 490), "It cannot show the design it never wrote.", F("InterDisplay-Black.otf", 60), ACC, ramp(t, 2.0, 0.7) * k, "mm")
    a3 = ramp(t, 4.6, 0.7) * k
    text(d, (W / 2, 700), "Core War Arena measures a skill real coding needs and most benchmarks miss:", F("Inter-Bold.otf", 36), FG, a3, "mm")
    text(d, (W / 2, 766), "turning the cases you can test into a design that wins on the ones you can't.", F("InterDisplay-Black.otf", 42), ACC, a3, "mm")
    return img


TRAIN = [("19", "training runs improve on the reward, outside the noise", "models from 3B to 32B; two methods"),
         ("2 seeds", "the gain replicates", "at 7B, 14B and 32B"),
         ("0.01 → 0.08", "a 32B model, writing its own bombers", "from the task text alone; best program 0.33")]

def v_train(t, dur):
    """Bonus: the environment also trains small models (RL_SYNTHESIS.md, the positive results)."""
    img, d, k = base(t, dur, {"tie"})
    head(d, t, "BONUS  ·  TRAINING", "It can also train small models", k)
    text(d, (120, 290), "Expert iteration and reinforcement learning on its reward (RL_SYNTHESIS.md):", F("Inter-SemiBold.otf", 30), MUTED, ramp(t, 0.4) * k)
    for i, (big, h, sub) in enumerate(TRAIN):
        a = ramp(t, 1.4 + i * 2.6, 0.6) * k
        y = 350 + i * 170
        panel(d, (120, y, 1800, y + 146), a, r=18)
        text(d, (160, y + 73), big, F("InterDisplay-Black.otf", 60), ACC, a, "lm")
        text(d, (620, y + 52), h, F("Inter-Bold.otf", 36), FG, a, "lm")
        text(d, (620, y + 100), sub, F("Inter-SemiBold.otf", 28), MUTED, a, "lm")
    return img


def v_bookend(t, dur):
    img, d, k = base(t, dur, set())
    question_small(d, 150, ramp(t, 0.2, 0.6) * k, 52)
    text(d, (W / 2, 370), "Not yet.", F("InterDisplay-Black.otf", 130), FG, ramp(t, 1.6, 0.5) * k, "mm")
    chart.answer_table(d, t, k, (200, 500, 1720, 860), dict(head=2.6, gpt_traps=3.0, gpt_design=3.0, opus=3.4), size=40, hsize=34, traps_first=True)
    return img


def v_close(t, dur):
    img = core_bg(8 + t * 0.5, 0.6); d = ImageDraw.Draw(img, "RGBA"); k = fade(t, dur, 0.5, 1.0)
    d.rectangle((0, 150, W, 990), fill=BG + (int(238 * k),))
    for x, v, lab, col, t0 in ((520, r2(N.OPUS_MEAN), "Claude Opus 5.5", RED, 0.4), (960, r2(N.GPT_MEAN), GPT_NAME, AMBER, 1.0),
                               (1400, "1.00", "Toxic, the #1 human program", GREEN, 1.6)):
        a = ramp(t, t0, 0.6) * k
        text(d, (x, 300), v, F("InterDisplay-Black.otf", 130), col, a, "mm")
        text(d, (x, 390), lab, F("Inter-Bold.otf", 32), col, a, "mm")
    a2 = ramp(t, 3.0, 0.7) * k
    text(d, (960, 520), "Practice traps on top of a deeper design gap:", F("InterDisplay-Black.otf", 52), FG, a2, "mm")
    text(d, (960, 590), "Core War Arena measures both, and ranks agents", F("Inter-Bold.otf", 44), FG, a2, "mm")
    text(d, (960, 648), "on the one no model has closed.", F("Inter-Bold.otf", 44), FG, a2, "mm")
    a3 = ramp(t, 8.6, 0.7) * k
    text(d, (960, 770), "Try it:", F("Inter-SemiBold.otf", 30), MUTED, a3, "mm")
    x, y = terminal(d, (390, 800, 1530, 900), a3)
    term_line(d, (x, y), "$ harbor run -p harbor/corewar-hill -a opencode -m <your model>", a3, 25)
    return img


dm.LABELS["reveal_title"] = "Then the hidden test"
R4 = "3 · THE TRAPS  ·  CLAUDE OPUS, RUN C5"

# Each slide lasts as long as a reader at 4 words per second needs, plus 0.6 s (python video/audit.py at 4,
# every line read in order of appearance; at least 3 s for a bridge). The replay and the game keep their timing.
SCENES = [("e01_title", v_title, 7.9), ("e02_question", v_question, 11.8),
          # 1 the test: a game, practice vs hidden, the scale, no brute force, no cheating
          ("e03_game", v_game, 11.2), ("e04_lang", v_lang, 11.8), ("e05_rps", v_rps, 9.7),
          ("e06_split", v_split, 13.0), ("e07_rules", v_rules, 14.8), ("e08_scale", v_scale, 11.0),
          ("e09_nobrute", v_nobrute, 7.1), ("e10_trust", v_trust, 8.3), ("e11_calib", t_calib, 7.1),
          # 2 the answer, under the question
          ("e12_agents", t_agents, 8.2), ("e13_result", v_result, 12.9), ("e14_answer", v_answer, 14.0),
          # 3 the traps of practice (Claude Opus): one run, then each trap up close, then why it matters
          ("e15_open", v_opener(K3, "traps", "Claude Opus 5.5 falls into all three traps of practice.",
                                "One of its runs, C5, replayed from its logs."), 10.0),
          ("e16_rep1", dm.replay(R4 + ", MINUTES 0 TO 3", "Minutes 0–3: two quick tries", 0.0, 3.2), 18.0),
          ("e17_rep2", dm.replay(R4 + ", MINUTES 3 TO 12", "Minutes 3–12: tuning one scanner", 3.2, 12.5), 16.0),
          ("e18_rep3", dm.replay_end(R4 + ", MINUTES 12 TO 16", ("It stops at minute 16.5, with 28.5 minutes left.",
                                                                "Its practice score: almost Toxic's.", "Then the hidden test.")), 15.0),
          ("e19_reveal", dm.reveal(R4, ("30 opponents it never saw, 500 games each.",
                                        "Practice: 0.018 behind Toxic. Hidden test: 0.089 behind.", "It trusted the score it could see.")), 15.1),
          ("e20_seen", s_seen, 20.0), ("e21_polish", s_polish, 19.1),
          ("e22_fight", dm.fight(R4, FIGHT), dm.INTRO + dm.SLOW + dm.FAST + dm.OUT),
          ("e23_stop", s_stop, 18.9), ("e24_table", v_table, 17.2), ("e25_real", s_real, 19.0),
          # 4 the design: is that all? no. Both trail Toxic even in practice; why; why it matters
          ("e26_open", v_opener(K4, "design", "Is that all? No: both agents miss a winning design.",
                                "Even against opponents they can see, their programs trail Toxic's."), 9.2),
          ("e27_chart", v_chart, 24.0), ("e28_wld", v_wld, 11.8), ("e29_gaps", v_gaps, 15.3), ("e30_survive", v_survive, 8.2),
          ("e31_why", v_llm, 17.8), ("e32_matters", v_design_matters, 14.8),
          # 5 conclusion: the question and the answer again, the thesis; then the bonus
          ("e33_bookend", v_bookend, 10.4), ("e34_close", v_close, 13.0), ("e35_train", v_train, 17.6)]
RAW_SCENES = list(SCENES)                   # the scenes alone, without the chapter bar (for audit.py)

# ---------------------------------------------------------------- the frame: full-screen slides and a chapter bar
# No desktop: each scene fills the screen. A slim bar at the bottom names the six chapters and
# lights the current one; the two terminal scenes sit in a terminal window on the slide background.
CHAPTER_OF = {}
_starts = {"e03": 0, "e12": 1, "e15": 2, "e26": 3, "e33": 4}
_c = None
for _n, _, _ in SCENES:
    _c = _starts.get(_n[:3], _c)
    CHAPTER_OF[_n] = _c
NO_BAR = {"e01_title", "e02_question", "e33_bookend", "e34_close", "e35_train"}
TERMINAL = {"e11_calib", "e12_agents"}
TOTAL = sum(d for _, _, d in SCENES)


def chapter_bar(img, name, T):
    d = ImageDraw.Draw(img, "RGBA")
    cur = CHAPTER_OF[name]
    f = F("Inter-SemiBold.otf", 21); fb = F("Inter-Bold.otf", 21)
    y = 1046
    d.line((120, y - 26, 1800, y - 26), fill=mix(LINE, 1.0), width=2)
    d.line((120, y - 26, 120 + 1680 * T / TOTAL, y - 26), fill=mix(ACC, 0.9), width=2)
    x = 120
    for i, s_ in enumerate(STOPS):
        lab = f"{i + 1}  {s_}"
        on = i == cur
        text(d, (x, y), lab, fb if on else f, ACC if on else MUTED, 1.0 if on else 0.75, "lm")
        x += d.textlength(lab, font=fb) + 46
    return img


def terminal_window(content, t, dur):
    img, d, k = base(t, dur, set())
    s_ = 0.84
    sc = content.resize((round(W * s_), round(H * s_)), Image.LANCZOS)
    x0, y0 = (W - sc.width) // 2, 70
    d.rounded_rectangle((x0 - 2, y0 - 38, x0 + sc.width + 2, y0 + sc.height + 2), 14, fill=mix((36, 40, 48), k), outline=mix((58, 63, 72), k), width=2)
    for i, c in enumerate(((237, 106, 94), (245, 191, 79), (98, 197, 84))):
        cx = x0 + 22 + i * 22
        d.ellipse((cx - 7, y0 - 26, cx + 7, y0 - 12), fill=mix(c, k))
    text(d, (W / 2, y0 - 19), "zsh — harbor", F("Inter-Medium.otf", 20), (170, 176, 186), k, "mm")
    img.paste(sc, (x0, y0))
    return img


def framed(name, fn, start):
    def scene(t, dur):
        img = fn(t, dur)
        if name in TERMINAL: img = terminal_window(img, t, dur)
        if name not in NO_BAR: img = chapter_bar(img, name, start + t)
        return img
    return scene


_start, _framed = 0.0, []
for _name, _fn, _dur in SCENES:
    _framed.append((_name, framed(_name, _fn, _start), _dur)); _start += _dur
SCENES = _framed

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn, dur in SCENES:
        if what in ("all", name):
            render(name, fn, dur); print("rendered", name, flush=True)
