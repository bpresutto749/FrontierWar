#!/usr/bin/env python3
"""The presentation video (about 4 minutes): the test we want, the game, why it works, what we found.
Every number on screen comes from the repository (README.md, FAILURES.md, results/, TRAINING.md).
usage: python video/explainer.py [all | <scene name>]   -> video/build/<scene>.mp4"""
import math, os, sys
from PIL import Image, ImageDraw
from style import (W, H, FPS, F, M, BG, PANEL, LINE, FG, MUTED, DIM, TRACK, RED, GREEN, RED_L, GREEN_L, ACC, ACC_L, BLUE, CODE_BG,
                     terminal, term_line, TERM_GREEN, TERM_RED,
                     clamp, ease, ramp, mix, fade, text, core_bg, rail, panel, head, base, tick, cross, arrow,
                     hbar, DWARF, render)

def center_lines(d, lines, y, a, gap):
    for s, font, col in lines:
        text(d, (W / 2, y), s, font, col, a, "mm"); y += gap

# ---------------------------------------------------------------- opening
def s_title(t, dur):
    img = core_bg(t * 0.9, 0.9); d = ImageDraw.Draw(img, "RGBA"); k = fade(t, dur, 0.3, 0.6)
    d.rectangle((0, 300, W, 790), fill=BG + (int(235 * k),))
    text(d, (W / 2, 450), "CORE WAR ARENA", F("InterDisplay-Black.otf", 156), FG, ramp(t, 0.6, 0.8) * k, "mm")
    text(d, (W / 2, 600), "Can AI coding agents beat human experts", F("Inter-Bold.otf", 52), FG, ramp(t, 1.8, 0.8) * k, "mm")
    text(d, (W / 2, 665), "at a classic programming game?", F("Inter-Bold.otf", 52), ACC, ramp(t, 2.4, 0.8) * k, "mm")
    text(d, (W / 2, 745), "Break the Agent challenge  ·  AfterQuery  ·  Junction 2026", F("Inter-Medium.otf", 30), MUTED, ramp(t, 3.2, 0.8) * k, "mm")
    return img

def s_game(t, dur):
    img, d, k = base(t, dur, set())
    head(d, t, "2 · THE GAME: CORE WAR", "A game where programs fight", k)
    lines = [("Two programs share", FG), ("one computer memory.", FG), ("They take turns.", FG),
             ("Each tries to crash", FG), ("the other.", FG)]
    ys = [330, 390, 480, 570, 630]
    groups = [0, 0, 1, 2, 2]
    for (s, c), y, g in zip(lines, ys, groups):
        text(d, (120, y), s, F("Inter-SemiBold.otf", 48), c, ramp(t, 0.8 + g * 1.4, 0.7) * k)
    if t > 5.2:
        text(d, (120, 760), "The last one running wins.", F("InterDisplay-Black.otf", 54), ACC, ramp(t, 5.2, 0.7) * k)
    pa = ramp(t, 0.6, 0.8) * k
    if pa > 0:
        core = core_bg(t * 0.55, 1.0).resize((820, 462), Image.BILINEAR)
        img.paste(core, (980, 320), Image.new("L", core.size, int(255 * pa)))
        d.rounded_rectangle((976, 316, 1804, 786), 14, outline=mix(LINE, pa), width=3)
        text(d, (980, 300), "the shared memory, live", F("Inter-SemiBold.otf", 24), MUTED, pa, "ls")
        for j, (c, lab) in enumerate(((RED, "program A drops bombs"), (BLUE, "program B copies itself"))):
            d.rounded_rectangle((980 + j * 410, 812, 1004 + j * 410, 836), 5, fill=mix(c, pa))
            text(d, (1016 + j * 410, 824), lab, F("Inter-SemiBold.otf", 26), FG, pa, "lm")
    return img

def box(d, x, y, w, h, title, sub, a, col=FG, fill=PANEL):
    panel(d, (x, y, x + w, y + h), a, fill=fill, outline=col if col != FG else LINE)
    text(d, (x + w / 2, y + h / 2 - 22), title, F("Inter-Bold.otf", 36), col, a, "mm")
    text(d, (x + w / 2, y + h / 2 + 26), sub, F("Inter-Medium.otf", 26), MUTED, a, "mm")

def s_player(t, dur):
    img, d, k = base(t, dur, set())
    head(d, t, "2 · THE GAME: CORE WAR", "You don't play it. You write the player.", k)
    a1, a2, a3 = (ramp(t, 0.8 + i * 1.3, 0.7) * k for i in range(3))
    box(d, 120, 360, 460, 220, "You write", "a program, called a warrior", a1)
    arrow(d, (600, 470), (700, 470), MUTED, a2, width=6, shrink=0)
    box(d, 720, 360, 480, 220, "It fights alone", "thousands of games, no help", a2)
    arrow(d, (1220, 470), (1320, 470), MUTED, a3, width=6, shrink=0)
    box(d, 1340, 360, 460, 220, "It gets a score", "more wins, higher score", a3, ACC, ACC_L)
    if t > 5.0:
        aa = ramp(t, 5.0, 0.8) * k
        text(d, (W / 2, 720), "So the whole game is writing a good program.", F("InterDisplay-Bold.otf", 50), FG, aa, "mm")
        text(d, (W / 2, 790), "That is exactly what AI coding agents are built to do.", F("Inter-Medium.otf", 36), MUTED, ramp(t, 6.2, 0.8) * k, "mm")
    return img

def s_lang(t, dur):
    img, d, k = base(t, dur, set())
    head(d, t, "2 · THE GAME: CORE WAR", "Easy to learn, very hard to master", k)
    a = ramp(t, 0.6, 0.7) * k
    text(d, (120, 250), "A complete program, the classic first example:", F("Inter-SemiBold.otf", 27), MUTED, a)
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
        a = ramp(t, 0.6 + i * 0.4, 0.6) * k
        d.ellipse((p[0] - 92, p[1] - 92, p[0] + 92, p[1] + 92), fill=mix(PANEL, a), outline=mix(FG, a), width=4)
        text(d, p, name, F("Inter-Black.otf", 27), FG, a, "mm")
    for i, (w, l) in enumerate([("SCANNER", "PAPER"), ("PAPER", "STONE"), ("STONE", "SCANNER")]):
        a = ramp(t, 2.2 + i * 1.0, 0.6) * k
        arrow(d, pts[w], pts[l], MUTED, a, width=5, head=24, shrink=104)
        mx, my = (pts[w][0] + pts[l][0]) / 2, (pts[w][1] + pts[l][1]) / 2
        ox, oy = mx - cx, my - cy; n = math.hypot(ox, oy) or 1
        text(d, (mx + ox / n * 44, my + oy / n * 44), "beats", F("Inter-SemiBold.otf", 24), MUTED, a, "mm")
    items = [("Scanner", "hunts the enemy down"), ("Paper", "copies itself everywhere"), ("Stone", "bombs everything, fast")]
    for i, (h, s) in enumerate(items):
        a = ramp(t, 2.2 + i * 1.0, 0.6) * k
        text(d, (1040, 340 + i * 110), h, F("Inter-Bold.otf", 38), FG, a)
        text(d, (1040, 390 + i * 110), s, F("Inter-Medium.otf", 32), MUTED, a)
    if t > 6.0:
        a = ramp(t, 6.0, 0.8) * k
        panel(d, (1020, 720, 1800, 880), a, fill=ACC_L, outline=ACC)
        text(d, (1050, 758), "Every style can be beaten.", F("Inter-Bold.otf", 34), ACC, a)
        text(d, (1050, 813), "Winning takes real design, not one trick.", F("Inter-Medium.otf", 30), FG, a)
    return img

def bridge(question, active, sub=None):
    def scene(t, dur):
        img, d, k = base(t, dur, active)
        a = ramp(t, 0.2, 0.7) * k
        text(d, (W / 2, 480), question, F("InterDisplay-Black.otf", 76), FG, a, "mm")
        if sub:
            text(d, (W / 2, 580), sub, F("Inter-Medium.otf", 36), MUTED, ramp(t, 0.9, 0.7) * k, "mm")
        return img
    return scene

def s_tests(t, dur, kicker="3 · WHY IT WORKS"):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, kicker, "It tests what real engineers do", k)
    for i, s in enumerate(["Write code that works", "Test it well", "Prepare for opponents it cannot see", "Combine ideas, not polish one"]):
        a = ramp(t, 0.8 + i * 1.1, 0.6) * k
        tick(d, 130, 330 + i * 115, a)
        text(d, (200, 352 + i * 115), s, F("Inter-SemiBold.otf", 48), FG, a, "lm")
    if t > 6.0:
        text(d, (120, 860), "Like security code, or trading bots: software facing an opponent.", F("Inter-Medium.otf", 34), MUTED, ramp(t, 6.0, 0.8) * k)
    return img

def s_space(t, dur, kicker="3 · WHY IT WORKS"):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, kicker, "Can't the AI just try everything?", k)
    a = ramp(t, 0.8, 0.8) * k
    f = F("InterDisplay-Black.otf", 200)
    w = d.textlength("10", font=f) + 8 + d.textlength("140", font=F("InterDisplay-Black.otf", 96))
    x0 = (W - w) / 2
    text(d, (x0, 300), "10", f, FG, a)
    text(d, (x0 + d.textlength("10", font=f) + 8, 300), "140", F("InterDisplay-Black.otf", 96), FG, a)
    text(d, (W / 2, 590), "different 12-line programs exist.", F("Inter-SemiBold.otf", 42), FG, ramp(t, 1.6, 0.7) * k, "mm")
    text(d, (W / 2, 650), "That is far more than atoms in the universe (about 10⁸⁰).", F("Inter-Medium.otf", 34), MUTED, ramp(t, 2.6, 0.7) * k, "mm")
    if t > 4.4:
        aa = ramp(t, 4.4, 0.8) * k
        text(d, (W / 2, 800), "Trying them all is impossible.", F("InterDisplay-Black.otf", 60), RED, aa, "mm")
        text(d, (W / 2, 870), "A whole AI run tries at most a few hundred programs.", F("Inter-Medium.otf", 32), MUTED, ramp(t, 5.4, 0.7) * k, "mm")
    return img

def s_design(t, dur, kicker="3 · WHY IT WORKS"):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, kicker, "Running games is free. Good ideas are not.", k)
    pts = [("Practice is not the exam.", "It trains on 30 opponents, but 30 secret ones grade it."),
           ("No move is safe.", "Beating one opponent can mean losing to another.")]
    for i, (h, s) in enumerate(pts):
        a = ramp(t, 0.8 + i * 1.6, 0.7) * k
        y = 320 + i * 190
        panel(d, (120, y, 1800, y + 160), a, r=18)
        cross(d, 156, y + 34, a)
        text(d, (226, y + 56), h, F("Inter-Bold.otf", 42), FG, a, "lm")
        text(d, (226, y + 114), s, F("Inter-Medium.otf", 32), MUTED, a, "lm")
    if t > 4.6:
        text(d, (W / 2, 790), "What is missing is not computing power.", F("InterDisplay-Bold.otf", 46), FG, ramp(t, 4.6, 0.8) * k, "mm")
        text(d, (W / 2, 880), "It is good design.", F("InterDisplay-Black.otf", 76), ACC, ramp(t, 5.6, 0.8) * k, "mm")
    return img

# ---------------------------------------------------------------- findings
LEGEND = "Reward: the game score, rescaled.   0 = Dwarf, the textbook beginner's program   ·   1 = the human expert"

def result(legend=LEGEND, pace=1.0, dot_label=True, sub="these 5, and 22 from earlier versions of the test",
           title="The AI falls short of the human expert"):
    """`pace` < 1 plays the same reveal faster (the short pitch)."""
    def scene(t, dur):
        img, d, k = base(t, dur, {"gap"})
        head(d, t, "4 · WHAT WE FOUND", title, k)
        x0, x1 = 760, 1650
        a = ramp(t, 0.4) * k
        text(d, (120, 300), legend, F("Inter-SemiBold.otf", 28), MUTED, a)
        hbar(d, t, x0, x1, 375, 56, 0.0, DIM, 0.6 * pace, "Doing nothing", lambda g: "0.000", lab_col=MUTED)
        hbar(d, t, x0, x1, 640, 56, 1.0, GREEN, 1.6 * pace, "Human expert program", lambda g: f"{1.0 * g:.3f}")
        hbar(d, t, x0, x1, 480, 56, 0.713, RED, 3.0 * pace, "AI agent, 5 runs", lambda g: f"{0.713 * g:.3f}")
        text(d, (x0 - 28, 560), "Claude Opus 5.5", F("Inter-Medium.otf", 26), MUTED, ramp(t, 3.0 * pace) * k, "rm")
        if t > 4.6 * pace:
            da = ramp(t, 4.6 * pace) * k
            for v, dy in ((0.666, 0), (0.692, 0), (0.727, 0), (0.740, -11), (0.741, 11)):
                cx = x0 + (x1 - x0) * v
                d.ellipse((cx - 10, 547 + dy, cx + 10, 567 + dy), fill=mix(RED, da), outline=mix(BG, da), width=2)
            if dot_label:
                text(d, (x0 + (x1 - x0) * 0.713, 582), "each dot is one run", F("Inter-Medium.otf", 22), MUTED, da, "mt")
        t1 = max(6.0, 0.54 * dur) * pace
        if t > t1:
            aa = ramp(t, t1, 0.8) * k
            panel(d, (120, 760, 1800, 935), aa, fill=RED_L, outline=RED)
            text(d, (960, 822), "0 of 27 AI runs reached the human expert's score.", F("InterDisplay-Black.otf", 48), RED, aa, "mm")
            text(d, (960, 888), sub, F("Inter-SemiBold.otf", 28), FG, ramp(t, t1 + 0.8, 0.6) * k, "mm")
        return img
    return scene

s_result = result()

CLOCK_TOP = "An earlier version of the test had no clock. Time the AI chose to work, out of 45 minutes:"

def s_clock(t, dur, top=CLOCK_TOP, title="More time does not help", kicker="4 · WHAT WE FOUND"):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, kicker, title, k)
    x0, x1 = 620, 1700
    text(d, (120, 300), top, F("Inter-SemiBold.otf", 32), MUTED, ramp(t, 0.4) * k)
    hbar(d, t, x0, x1, 350, 50, 13.6 / 45, DIM, 1.0, "without a clock", lambda g: "4–14 min", 34, 36)
    hbar(d, t, x0, x1, 420, 50, 32.7 / 45, FG, 2.0, "with a clock", lambda g: "16–33 min", 34, 36)
    text(d, (120, 540), "Its score:", F("Inter-SemiBold.otf", 32), MUTED, ramp(t, 3.4) * k)
    hbar(d, t, x0, x1, 590, 50, 0.704, DIM, 3.6, "without a clock", lambda g: "0.704", 34, 36)
    hbar(d, t, x0, x1, 660, 50, 0.713, FG, 4.4, "with a clock", lambda g: "0.713", 34, 36)
    if t > 6.0:
        text(d, (960, 830), "3× more time.  Same score.", F("InterDisplay-Black.otf", 76), RED, ramp(t, 6.0, 0.7) * k, "mm")
    return img

def s_learned(t, dur):
    img, d, k = base(t, dur, {"diff", "gap"})
    head(d, t, "4 · WHAT WE FOUND", "Three ways the AI falls short", k)
    cards = [("It trusts the score", "it can see"), ("It polishes", "one idea"), ("It stops", "too early")]
    for i, (h1, h2) in enumerate(cards):
        t0 = 0.8 + i * 2.4
        a = ramp(t, t0, 0.7) * k
        x = 120 + i * 570
        panel(d, (x, 300, x + 540, 900), a, r=22)
        cross(d, x + 36, 330, a)
        text(d, (x + 36, 420), h1, F("Inter-Bold.otf", 40), FG, a)
        text(d, (x + 36, 470), h2, F("Inter-Bold.otf", 40), FG, a)
        if i == 0:
            mins = [0.4, 18.8, 21.1, 28.0, 30.5]
            vis = [0.390, 0.395, 0.418, 0.427, 0.437]; hid = [0.391, 0.387, 0.367, 0.365, 0.373]
            X = lambda m: x + 50 + 440 * m / 31; Y = lambda v: 760 - 180 * (v - 0.36) / 0.08
            n = max(2, int(1 + ramp(t, t0 + 0.4, 2.0) * 4))
            d.line([(X(m), Y(v)) for m, v in zip(mins[:n], vis[:n])], fill=mix(ACC, a), width=6)
            d.line([(X(m), Y(v)) for m, v in zip(mins[:n], hid[:n])], fill=mix(RED, a), width=6)
            text(d, (x + 36, 548), "run C1, minutes 0 to 30", F("Inter-Medium.otf", 24), MUTED, a)
            text(d, (x + 36, 800), "practice score: up", F("Inter-SemiBold.otf", 30), ACC, a)
            text(d, (x + 36, 842), "real score: down", F("Inter-SemiBold.otf", 30), RED, a)
        elif i == 1:
            text(d, (x + 36, 560), "It tunes one scanner:", F("Inter-SemiBold.otf", 30), FG, a)
            text(d, (x + 36, 605), "dozens of small variants.", F("Inter-SemiBold.otf", 30), FG, a)
            text(d, (x + 36, 680), "None of the 5 runs opens", F("Inter-SemiBold.otf", 30), FG, a)
            text(d, (x + 36, 725), "with a quick scan for", F("Inter-SemiBold.otf", 30), FG, a)
            text(d, (x + 36, 770), "the enemy.", F("Inter-SemiBold.otf", 30), FG, a)
            text(d, (x + 36, 830), "The expert program does.", F("Inter-SemiBold.otf", 30), GREEN, a)
        else:
            text(d, (x + 36, 600), "Up to 29 minutes", F("Inter-SemiBold.otf", 30), FG, a)
            text(d, (x + 36, 645), "left unused.", F("Inter-SemiBold.otf", 30), FG, a)
            text(d, (x + 36, 760), "“with about 22 minutes", F("Inter-MediumItalic.otf", 30), MUTED, a)
            text(d, (x + 36, 802), "left on the clock”", F("Inter-MediumItalic.otf", 30), MUTED, a)
    return img

CHEATS = ["Copy a known program", "Copy it, change the numbers", "Recall a secret opponent",
          "Crash the simulator", "Fake the score file", "Do nothing"]

def s_cheat(t, dur):
    img, d, k = base(t, dur, {"integ"})
    head(d, t, "5 · CAN THE SCORE BE TRUSTED?", "Cheating scores zero", k)
    cols, tw, th = 3, 540, 120
    for i, s in enumerate(CHEATS):
        r, c = divmod(i, cols)
        x, y = 120 + c * (tw + 30), 300 + r * (th + 26)
        a = ramp(t, 0.8 + i * 0.5, 0.5) * k
        panel(d, (x, y, x + tw, y + th), a, r=16)
        text(d, (x + 28, y + 40), s, F("Inter-SemiBold.otf", 30), FG, a, "lm")
        st = ramp(t, 1.1 + i * 0.5, 0.35) * k
        text(d, (x + 28, y + 88), "score 0.000", F("Inter-Black.otf", int(32 * (1 + 0.5 * (1 - st)))), RED, st, "lm")
    for i, s in enumerate(["34 cheats and shortcuts, run through the real scorer", "Copies and fakes score 0; shortcuts earn at most 0.24",
                           "Scoring runs in a separate, sealed box"]):
        a = ramp(t, 0.46 * dur + i * 0.12 * dur, 0.6) * k
        tick(d, 130, 640 + i * 90, a)
        text(d, (196, 662 + i * 90), s, F("Inter-SemiBold.otf", 38), FG, a, "lm")
    return img

TERM = [("$ harbor run -p harbor/corewar-hill -a oracle", "Mean: 1.000", TERM_GREEN, "the expert program"),
        ("$ harbor run -p harbor/corewar-hill -a nop", "Mean: 0.000", None, "doing nothing"),
        ("$ harbor run -p harbor/corewar-hill -a opencode -m anthropic/claude-opus-5-5 -k 5", "Mean: 0.713", TERM_RED, "the AI agent, 5 runs")]

def s_craft(t, dur):
    img, d, k = base(t, dur, {"craft"})
    head(d, t, "5 · CAN THE SCORE BE TRUSTED?", "Anyone can check it, with one command", k)
    a = ramp(t, 0.4) * k
    x, y0 = terminal(d, (120, 290, 1800, 700), a, "zsh — harbor")
    for i, (cmd, out, c, note) in enumerate(TERM):
        y = y0 + i * 118; t0 = 0.8 + i * 1.5
        if t < t0: continue
        n = int(clamp((t - t0) / 0.8) * (len(cmd) - 2))
        term_line(d, (x, y), cmd, a, 25, typed=n, cursor=t < t0 + 0.9)
        if t > t0 + 0.9:
            aa = ramp(t, t0 + 0.9, 0.4) * k
            term_line(d, (x, y + 46), f"{out}   # {note}", aa, 26, color=c)
    if t > 6.0:
        x = 120
        for i, s in enumerate(["Same program, same score, every time", "11 automated tests", "Every change is documented"]):
            aa = ramp(t, 6.0 + i * 0.4, 0.5) * k
            w = d.textlength(s, font=F("Inter-SemiBold.otf", 30)) + 60
            d.rounded_rectangle((x, 750, x + w, 818), 34, outline=mix(ACC, aa), width=3, fill=mix(ACC_L, aa))
            text(d, (x + w / 2, 784), s, F("Inter-SemiBold.otf", 30), ACC, aa, "mm")
            x += w + 24
    return img

def s_train(t, dur, title="A small AI can learn from the game, a little", punch="It learned the simplest trick. There is a lot left to learn.",
            intro="A small open model (Qwen2.5-Coder-7B) practised and kept its best attempts.", kicker="BONUS · TRAINING"):
    img, d, k = base(t, dur, {"tie"})
    head(d, t, kicker, title, k)
    text(d, (120, 290), intro, F("Inter-Medium.otf", 32), MUTED, ramp(t, 0.5) * k)
    def pair(x, title, before, after, maxv, fmt, t0):
        a = ramp(t, t0, 0.6) * k
        panel(d, (x, 360, x + 780, 760), a)
        text(d, (x + 40, 400), title, F("Inter-Bold.otf", 36), FG, a)
        for j, (lab, v, c) in enumerate((("before practice", before, DIM), ("after practice", after, ACC))):
            g = ramp(t, t0 + 0.5 + j * 0.8, 1.2); y = 490 + j * 125
            text(d, (x + 40, y), lab, F("Inter-Medium.otf", 30), MUTED, a)
            d.rounded_rectangle((x + 40, y + 44, x + 740, y + 86), 10, fill=mix(TRACK, a))
            wv = 700 * v / maxv * g
            if wv > 2: d.rounded_rectangle((x + 40, y + 44, x + 40 + wv, y + 86), 10, fill=mix(c, a))
            text(d, (x + 740, y), fmt(v * g if g < 1 else v), F("Inter-Black.otf", 36), FG if c == DIM else c, a, "ra")
    pair(120, "Programs that work", 24, 53, 64, lambda v: f"{v:.0f} out of 64", 0.8)
    pair(1020, "Average score", 0.000, 0.032, 0.06, lambda v: f"{v:.3f}", 2.4)
    if t > 5.6:
        text(d, (960, 860), punch, F("Inter-SemiBold.otf", 36), FG, ramp(t, 5.6, 0.7) * k, "mm")
    return img

def s_close(t, dur):
    img = core_bg(8 + t * 0.5, 0.6); d = ImageDraw.Draw(img, "RGBA"); k = fade(t, dur, 0.5, 1.0)
    d.rectangle((0, 210, W, 960), fill=BG + (int(238 * k),))
    a = ramp(t, 0.4, 0.8) * k
    text(d, (960, 320), "AI coding agents don't yet match", F("InterDisplay-Black.otf", 86), FG, a, "mm")
    text(d, (960, 420), "human experts.", F("InterDisplay-Black.otf", 86), FG, a, "mm")
    a2 = ramp(t, 1.8, 0.8) * k
    text(d, (700, 570), "0.713", F("InterDisplay-Black.otf", 120), RED, a2, "mm")
    text(d, (960, 575), "vs", F("Inter-Bold.otf", 52), MUTED, a2, "mm")
    text(d, (1220, 570), "1.000", F("InterDisplay-Black.otf", 120), GREEN, a2, "mm")
    text(d, (700, 650), "AI agent, average of 5 runs", F("Inter-SemiBold.otf", 30), RED, a2, "mm")
    text(d, (1220, 650), "human expert", F("Inter-SemiBold.otf", 30), GREEN, a2, "mm")
    a3 = ramp(t, 3.2, 0.8) * k
    text(d, (960, 745), "Try it:", F("Inter-SemiBold.otf", 30), MUTED, a3, "mm")
    x, y = terminal(d, (390, 775, 1530, 875), a3)
    term_line(d, (x, y), "$ harbor run -p harbor/corewar-hill -a opencode -m <your model>", a3, 25)
    return img


def question(steps):
    def scene(t, dur):
        img, d, k = base(t, dur, set())
        a = ramp(t, 0.3, 0.8) * k
        text(d, (W / 2, 250), "THE QUESTION", F("Inter-Bold.otf", 30), ACC, a, "mm")
        text(d, (W / 2, 370), "Can AI coding agents match", F("InterDisplay-Black.otf", 76), FG, a, "mm")
        text(d, (W / 2, 465), "human experts at real design work?", F("InterDisplay-Black.otf", 76), FG, a, "mm")
        text(d, (W / 2, 580), "Not a quiz, and not brute force: real design, against opponents it never sees.",
             F("Inter-Medium.otf", 36), MUTED, ramp(t, 1.8, 0.8) * k, "mm")
        fnt = F("Inter-Bold.otf", 30)
        widths = [66 + d.textlength(s_, font=fnt) for s_ in steps]
        gap = min(80, (1680 - sum(widths)) / (len(steps) - 1))
        x = (W - sum(widths) - (len(steps) - 1) * gap) / 2
        for i, s_ in enumerate(steps):
            aa = ramp(t, 3.0 + i * 0.6, 0.6) * k
            d.ellipse((x, 704, x + 52, 756), fill=mix(ACC, aa))
            text(d, (x + 26, 730), str(i + 1), F("Inter-Black.otf", 28), BG, aa, "mm")
            text(d, (x + 66, 730), s_, fnt, FG, aa, "lm")
            x += widths[i] + gap
        return img
    return scene

s_question = question(["The test we need", "The game", "Why it works", "What we found", "Can we trust it?"])


GOALS = [("Good design, not just compute", "Winning should take good ideas, not just more trial and error."),
         ("Beating opponents of every kind", "Every strategy has a counter, so no single trick wins."),
         ("Handling the unknown", "It is graded on opponents it has never seen."),
         ("Combining ideas", "The best answers mix several strategies, like an engineer would.")]

def s_goal(t, dur):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, "1 · THE TEST WE NEED", "What we want to measure", k)
    step = (0.58 * dur - 0.8) / (len(GOALS) - 1)
    for i, (h, sub) in enumerate(GOALS):
        a = ramp(t, 0.8 + i * step, 0.7) * k
        y = 310 + i * 150
        panel(d, (120, y, 1800, y + 128), a, fill=ACC_L if i == 0 else PANEL, outline=ACC if i == 0 else LINE, r=18)
        text(d, (160, y + 44), h, F("Inter-Bold.otf", 40), ACC if i == 0 else FG, a, "lm")
        text(d, (160, y + 96), sub, F("Inter-Medium.otf", 31), MUTED, a, "lm")
    return img

NEEDS = [("A real human level to compare with", "so that \u201cbelow human\u201d is a measured fact", {"gap"}),
         ("An exact score, not an opinion", "no human or AI judge deciding who did well", {"integ"}),
         ("Opponents the AI cannot see", "so practice is not the exam, like real software", {"diff"}),
         ("No tricks and no shortcuts", "every rule and tool given; copying does not pay", {"diff", "integ"})]

def s_need(t, dur):
    step = (0.70 * dur - 0.8) / (len(NEEDS) - 1)
    i_now = min(len(NEEDS) - 1, int(max(0, t - 0.8) // step))
    active = set().union(*[n[2] for n in NEEDS[: i_now + 1]]) if t > 0.8 else set()
    img, d, k = base(t, dur, active)
    head(d, t, "1 · THE TEST WE NEED", "And to measure it fairly, the test must have", k)
    for i, (h, sub, _) in enumerate(NEEDS):
        a = ramp(t, 0.8 + i * step, 0.6) * k
        y = 310 + i * 150
        panel(d, (120, y, 1800, y + 128), a, r=18)
        d.ellipse((150, y + 34, 210, y + 94), fill=mix(ACC, a))
        text(d, (180, y + 64), str(i + 1), F("Inter-Black.otf", 30), BG, a, "mm")
        text(d, (240, y + 44), h, F("Inter-Bold.otf", 38), FG, a, "lm")
        text(d, (240, y + 94), sub, F("Inter-Medium.otf", 30), MUTED, a, "lm")
    return img

FITS = [("A real human level", "30 years of expert programs; the one we compare to ranks #1 of 264", {"gap"}),
        ("An exact score", "the real simulator plays the games and counts the wins", {"integ"}),
        ("Opponents it cannot see", "it practises on 30 programs and is graded on 30 others", {"diff"}),
        ("No tricks, no shortcuts", "one page of rules, all documents, a clock; copies score zero", {"diff", "integ"})]

def s_fits(t, dur, kicker="3 · WHY IT WORKS"):
    step = (0.70 * dur - 0.8) / (len(FITS) - 1)
    i_now = min(len(FITS) - 1, int(max(0, t - 0.8) // step))
    img, d, k = base(t, dur, FITS[i_now][2] if t > 0.8 else set())
    head(d, t, kicker, "Core War has everything the test needs", k)
    for i, (h, sub, _) in enumerate(FITS):
        a = ramp(t, 0.8 + i * step, 0.6) * k
        y = 310 + i * 150
        cur = i == i_now
        panel(d, (120, y, 1800, y + 128), a, fill=ACC_L if cur else PANEL, outline=ACC if cur else LINE, r=18)
        tick(d, 152, y + 42, a)
        text(d, (230, y + 44), h, F("Inter-Bold.otf", 38), FG, a, "lm")
        text(d, (230, y + 94), sub, F("Inter-Medium.otf", 30), MUTED if not cur else FG, a, "lm")
    return img

def s_real(t, dur):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, "4 · WHAT WE FOUND", "Not just a game problem", k)
    text(d, (120, 300), "The same three mistakes show up in everyday AI coding work:", F("Inter-SemiBold.otf", 36), MUTED, ramp(t, 0.4, 0.7) * k)
    rows = [("It trusts the score it can see", "passes the tests it is shown, fails in real use"),
            ("It polishes one idea", "tunes one design instead of rethinking it"),
            ("It stops too early", "says “done” while there is still time to improve")]
    for i, (game, work) in enumerate(rows):
        t0 = 1.0 + i * (0.42 * dur - 1.0) / 2
        a = ramp(t, t0, 0.6) * k
        y = 380 + i * 150
        panel(d, (120, y, 860, y + 120), a, fill=RED_L, outline=RED, r=16)
        text(d, (150, y + 60), game, F("Inter-Bold.otf", 32), RED, a, "lm")
        a2 = ramp(t, t0 + 0.6, 0.6) * k
        arrow(d, (880, y + 60), (980, y + 60), MUTED, a2, width=6)
        panel(d, (1000, y, 1800, y + 120), a2, r=16)
        text(d, (1030, y + 60), work, F("Inter-SemiBold.otf", 32), FG, a2, "lm")
    if t > 0.66 * dur:
        text(d, (W / 2, 880), "Here, each one is measured against a real human level.", F("InterDisplay-Bold.otf", 44), ACC, ramp(t, 0.66 * dur, 0.7) * k, "mm")
    return img


SCENES = [("e01_title", s_title, 7.5), ("e02_question", s_question, 9.0), ("e02b_goal", s_goal, 10.0), ("e03_need", s_need, 11.5),
          ("e04_bridge", bridge("We found it in a game from 1984:", set(), "Core War, a game you play by writing programs."), 4.5),
          ("e05_game", s_game, 11.0), ("e06_player", s_player, 10.5), ("e07_lang", s_lang, 10.5),
          ("e08_rps", s_rps, 11.5),
          ("e09_bridge", bridge("So why does it work as a test?", set()), 3.8),
          ("e10_fits", s_fits, 12.0), ("e11_tests", s_tests, 10.0), ("e12_space", s_space, 9.5),
          ("e13_design", s_design, 10.0),
          ("e14_bridge", bridge("So how do the best AI agents do?", {"gap"}), 3.8),
          ("e15_result", s_result, 11.5), ("e16_clock", s_clock, 11.0),
          ("e17_bridge", bridge("Why do they fall short?", {"diff"}), 3.5),
          ("e18_learned", s_learned, 14.0), ("e19_real", s_real, 10.0),
          ("e20_bridge", bridge("Can the score be trusted?", {"integ", "craft"}), 3.5),
          ("e21_cheat", s_cheat, 10.0), ("e22_craft", s_craft, 10.5),
          ("e23_bridge", bridge("Last question: can an AI learn from this game?", {"tie"}), 3.8),
          ("e24_train", s_train, 10.5), ("e25_close", s_close, 10.0)]

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn, dur in SCENES:
        if what in ("all", name):
            render(name, fn, dur); print("rendered", name, flush=True)
