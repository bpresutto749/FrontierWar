"""The one chart behind both videos: every run's final program, practice score across, hidden-test
score up, with Toxic (the #1 human program) for reference. Read from results/models.json.
On the dashed line a program scores the same on new opponents as in practice; further right it is
stronger in practice. GPT-6.1 sol sits near the line but left of Toxic: its gap is already there in
practice. Claude Opus 5.5 sits further left, and two of its runs (C1, C5) fall well below the line."""
from style import F, FG, MUTED, RED, GREEN, LINE, mix, text, clamp, ease
import figures as N

AMBER = (245, 166, 35)
LO, HI = 0.365, 0.515                      # the same range on both axes, so the line is at 45 degrees


def _ramp(t, t0, d=0.5):
    return ease((t - t0) / d)


def dashed(d, p, q, col, a, width=3, dash=14, gap=10):
    (x0, y0), (x1, y1) = p, q
    n = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
    if n == 0: return
    ux, uy = (x1 - x0) / n, (y1 - y0) / n
    s = 0.0
    while s < n:
        e = min(n, s + dash)
        d.line((x0 + ux * s, y0 + uy * s, x0 + ux * e, y0 + uy * e), fill=mix(col, a), width=width)
        s += dash + gap


def scatter(d, t, k, box, at, labels=True):
    """box = (x0, y0, x1, y1) of the plot area. `at` = start times of: axes, toxic, gpt, gap, opus, drops
    (a missing key is never shown)."""
    x0, y0, x1, y1 = box
    X = lambda v: x0 + (x1 - x0) * (v - LO) / (HI - LO)
    Y = lambda v: y1 - (y1 - y0) * (v - LO) / (HI - LO)
    a = _ramp(t, at.get("axes", 0.0)) * k
    fs, fl = F("Inter-SemiBold.otf", 24), F("Inter-Bold.otf", 30)
    d.line((x0, y0, x0, y1), fill=mix(LINE, a), width=3)
    d.line((x0, y1, x1, y1), fill=mix(LINE, a), width=3)
    for v in (0.40, 0.45, 0.50):
        text(d, (X(v), y1 + 16), f"{v:.2f}", fs, MUTED, a, "mt")
        text(d, (x0 - 14, Y(v)), f"{v:.2f}", fs, MUTED, a, "rm")
        d.line((X(v), y1, X(v), y1 + 8), fill=mix(LINE, a), width=2)
        d.line((x0 - 8, Y(v), x0, Y(v)), fill=mix(LINE, a), width=2)
    text(d, ((x0 + x1) / 2, y1 + 50), "practice score  →", fl, FG, a, "mt")
    text(d, (x0 - 4, y0 - 34), "↑  hidden-test score", fl, FG, a, "lb")
    dashed(d, (X(LO), Y(LO)), (X(HI), Y(HI)), MUTED, a * 0.9)
    if labels:
        text(d, (X(HI) + 14, Y(HI) + 4), "same score as in practice", F("Inter-SemiBold.otf", 24), MUTED, a, "lm")

    if "toxic" in at:
        ta = _ramp(t, at["toxic"]) * k
        tx, ty = X(N.REF["practice"]), Y(N.REF["hill"])
        dashed(d, (tx, ty + 18), (tx, y1), GREEN, ta * 0.7, width=2, dash=8, gap=8)
        d.ellipse((tx - 15, ty - 15, tx + 15, ty + 15), fill=mix(GREEN, ta), outline=mix(FG, ta), width=2)
        text(d, (tx + 26, ty), "Toxic", F("Inter-Black.otf", 32), GREEN, ta, "lm")

    def dots(runs, col, t0):
        da = _ramp(t, t0) * k
        for i, r in enumerate(runs):
            ai = _ramp(t, t0 + i * 0.12) * k
            cx, cy = X(r["practice"]), Y(r["hill"])
            d.ellipse((cx - 11, cy - 11, cx + 11, cy + 11), fill=mix(col, ai), outline=mix((13, 17, 23), ai), width=2)
        return da

    if "gpt" in at:
        ga = dots(N.GPT, AMBER, at["gpt"])
        text(d, (X(0.441), Y(0.462)), "GPT-6.1 sol", F("Inter-Black.otf", 32), AMBER, ga, "rm")
    if "gap" in at:
        pa = _ramp(t, at["gap"], 0.8) * k
        y = Y(0.501)
        xa, xb = X(max(r["practice"] for r in N.GPT)), X(N.REF["practice"]) - 6
        g = clamp((t - at["gap"]) / 0.8)
        xe = xa + (xb - xa) * ease(g)
        d.line((xa, y, xe, y), fill=mix(FG, pa), width=4)
        d.line((xa, y - 12, xa, y + 12), fill=mix(FG, pa), width=4)
        if g >= 1: d.line((xb, y - 12, xb, y + 12), fill=mix(FG, pa), width=4)
        text(d, (xb + 4, y - 22), "behind Toxic, even in practice", F("Inter-Bold.otf", 24), FG, pa, "rb")
        g1 = max(N.GPT, key=lambda r: r["practice"])
        dashed(d, (xa, y + 14), (xa, Y(g1["hill"]) - 16), AMBER, pa * 0.8, width=2, dash=6, gap=6)
    if "opus" in at:
        oa = dots(N.OPUS, RED, at["opus"])
        text(d, (X(0.367), Y(0.437)), "Claude Opus 5.5", F("Inter-Black.otf", 32), RED, oa, "lm")
    if "drops" in at:
        ra = _ramp(t, at["drops"]) * k
        for r in N.OVERFIT:
            px = X(r["practice"])
            dashed(d, (px, Y(r["practice"]) + 6), (px, Y(r["hill"]) - 14), RED, ra, width=3, dash=6, gap=6)
            text(d, (px + 16, Y(r["hill"])), r["label"], F("Inter-Bold.otf", 24), RED, ra, "lm")
        c5 = next(r for r in N.OVERFIT if r["label"] == "C5")
        text(d, (X(c5["practice"]) + 16, Y(c5["hill"]) + 34), "fitted to practice", F("Inter-Bold.otf", 24), RED, ra, "lm")
    return X, Y


# ---------------------------------------------------------------- the answer, as a table
# The question asks two things: turn practice into a winning design, and make it hold up on opponents
# never seen (not be fooled by practice). The answer: each agent misses the design, the traps of
# practice, or both. GPT-6.1 sol: no winning design, no traps. Claude Opus 5.5: both.
COLS = ("Find a winning design", "Escape the traps of practice")
ROWS = (("Claude Opus 5.5", RED, (False, False)), ("GPT-6.1 sol", AMBER, (False, True)))


def mark(d, x, y, ok, a, r=24):
    from style import BG
    col = GREEN if ok else RED
    d.ellipse((x - r, y - r, x + r, y + r), fill=mix(col, a))
    if ok:
        d.line((x - r * 0.45, y + r * 0.02, x - r * 0.1, y + r * 0.38, x + r * 0.5, y - r * 0.35), fill=mix(BG, a), width=6, joint="curve")
    else:
        q = r * 0.42
        d.line((x - q, y - q, x + q, y + q), fill=mix(BG, a), width=6); d.line((x - q, y + q, x + q, y - q), fill=mix(BG, a), width=6)


def answer_table(d, t, k, box, at, lit=None, size=36, hsize=None, traps_first=False):
    """box = (x0, y0, x1, y1). `at`: start times of head (columns and row names) and of each mark:
    'opus' (both of Opus's), 'gpt_design', 'gpt_traps'. lit = 'design' or 'traps' dims the other column."""
    from style import PANEL, ACC, ACC_L
    x0, y0, x1, y1 = box
    cols, keys = (COLS[::-1], ("traps", "design")) if traps_first else (COLS, ("design", "traps"))
    rows = [(n, c, oks[::-1] if traps_first else oks) for n, c, oks in ROWS]
    gkeys = ("gpt_traps", "gpt_design") if traps_first else ("gpt_design", "gpt_traps")
    xn = x0 + (x1 - x0) * 0.30                       # end of the name column
    cx = [xn + (x1 - xn) * 0.25, xn + (x1 - xn) * 0.75]
    rh = (y1 - y0) / 3
    ah = _ramp(t, at.get("head", 0.0)) * k
    for j, c in enumerate(cols):
        on = lit in (None, keys[j])
        if lit == keys[j]:
            d.rounded_rectangle((cx[j] - (x1 - xn) * 0.24, y0, cx[j] + (x1 - xn) * 0.24, y1), 18, fill=mix(ACC_L, ah), outline=mix(ACC, ah), width=3)
        text(d, (cx[j], y0 + rh / 2), c, F("Inter-Bold.otf", hsize or size), FG, ah * (1 if on else 0.4), "mm")
    for i, (name, col, oks) in enumerate(rows):
        y = y0 + rh * (i + 1.5)
        d.line((x0, y - rh / 2, x1, y - rh / 2), fill=mix(LINE, ah), width=2)
        text(d, (x0 + 10, y), name, F("Inter-Black.otf", size + 4), col, ah, "lm")
        for j, ok in enumerate(oks):
            key = "opus" if i == 0 else gkeys[j]
            if key not in at: continue
            on = lit in (None, keys[j])
            mark(d, cx[j], y, ok, _ramp(t, at[key], 0.4) * k * (1 if on else 0.4), r=int(size * 0.75))
