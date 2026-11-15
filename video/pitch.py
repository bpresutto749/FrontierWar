#!/usr/bin/env python3
"""The pitch (1 min 59): the whole argument in eleven scenes.
The test we want, the game, the test, what we found (the gap, one run, one game, three everyday
mistakes), why the score can be trusted, and the close. One idea per scene, few words per scene.
Every number is the same as in the full video and comes from the repository.
usage: python video/pitch.py [all | <scene name>]   -> video/build/<scene>.mp4"""
import math, sys
from PIL import Image, ImageDraw
from style import (W, H, F, M, BG, PANEL, LINE, FG, MUTED, DIM, TRACK, RED, GREEN, RED_L, GREEN_L, ACC, ACC_L, BLUE, terminal, term_line,
                   clamp, ramp, mix, fade, text, panel, arrow, tick, cross, rail, render, base, head, core_bg)
import explainer as ex
import demo as dm

BLUE_T = (60, 84, 150)

# ---------------------------------------------------------------- 1 the test we want
def s_title(t, dur):
    img = core_bg(1.2 + t * 0.9, 0.9); d = ImageDraw.Draw(img, "RGBA"); k = fade(t, dur, 0.3, 0.5)
    d.rectangle((0, 300, W, 790), fill=(255, 255, 255, int(235 * k)))
    text(d, (W / 2, 450), "CORE WAR ARENA", F("InterDisplay-Black.otf", 156), FG, ramp(t, 0.2, 0.5) * k, "mm")
    text(d, (W / 2, 600), "Can AI coding agents beat human experts", F("Inter-Bold.otf", 52), FG, ramp(t, 0.6, 0.5) * k, "mm")
    text(d, (W / 2, 665), "at a classic programming game?", F("Inter-Bold.otf", 52), ACC, ramp(t, 0.8, 0.5) * k, "mm")
    text(d, (W / 2, 745), "Break the Agent  ·  AfterQuery  ·  Junction 2026", F("Inter-Medium.otf", 30), MUTED, ramp(t, 1.2, 0.5) * k, "mm")
    return img

WANT = [("Good ideas win, not brute force", {"diff"}),
        ("Opponents it has never seen", {"diff"}),
        ("An exact score, against a real human expert", {"gap", "integ"})]

def s_want(t, dur):
    step = 1.8
    shown = [w for i, w in enumerate(WANT) if t > 0.8 + i * step]
    img, d, k = base(t, dur, set().union(*[w[1] for w in shown]) if shown else set())
    head(d, t, "1 · THE TEST WE WANT", "A test of design, not compute", k)
    for i, (h, _) in enumerate(WANT):
        a = ramp(t, 0.8 + i * step, 0.6) * k
        y = 320 + i * 190
        panel(d, (120, y, 1800, y + 150), a, r=20)
        tick(d, 164, y + 53, a)
        text(d, (244, y + 75), h, F("Inter-Bold.otf", 50), FG, a, "lm")
    return img

# ---------------------------------------------------------------- 2 the game
def s_game(t, dur):
    img, d, k = base(t, dur, set())
    head(d, t, "2 · THE GAME: CORE WAR, 1984", "A game where programs fight", k)
    for s, y, g in (("Two programs share", 330, 0), ("one computer memory.", 392, 0), ("Each tries to crash", 484, 1), ("the other.", 546, 1)):
        text(d, (120, y), s, F("Inter-SemiBold.otf", 48), FG, ramp(t, 0.8 + g * 1.7, 0.6) * k)
    if t > 4.2:
        aa = ramp(t, 4.2, 0.6) * k
        text(d, (120, 680), "You don't play it.", F("InterDisplay-Black.otf", 56), ACC, aa)
        text(d, (120, 752), "You write the player.", F("InterDisplay-Black.otf", 56), ACC, aa)
    pa = ramp(t, 0.5, 0.7) * k
    if pa > 0:
        core = core_bg(0.5 + t * 0.6, 1.0).resize((820, 462), Image.BILINEAR)
        img.paste(core, (980, 330), Image.new("L", core.size, int(255 * pa)))
        d.rounded_rectangle((976, 326, 1804, 796), 14, outline=mix(LINE, pa), width=3)
        for j, (c, lab) in enumerate(((RED, "program A"), (BLUE, "program B"))):
            d.rounded_rectangle((980 + j * 240, 824, 1004 + j * 240, 848), 5, fill=mix(c, pa))
            text(d, (1016 + j * 240, 836), lab, F("Inter-SemiBold.otf", 26), FG, pa, "lm")
    return img

def s_hard(t, dur):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, "2 · THE GAME: CORE WAR, 1984", "No perfect program, no brute force", k)
    cx, cy, R = 520, 560, 190
    pts = {"SCANNER": (cx, cy - R), "PAPER": (cx + R * 0.95, cy + R * 0.55), "STONE": (cx - R * 0.95, cy + R * 0.55)}
    a = ramp(t, 0.6, 0.6) * k
    for name, p in pts.items():
        d.ellipse((p[0] - 86, p[1] - 86, p[0] + 86, p[1] + 86), fill=mix(PANEL, a), outline=mix(FG, a), width=4)
        text(d, p, name, F("Inter-Black.otf", 24), FG, a, "mm")
    for i, (w, l) in enumerate([("SCANNER", "PAPER"), ("PAPER", "STONE"), ("STONE", "SCANNER")]):
        aa = ramp(t, 1.0 + i * 0.3, 0.5) * k
        arrow(d, pts[w], pts[l], MUTED, aa, width=5, head=24, shrink=98)
        mx, my = (pts[w][0] + pts[l][0]) / 2, (pts[w][1] + pts[l][1]) / 2
        ox, oy = mx - cx, my - cy; n = math.hypot(ox, oy) or 1
        text(d, (mx + ox / n * 46, my + oy / n * 40), "beats", F("Inter-SemiBold.otf", 24), MUTED, aa, "mm")
    text(d, (cx, 826), "Every style can be beaten.", F("Inter-Bold.otf", 36), FG, ramp(t, 2.0, 0.6) * k, "mm")
    d.line((950, 330, 950, 840), fill=mix(LINE, a), width=2)
    if t > 3.2:
        aa = ramp(t, 3.2, 0.6) * k
        f1, f2 = F("InterDisplay-Black.otf", 170), F("InterDisplay-Black.otf", 82)
        w = d.textlength("10", font=f1) + 8 + d.textlength("140", font=f2)
        x0 = 1375 - w / 2
        text(d, (x0, 340), "10", f1, FG, aa)
        text(d, (x0 + d.textlength("10", font=f1) + 8, 340), "140", f2, FG, aa)
        text(d, (1375, 580), "possible 12-line programs.", F("Inter-SemiBold.otf", 38), FG, aa, "mm")
        text(d, (1375, 640), "An AI run tries at most a few hundred.", F("Inter-Medium.otf", 34), MUTED, ramp(t, 4.4, 0.6) * k, "mm")
    if t > 5.8:
        text(d, (W / 2, 912), "What wins is good design, not compute.", F("InterDisplay-Black.otf", 54), ACC, ramp(t, 5.8, 0.6) * k, "mm")
    return img

# ---------------------------------------------------------------- 3 the test
def s_test(t, dur):
    img, d, k = base(t, dur, {"diff", "integ"})
    head(d, t, "3 · THE TEST", "One program, 30 secret opponents", k)
    a1 = ramp(t, 0.6, 0.6) * k
    panel(d, (120, 316, 500, 452), a1, fill=RED_L, outline=RED, r=18)
    text(d, (310, 384), "the AI's program", F("Inter-Bold.otf", 34), RED, a1, "mm")
    a2 = ramp(t, 1.1, 0.6) * k
    arrow(d, (520, 384), (640, 384), MUTED, a2, width=6)
    text(d, (578, 344), "plays", F("Inter-SemiBold.otf", 24), MUTED, a2, "mm")
    for i in range(30):
        r, c = divmod(i, 10)
        x, y = 670 + c * 113, 312 + r * 50
        aa = ramp(t, 1.3 + i * 0.03, 0.4) * k
        d.rounded_rectangle((x, y, x + 100, y + 42), 10, fill=mix((222, 229, 244), aa), outline=mix((90, 112, 170), aa), width=2)
        text(d, (x + 50, y + 21), "?", F("Inter-Bold.otf", 22), (90, 112, 170), aa, "mm")
    text(d, (1228, 492), "500 games against each of them", F("Inter-Bold.otf", 28), BLUE_T, ramp(t, 2.2) * k, "mm")
    rows = [(3.6, "The AI gets 45 minutes and 30 practice opponents, never the secret ones.", FG, PANEL, LINE),
            (6.6, "A human expert's program takes the same test: Toxic, rated #1 of 264.", GREEN, GREEN_L, GREEN),
            (9.4, "Reward:   0 = the textbook beginner's program   ·   1 = the human expert", FG, ACC_L, ACC)]
    for i, (t0, s, col, fill, line) in enumerate(rows):
        if t > t0:
            aa = ramp(t, t0, 0.6) * k
            y = 560 + i * 120
            panel(d, (120, y, 1800, y + 96), aa, fill=fill, outline=line, r=18)
            text(d, (160, y + 48), s, F("Inter-Bold.otf", 36), col, aa, "lm")
    return img

# ---------------------------------------------------------------- 4 what we found
s_result = ex.result(legend="", pace=0.78, dot_label=False, sub="these 5, and 22 on earlier versions")       # the reward was defined in the scene just before

def s_run(t, dur):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, "4 · WHAT WE FOUND", "One run: practice is not the test", k)
    a = ramp(t, 0.3) * k
    m = 16.5 * clamp((t - 0.8) / 3.6)
    panel(d, (120, 290, 1000, 945), a, r=18)
    text(d, (160, 330), "run C5: its practice scores", F("Inter-Bold.otf", 26), FG, a, "lm")
    text(d, (960, 330), f"minute {m:4.1f} of 45", M(24, True), MUTED, a, "rm")
    dm.practice_chart(d, a, m, (160, 400, 950, 860), caption=False)
    if t > 4.8:
        aa = ramp(t, 4.8, 0.6) * k
        panel(d, (1060, 290, 1800, 420), aa, fill=RED_L, outline=RED, r=18)
        text(d, (1090, 332), "It stops at minute 16.5,", F("Inter-Bold.otf", 32), RED, aa, "lm")
        text(d, (1090, 378), "with 28.5 of its 45 minutes left.", F("Inter-Bold.otf", 32), RED, aa, "lm")
    c1, c2 = 1510, 1690
    if t > 6.6:
        aa = ramp(t, 6.6, 0.6) * k
        text(d, (c1, 490), "the AI", F("Inter-Bold.otf", 28), RED, aa, "mm")
        text(d, (c2, 490), "the expert", F("Inter-Bold.otf", 28), GREEN, aa, "mm")
    for i, (t0, lab, va, ve, fill, line) in enumerate(((6.6, "In practice", "0.489", "0.507", PANEL, LINE),
                                                       (8.4, "In the real test", "0.398", "0.487", RED_L, RED))):
        if t > t0:
            aa = ramp(t, t0, 0.6) * k
            y = 525 + i * 150
            panel(d, (1060, y, 1800, y + 124), aa, fill=fill, outline=line, r=18)
            text(d, (1090, y + 62), lab, F("Inter-Bold.otf", 34), FG, aa, "lm")
            text(d, (c1, y + 62), va, F("InterDisplay-Black.otf", 46), RED, aa, "mm")
            text(d, (c2, y + 62), ve, F("InterDisplay-Black.otf", 46), GREEN, aa, "mm")
    return img

T0, SLOW, FAST = 2.0, 5.4, 2.4          # the game: a still, 60 steps slowly, then fast-forward

def s_fight(t, dur):
    img, d, k = base(t, dur, {"diff"})
    head(d, t, "4 · WHAT WE FOUND", "One game of the real test", k)
    (sa, _), (sb, _) = dm.fights()
    last = sa[-1][0]
    c = 0 if t < T0 else 60 * (t - T0) / SLOW if t < T0 + SLOW else 60 + (last - 60) * clamp((t - T0 - SLOW) / FAST)
    a = ramp(t, 0.3) * k
    gy = 318
    for x, snaps, light, dark, label, win in ((170, sa, dm.RED_C, RED, "the AI's program", False),
                                              (1050, sb, dm.GREEN_C, GREEN, "the expert's program", True)):
        cyc, owner, pa, pb, na, nb = dm.pick(snaps, c)
        g = dm.grid(owner, pa, pb, light, dark)
        img.paste(g, (x, gy), Image.new("L", g.size, int(255 * a)))
        d = ImageDraw.Draw(img, "RGBA")
        text(d, (x, 306), label, F("Inter-Bold.otf", 28), dark, a, "ls")
        end = snaps[-1][0]
        if t >= T0 and c >= end:
            t_end = T0 + (SLOW * end / 60 if end <= 60 else SLOW + FAST * (end - 60) / (last - 60))
            aa = ramp(t, t_end, 0.4) * k
            d.rounded_rectangle((x + 110, 500, x + 590, 590), 20, fill=mix((255, 255, 255), aa), outline=mix(dark, aa), width=4)
            text(d, (x + 350, 545), f"wins at step {end:,}" if win else f"loses at step {end:,}", F("InterDisplay-Black.otf", 38), dark, aa, "mm")
    text(d, (1750, 266), f"step {int(min(c, last)):,}", F("Inter-Bold.otf", 26), FG, a, "rm")
    text(d, (170, 266), "blue: the same secret opponent", F("Inter-SemiBold.otf", 24), BLUE_T, a, "lm")
    if t < T0 + SLOW + 0.3:
        text(d, (W / 2, 946), "The expert finds the opponent fast: it wins in 41 steps.", F("Inter-Bold.otf", 30), GREEN, ramp(t, 0.8, 0.5) * k, "mm")
    else:
        text(d, (W / 2, 946), "The AI's program fights on, and loses.", F("Inter-Bold.otf", 30), RED, ramp(t, T0 + SLOW + 0.3, 0.4) * k, "mm")
    return img

WHY = [("Trusts the score it can see", "", "passes the shown tests, fails in real use"),
       ("Skips the experts' opening move", "0 of 5 runs use it", "polishes one idea instead of rethinking it"),
       ("Stops too early", "12 to 29 minutes unused", "says “done” while there is still time to improve")]

def s_why(t, dur):
    img, d, k = base(t, dur, {"gap", "diff"})
    head(d, t, "4 · WHAT WE FOUND", "Three everyday coding mistakes", k)
    step = 3.5
    for i, (game, proof, work) in enumerate(WHY):
        t0 = 0.8 + i * step
        a = ramp(t, t0, 0.6) * k
        y = 310 + i * 205
        panel(d, (120, y, 880, y + 170), a, fill=RED_L, outline=RED, r=18)
        text(d, (154, y + (62 if proof else 85)), game, F("Inter-Bold.otf", 36), RED, a, "lm")
        if proof: text(d, (154, y + 116), proof, F("Inter-SemiBold.otf", 28), FG, a, "lm")
        a2 = ramp(t, t0 + 0.9, 0.6) * k
        arrow(d, (900, y + 85), (990, y + 85), MUTED, a2, width=6)
        panel(d, (1010, y, 1800, y + 170), a2, r=18)
        text(d, (1044, y + 85), work, F("Inter-SemiBold.otf", 32), FG, a2, "lm")
    return img

# ---------------------------------------------------------------- 5 trust, and the close
def s_trust(t, dur):
    img, d, k = base(t, dur, {"integ", "craft"})
    head(d, t, "5 · CAN THE SCORE BE TRUSTED?", "Cheating scores zero", k)
    for i, s in enumerate(["Copy a published program", "Fake the score file"]):
        x = 120 + i * 855
        a = ramp(t, 0.7 + i * 0.6, 0.5) * k
        panel(d, (x, 300, x + 825, 440), a, r=16)
        text(d, (x + 30, 345), s, F("Inter-SemiBold.otf", 32), FG, a, "lm")
        text(d, (x + 30, 399), "score 0.000", F("Inter-Black.otf", 34), RED, ramp(t, 1.0 + i * 0.6, 0.4) * k, "lm")
    for i, s in enumerate(["34 cheats and shortcuts tested: at most 0.24", "Scored in a separate, sealed box",
                           "Reproducible with one command"]):
        a = ramp(t, 2.8 + i * 1.5, 0.6) * k
        tick(d, 130, 548 + i * 122, a)
        text(d, (204, 570 + i * 122), s, F("Inter-SemiBold.otf", 46), FG, a, "lm")
    return img

def s_close(t, dur):
    img = core_bg(8 + t * 0.5, 0.6); d = ImageDraw.Draw(img, "RGBA"); k = fade(t, dur, 0.5, 1.0)
    d.rectangle((0, 190, W, 960), fill=(255, 255, 255, int(238 * k)))
    a = ramp(t, 0.4, 0.7) * k
    text(d, (960, 290), "AI coding agents don't yet match", F("InterDisplay-Black.otf", 86), FG, a, "mm")
    text(d, (960, 390), "human experts.", F("InterDisplay-Black.otf", 86), FG, a, "mm")
    a2 = ramp(t, 1.8, 0.7) * k
    text(d, (700, 535), "0.713", F("InterDisplay-Black.otf", 120), RED, a2, "mm")
    text(d, (960, 540), "vs", F("Inter-Bold.otf", 52), MUTED, a2, "mm")
    text(d, (1220, 535), "1.000", F("InterDisplay-Black.otf", 120), GREEN, a2, "mm")
    text(d, (700, 615), "AI agent, average of 5 runs", F("Inter-SemiBold.otf", 30), RED, a2, "mm")
    text(d, (1220, 615), "human expert", F("Inter-SemiBold.otf", 30), GREEN, a2, "mm")
    text(d, (960, 720), "Bonus: a small open model learns from it, a little (reward 0.000 → 0.032).", F("Inter-SemiBold.otf", 34), FG,
         ramp(t, 3.6, 0.7) * k, "mm")
    a3 = ramp(t, 5.4, 0.7) * k
    text(d, (960, 790), "Try it:", F("Inter-SemiBold.otf", 30), MUTED, a3, "mm")
    x, y = terminal(d, (390, 820, 1530, 920), a3)
    term_line(d, (x, y), "$ harbor run -p harbor/corewar-hill -a opencode -m <your model>", a3, 25)
    return img

SCENES = [("s01_title", s_title, 5.5), ("s02_want", s_want, 8.5),
          ("s03_game", s_game, 10.0), ("s04_hard", s_hard, 10.5),
          ("s05_test", s_test, 14.0),
          ("s06_result", s_result, 11.0), ("s07_run", s_run, 12.5), ("s08_fight", s_fight, 12.0), ("s09_why", s_why, 14.5),
          ("s10_trust", s_trust, 10.5), ("s11_close", s_close, 10.0)]
assert abs(sum(s[2] for s in SCENES) - 119.0) < 1e-6                    # 1 min 59

if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn, dur in SCENES:
        if what in ("all", name):
            render(name, fn, dur); print("rendered", name, flush=True)
