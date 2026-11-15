#!/usr/bin/env python3
"""Checks a video's scenes without encoding them: text that leaves the frame, texts that overlap,
and text that is not on screen long enough to be read.
The reading check simulates a viewer who reads every line in order of appearance at WPS words per
second. A number counts for half a word; code, log lines and running counters are glanced at, not
read, and count for a third; a heading repeated from the previous scene is not read again.
Text out of frame or overlapping fails the check; reading time is reported (slack per scene, in seconds).
usage: python video/audit.py <module> [words-per-second]      e.g. python video/audit.py pitch 4
AUDIT_ONLY=a,b audits only those scenes; AUDIT_VERBOSE=1 prints when each line is read."""
import importlib, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from PIL import Image, ImageDraw
import style
VERBOSE = os.environ.get("AUDIT_VERBOSE") == "1"     # print when each line is read
ONLY = set(filter(None, os.environ.get("AUDIT_ONLY", "").split(",")))   # audit only these scenes

REC = []
_probe = ImageDraw.ImageDraw(Image.new("RGB", (8, 8)))
_orig = style.text

def _text(d, xy, s, font, fill, a=1.0, anchor="la"):
    if s.strip() and a > 0:
        REC.append((s, _probe.textbbox(xy, s, font=font, anchor=anchor), a, "Mono" in font.getname()[0]))
    return _orig(d, xy, s, font, fill, a, anchor)

def words(s):
    return sum(1.0 if re.search("[A-Za-z]", w) else 0.5 if re.search(r"\d", w) else 0.0 for w in s.split())

def audit(modname, wps=4.0, step=0.1):
    mod = importlib.import_module(modname)
    for m in list(sys.modules.values()):
        if getattr(m, "text", None) is _orig: m.text = _text
    if hasattr(mod, "show"):                       # promo.py draws its words with show(), not text()
        _show0 = mod.show
        def _show(img, s, font, size, color, x, y, t, t0, t1=None, anchor="m"):
            if s.strip() and t >= t0 and (t1 is None or t <= t1):
                a = style.ease((t - t0) / 0.6) * (style.clamp((t1 - t) / 0.5) if t1 is not None else 1.0)
                l, tp, r, b = style.F(font, size).getbbox(s)
                x0 = {"l": x, "m": x - (r - l) / 2, "r": x - (r - l)}[anchor]
                REC.append((s, (x0, y - (b - tp) / 2, x0 + r - l, y + (b - tp) / 2), a, False))
            return _show0(img, s, font, size, color, x, y, t, t0, t1, anchor)
        mod.show = _show
    problems, lates, total_words, total_dur = 0, 0, 0.0, 0.0
    print(f"{'scene':<14}{'dur':>6}{'words':>7}{'w/s':>6}{'slack':>7}")
    previous = set()
    for name, fn, dur in getattr(mod, "RAW_SCENES", mod.SCENES):      # a framed video is checked without its frame
        if ONLY and name not in ONLY:                                     # skipped, but its headings still count
            REC.clear(); fn(min(2.0, dur / 2), dur)
            previous = {(r[0], round(r[1][0]), round(r[1][1])) for r in REC if r[2] >= 0.6}
            continue
        seen, out, overlap, variants = {}, set(), set(), {}
        t = 0.0
        while t < dur:
            REC.clear(); fn(t, dur)
            vis = [r for r in REC if r[1][1] < 985]                    # the criteria rail is not content
            for s, (x0, y0, x1, y1), a, mono in vis:
                if a >= 0.6:
                    key = re.sub(r"\d[\d,.:]*", "#", s)
                    if not re.search("[A-Za-z]", key): key += f"@{round(y0 / 30)}"   # a bare number: one per row
                    if s.startswith("$ "): key = f"$@{round(y0 / 8)}"                # a command being typed
                    variants.setdefault(key, set()).add(s)
                    e = seen.setdefault(key, [t, t, 0.0, y0, x0, s, (s, round(x0), round(y0))])
                    e[1] = t
                    w = words(s) * (0.34 if mono else 1.0)
                    if w > e[2]: e[2], e[5] = w, s
                if a >= 0.25 and (x0 < 108 or x1 > 1812 or y0 < 55 or y1 > 975):
                    out.add((s, (round(x0), round(y0), round(x1), round(y1))))
            big = [r for r in vis if r[2] >= 0.25]
            for i in range(len(big)):
                for j in range(i + 1, len(big)):
                    a_, b_ = big[i][1], big[j][1]
                    if min(a_[2], b_[2]) - max(a_[0], b_[0]) > 6 and min(a_[3], b_[3]) - max(a_[1], b_[1]) > 6:
                        overlap.add((big[i][0], big[j][0]))
            t += step
        for key, e in seen.items():
            if len(variants[key]) > 3 and not key.startswith("$"): e[2] *= 0.34      # a running counter
            if e[6] in previous: e[2] = 0.0                                          # heading kept from the last scene
        previous = {e[6] for e in seen.values()}
        items = sorted(seen.values(), key=lambda e: (round(e[0], 1), e[3], e[4]))
        clock, late = 0.0, []
        for t_on, t_off, w, _, _, s, _ in items:
            if w == 0: continue
            start = max(clock, t_on)
            clock = start + w / wps + 0.1
            if VERBOSE: print(f"      on {t_on:5.1f}  read {start:5.1f}-{clock:5.1f}  off {t_off:5.1f}  {s[:70]}")
            if clock > t_off + 0.15: late.append((s, round(clock - t_off, 1)))
        nwords = sum(e[2] for e in items)
        last_off = max((e[1] for e in items), default=dur)
        print(f"{name:<14}{dur:>6.1f}{nwords:>7.0f}{nwords / dur:>6.1f}{last_off - clock:>7.1f}")
        for s, over in late: print(f"    late by {over}s: {s[:70]}")
        for s, bb in sorted(out): print(f"    OUT OF FRAME {bb}: {s[:60]}")
        for a_, b_ in sorted(overlap): print(f"    OVERLAP: {a_[:40]!r} / {b_[:40]!r}")
        problems += len(out) + len(overlap); lates += len(late); total_words += nwords; total_dur += dur
    print(f"total {total_dur:.1f} s, {total_words:.0f} words, {total_words / total_dur:.2f} words/s; "
          f"{problems} layout problem(s), {lates} line(s) late at {wps} words/s")
    return problems

if __name__ == "__main__":
    sys.exit(1 if audit(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 4.0) else 0)
