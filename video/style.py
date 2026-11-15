#!/usr/bin/env python3
"""Shared drawing helpers for all the videos: palette, fonts, easing, anti-aliased shapes, panels,
the judging-criteria rail, the animated memory background, and render() (frames piped to ffmpeg,
one mp4 per scene)."""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # repository root
OUT = os.environ.get("VIDEO_BUILD", os.path.join(ROOT, "video", "build"))     # one mp4 per scene
os.makedirs(OUT, exist_ok=True)
FD = os.environ.get("INTER_DIR", "/usr/share/fonts/opentype/inter/")       # Inter + Inter Display (fonts-inter)
def F(name, size): return ImageFont.truetype(FD + name, size)
def M(size, bold=False):
    return ImageFont.truetype(os.environ.get("MONO_PREFIX", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono") + ("-Bold" if bold else "") + ".ttf", size)

BG = (255, 255, 255); PANEL = (246, 247, 249); LINE = (226, 229, 234)
FG = (17, 24, 39); MUTED = (100, 108, 122); DIM = (205, 210, 217); TRACK = (236, 238, 242)
RED = (220, 38, 38); GREEN = (22, 150, 70); RED_L = (254, 226, 226); GREEN_L = (220, 245, 228)
ACC = (37, 99, 235); ACC_L = (232, 240, 254); BLUE = (60, 90, 170)
# colours of particular elements (cards, terminal panels, the secret opponents, memory cells, the background animation)
CARD = (255, 255, 255); CODE_BG = (250, 250, 251); LOSS = (120, 128, 140); RUN_BAR = (236, 120, 120)
OPP_FILL = (222, 229, 244); OPP_LINE = (90, 112, 170); BLUE_T = (60, 84, 150)
CELL_EMPTY = (236, 238, 242); CELL_GAP = (255, 255, 255)
RED_C = (248, 185, 185); GREEN_C = (180, 226, 196); BLUE_C = (205, 214, 236)      # memory written by AI / expert / opponent
CORE_BASE = (238, 240, 243); CORE_A = (247, 178, 178); CORE_B = (198, 210, 238)

# VIDEO_THEME=dark (set by demo_full.py before it imports anything): the same scenes in an app-like dark theme
THEME = os.environ.get("VIDEO_THEME", "light")
if THEME == "dark":
    BG = (13, 17, 23); PANEL = (22, 27, 34); LINE = (48, 54, 61)
    FG = (230, 237, 243); MUTED = (139, 148, 158); DIM = (66, 74, 84); TRACK = (33, 38, 45)
    RED = (248, 81, 73); GREEN = (63, 185, 80); RED_L = (56, 23, 26); GREEN_L = (16, 44, 27)
    ACC = (88, 166, 255); ACC_L = (15, 34, 62); BLUE = (121, 170, 255)
    CARD = (22, 27, 34); CODE_BG = (8, 11, 16); LOSS = (110, 118, 129); RUN_BAR = (150, 62, 60)
    OPP_FILL = (24, 34, 56); OPP_LINE = (88, 124, 200); BLUE_T = (140, 180, 255)
    CELL_EMPTY = (27, 32, 40); CELL_GAP = BG
    RED_C = (104, 40, 42); GREEN_C = (26, 84, 47); BLUE_C = (36, 56, 94)
    CORE_BASE = (24, 29, 37); CORE_A = (96, 38, 40); CORE_B = (35, 56, 96)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def ramp(t, t0, dur=0.5): return ease((t - t0) / dur)
def mix(c, a): return tuple(int(v) for v in c) + (int(255 * clamp(a)),)
def fade(t, dur, fin=0.35, fout=0.35): return clamp(min(t / fin, (dur - t) / fout))
def text(d, xy, s, font, fill, a=1.0, anchor="la"): d.text(xy, s, font=font, fill=mix(fill, a), anchor=anchor)

# ---------------------------------------------------------------- anti-aliased shapes
# Pillow anti-aliases text but not shapes. ImageDraw.Draw is replaced below by a drawer whose ellipses,
# rounded rectangles, polygons and slanted lines come from 4x supersampled masks (cached by geometry),
# so circles, arrows and chart lines have smooth edges. Axis-aligned lines and rectangles are unchanged.
# The same drawer makes text honour its alpha, so that text fades in and out with the shapes around it.
SS = 4
_MASKS = {}
_LUT = [[v * a // 255 for v in range(256)] for a in range(256)]

def _cached(key, build):
    m = _MASKS.get(key)
    if m is None:
        if len(_MASKS) > 3000: _MASKS.clear()
        m = _MASKS[key] = build()
    return m

def _ss(key, w, h, paint):
    def build():
        big = Image.new("L", (w * SS, h * SS), 0)
        paint(ImageDraw.ImageDraw(big))
        return big.reduce(SS)
    return _cached(key, build)

def _box(xy):
    if len(xy) == 2: (x0, y0), (x1, y1) = xy
    else: x0, y0, x1, y1 = xy
    X0, Y0 = round(x0), round(y0)
    return X0, Y0, round(x1) - X0 + 1, round(y1) - Y0 + 1

def _pts(xy):
    xy = list(xy)
    return [tuple(p) for p in xy] if isinstance(xy[0], (tuple, list)) else list(zip(xy[0::2], xy[1::2]))

def _rr(w, h, r):
    def build():
        m = Image.new("L", (w, h), 255)
        if r > 0:
            c = _ss(("c", r), 2 * r, 2 * r, lambda g: g.ellipse((0, 0, 2 * r * SS - 1, 2 * r * SS - 1), fill=255))
            for sx, dx in ((0, 0), (r, w - r)):
                for sy, dy in ((0, 0), (r, h - r)):
                    m.paste(c.crop((sx, sy, sx + r, sy + r)), (dx, dy))
        return m
    return _cached(("rr", w, h, r), build)

def _rr_ring(w, h, r, width):
    def build():
        outer = _rr(w, h, r)
        if w <= 2 * width or h <= 2 * width: return outer
        inner = Image.new("L", (w, h), 0)
        inner.paste(_rr(w - 2 * width, h - 2 * width, max(0, r - width)), (width, width))
        return ImageChops.subtract(outer, inner)
    return _cached(("ring", w, h, r, width), build)

class AADraw(ImageDraw.ImageDraw):
    def __init__(self, im, mode=None):
        super().__init__(im, mode); self._target = im

    def _put(self, m, x, y, color):
        a = color[3] if len(color) > 3 else 255
        if a <= 0: return
        if a < 255: m = m.point(_LUT[a])
        self._target.paste(tuple(color[:3]), (x, y), m)

    def text(self, xy, text, fill=None, font=None, anchor=None, **kw):
        # Pillow draws text opaque whatever the fill's alpha, so a fading text is drawn as a mask
        # and pasted through it like the shapes.
        a = fill[3] if fill is not None and len(fill) > 3 else 255
        if a >= 255: return super().text(xy, text, fill=fill, font=font, anchor=anchor, **kw)
        if a <= 0: return
        x0, y0, x1, y1 = self.textbbox(xy, text, font=font, anchor=anchor, **kw)
        X0, Y0 = math.floor(x0) - 2, math.floor(y0) - 2
        m = Image.new("L", (math.ceil(x1) - X0 + 3, math.ceil(y1) - Y0 + 3), 0)
        ImageDraw.ImageDraw(m).text((xy[0] - X0, xy[1] - Y0), text, fill=255, font=font, anchor=anchor, **kw)
        self._put(m, X0, Y0, fill)

    def ellipse(self, xy, fill=None, outline=None, width=1):
        x, y, w, h = _box(xy)
        if w < 1 or h < 1: return
        full = (0, 0, w * SS - 1, h * SS - 1)
        if fill is not None:
            self._put(_ss(("e", w, h), w, h, lambda g: g.ellipse(full, fill=255)), x, y, fill)
        if outline is not None and width > 0:
            self._put(_ss(("eo", w, h, width), w, h, lambda g: g.ellipse(full, outline=255, width=width * SS)), x, y, outline)

    def rounded_rectangle(self, xy, radius=0, fill=None, outline=None, width=1, **kw):
        x, y, w, h = _box(xy)
        if w < 1 or h < 1: return
        r = int(min(radius, w // 2, h // 2))
        if fill is not None: self._put(_rr(w, h, r), x, y, fill)
        if outline is not None and width > 0: self._put(_rr_ring(w, h, r, width), x, y, outline)

    def _shape(self, kind, pts, pad, fill, paint):
        X0 = math.floor(min(p[0] for p in pts)) - pad; Y0 = math.floor(min(p[1] for p in pts)) - pad
        w = math.ceil(max(p[0] for p in pts)) + pad - X0 + 1; h = math.ceil(max(p[1] for p in pts)) + pad - Y0 + 1
        loc = tuple((round((px - X0) * SS), round((py - Y0) * SS)) for px, py in pts)
        self._put(_ss((kind, loc, pad), w, h, lambda g: paint(g, loc)), X0, Y0, fill)

    def polygon(self, xy, fill=None, outline=None, width=1):
        if fill is not None: self._shape("p", _pts(xy), 1, fill, lambda g, loc: g.polygon(loc, fill=255))

    def line(self, xy, fill=None, width=0, joint=None):
        pts = _pts(xy)
        if fill is None or len(pts) < 2: return
        if all(abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6 for a, b in zip(pts, pts[1:])):
            return super().line([(round(px), round(py)) for px, py in pts], fill=fill, width=width, joint=joint)
        width = max(1, int(width)); rr = width * SS / 2
        def paint(g, loc):
            g.line(loc, fill=255, width=width * SS, joint="curve")
            for cx, cy in (loc[0], loc[-1]): g.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=255)   # round caps
        self._shape("l", pts, width, fill, paint)

ImageDraw.Draw = lambda im, mode=None: AADraw(im, mode)

# ---------------------------------------------------------------- light core-memory animation
COLS, ROWS, CELL = 96, 54, 20
N = COLS * ROWS
tA = np.full(N, np.inf); tB = np.full(N, np.inf)
for k in range(1400):
    p = (k * 1237) % N; tA[p] = min(tA[p], 0.15 + k * 0.0042)
seeds = [(4000, 0.0)]
for g in range(9):
    new = []
    for (s, t0) in seeds:
        for j in range(9): tB[(s + j) % N] = min(tB[(s + j) % N], t0 + j * 0.02)
        new.append(((s + 2741 * (g + 1) + 377 * len(new)) % N, t0 + 0.55))
    seeds = seeds + new

def core_bg(t, strength=1.0):
    base = np.array(CORE_BASE, float)
    col = np.tile(base, (N, 1))
    a = tA <= t; b = tB <= t
    col[b] = CORE_B; col[a] = CORE_A
    col[(tA <= t) & (tA > t - 0.12)] = RED; col[(tB <= t) & (tB > t - 0.12)] = BLUE
    bg = np.array(BG, float)
    col = bg + (col - bg) * strength
    img = np.repeat(np.repeat(col.reshape(ROWS, COLS, 3), CELL, 0), CELL, 1)
    m = np.ones((CELL, CELL), bool); m[16:, :] = False; m[:, 16:] = False
    out = np.where(np.tile(m, (ROWS, COLS))[..., None], img, bg)
    return Image.fromarray(out.astype(np.uint8), "RGB")

# ---------------------------------------------------------------- frame helpers
CRIT = [("gap", "Gap", "30"), ("diff", "Meaningful difficulty", "30"), ("integ", "Reward integrity", "25"),
        ("craft", "Craft", "15"), ("tie", "Tiebreaker", "training")]

def rail(d, active, a=1.0):
    y0, y1 = 1000, 1052
    d.line((120, 978, 1800, 978), fill=mix(LINE, a), width=2)
    text(d, (120, (y0 + y1) / 2), "JUDGING CRITERIA", F("Inter-Bold.otf", 20), MUTED, a, "lm")
    x = 330
    for key, name, pts in CRIT:
        on = key in active
        s = f"{name}  {pts}"
        f = F("Inter-Bold.otf" if on else "Inter-SemiBold.otf", 24)
        w = d.textlength(s, font=f) + 48
        if on:
            d.rounded_rectangle((x, y0, x + w, y1), 26, fill=mix(ACC, a))
            text(d, (x + w / 2, (y0 + y1) / 2), s, f, BG, a, "mm")
        else:
            d.rounded_rectangle((x, y0, x + w, y1), 26, outline=mix(DIM, a), width=2)
            text(d, (x + w / 2, (y0 + y1) / 2), s, f, MUTED, a, "mm")
        x += w + 16

def panel(d, box, a=1.0, fill=PANEL, outline=LINE, r=20, width=2):
    d.rounded_rectangle(box, r, fill=mix(fill, a), outline=mix(outline, a), width=width)

def head(d, t, kicker, title, k):
    a = ramp(t, 0.0, 0.45) * k
    text(d, (120, 92), kicker, F("Inter-Bold.otf", 30), ACC, a)
    text(d, (120, 132), title, F("InterDisplay-Black.otf", 80), FG, a)

def base(t, dur, active=None):
    """A blank scene. `active` (the judging criteria a scene bears on) is kept for reference; the
    criteria rail is no longer drawn."""
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img, "RGBA")
    return img, d, fade(t, dur)


# ---------------------------------------------------------------- terminal panes
# Anything that is code, a command or a log line is shown as it would look in a terminal:
# a dark window, a monospace font, a green prompt, comments in grey, a block cursor while typing.
TERM_BG, TERM_BAR, TERM_EDGE = (12, 14, 19), (36, 40, 48), (58, 63, 72)
TERM_FG, TERM_DIM, TERM_PROMPT = (214, 220, 228), (124, 132, 144), (110, 220, 120)
TERM_GREEN, TERM_RED = (110, 220, 120), (255, 110, 100)


def terminal(d, box, a, title="zsh"):
    """Draws an empty terminal window; returns (x, y) where its first line starts."""
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, 12, fill=mix(TERM_BG, a), outline=mix(TERM_EDGE, a), width=2)
    d.rounded_rectangle((x0 + 1, y0 + 1, x1 - 1, y0 + 34), 11, fill=mix(TERM_BAR, a))
    d.rectangle((x0 + 1, y0 + 22, x1 - 1, y0 + 34), fill=mix(TERM_BAR, a))
    for i, c in enumerate(((237, 106, 94), (245, 191, 79), (98, 197, 84))):
        cx = x0 + 20 + i * 20
        d.ellipse((cx - 6, y0 + 11, cx + 6, y0 + 23), fill=mix(c, a))
    text(d, ((x0 + x1) / 2, y0 + 17), title, F("Inter-Medium.otf", 18), (170, 176, 186), a, "mm")
    return x0 + 24, y0 + 56


def term_line(d, xy, s, a, size=26, color=None, typed=None, cursor=False):
    """One terminal line. A line starting with '$ ' is a command: green prompt, then the command;
    `typed` shows only the first characters, with a block cursor. Text after ' # ' or ' ; ' is a
    comment, in grey."""
    f = M(size); x, y = xy
    if s.startswith("$ "):
        text(d, (x, y), "$", f, TERM_PROMPT, a, "lm"); x += d.textlength("$ ", font=f); s = s[2:]
    if typed is not None:
        s = s[:typed]
    for sep in (" # ", " ; ", "   ; "):
        if sep in s:
            code, com = s.split(sep, 1)
            text(d, (x, y), code, f, color or TERM_FG, a, "lm")
            text(d, (x + d.textlength(code + sep[:-2], font=f), y), sep.strip()[0] + " " + com, f, TERM_DIM, a, "lm")
            break
    else:
        text(d, (x, y), s, f, color or TERM_FG, a, "lm")
    if cursor:
        cx = x + d.textlength(s, font=f)
        d.rectangle((cx + 2, y - size * 0.55, cx + 2 + size * 0.6, y + size * 0.5), fill=mix(TERM_FG, a * 0.85))

def tick(d, x, y, a, c=ACC):
    d.ellipse((x, y, x + 44, y + 44), fill=mix(c, a))
    d.line((x + 11, y + 23, x + 19, y + 32, x + 33, y + 13), fill=mix(BG, a), width=6, joint="curve")

def cross(d, x, y, a, c=RED):
    d.ellipse((x, y, x + 44, y + 44), fill=mix(c, a))
    d.line((x + 14, y + 14, x + 30, y + 30), fill=mix(BG, a), width=6)
    d.line((x + 30, y + 14, x + 14, y + 30), fill=mix(BG, a), width=6)

def arrow(d, p, q, c, a, width=6, head=24, shrink=0):
    (x0, y0), (x1, y1) = p, q
    ang = math.atan2(y1 - y0, x1 - x0)
    x0 += math.cos(ang) * shrink; y0 += math.sin(ang) * shrink
    x1 -= math.cos(ang) * shrink; y1 -= math.sin(ang) * shrink
    co, si = math.cos(ang), math.sin(ang)
    bx, by, hw = x1 - head * co, y1 - head * si, head * 0.52        # base and half-width of the head
    d.line((x0, y0, bx, by), fill=mix(c, a), width=width)
    d.polygon([(x1, y1), (bx - si * hw, by + co * hw), (bx + si * hw, by - co * hw)], fill=mix(c, a))

def hbar(d, t, x0, x1, y, h, v, c, t0, label, val, lab_font=34, val_font=38, lab_col=FG):
    a = ramp(t, t0); g = ramp(t, t0 + 0.2, 1.1)
    text(d, (x0 - 28, y + h / 2), label, F("Inter-Bold.otf", lab_font), lab_col, a, "rm")
    d.rounded_rectangle((x0, y, x1, y + h), 12, fill=mix(TRACK, a))
    wv = (x1 - x0) * v * g
    if wv > 2: d.rounded_rectangle((x0, y, x0 + wv, y + h), 12, fill=mix(c, a))
    text(d, (x0 + wv + 18, y + h / 2), val(g), F("Inter-Black.otf", val_font), MUTED if c == DIM else c, a, "lm")
    return a


DWARF = [("start  add.ab #4, bmb", "move 4 cells ahead"), ("       mov.i  bmb, @bmb", "drop a bomb there"),
         ("       jmp    start", "repeat"), ("bmb    dat    #0, #0", "the bomb")]

def render(name, fn, dur):
    tmp = os.path.join(OUT, f"{name}.tmp.mp4"); dst = os.path.join(OUT, f"{name}.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "16", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(int(round(dur * FPS))):
        p.stdin.write(fn(i / FPS, dur).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, dst)
    else: sys.exit(f"ffmpeg failed on {name}")
