#!/usr/bin/env python3
"""A quiet electronic bed for the 1:59 pitch, synthesised (no samples, no licence):
a slow A-minor pad (Am - F - C - G), a sub bass, a soft plucked arpeggio, a soft pulse once the
story starts, and light effects at the video's cuts and reveals (sfx.json): a whoosh on each
cut, a soft hit on the big numbers, ticks on the list, a riser before the close. Fade out.
usage: python3 video/audio/music.py OUT.wav [seconds]"""
import json, sys
from pathlib import Path
import numpy as np

SR = 44100
BPM = 88
BEAT = 60 / BPM


def env(n, a, r):
    """Attack / release envelope over n samples (seconds a and r)."""
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def pad(freqs, n, rng):
    """A soft pad: a few slightly detuned sines per note, with slow vibrato."""
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    for f in freqs:
        for det, pan in ((-0.004, 0.3), (0.0, 0.5), (0.005, 0.7)):
            ph = rng.uniform(0, 2 * np.pi)
            w = np.sin(2 * np.pi * f * (1 + det) * t + 0.002 * np.sin(2 * np.pi * 0.2 * t) + ph)
            w += 0.25 * np.sin(2 * np.pi * 2 * f * (1 + det) * t + ph)        # a little brightness
            out[:, 0] += w * (1 - pan); out[:, 1] += w * pan
    return out / (len(freqs) * 3)


def kick(n):
    t = np.arange(n) / SR
    f = 46 + 70 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def tick(n, rng):
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    noise = np.diff(noise, prepend=0)                                        # high-passed noise
    return noise * np.exp(-t * 60)


def pluck(f, n):
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 7)


def whoosh(n, rng):
    """Filtered noise that swells and fades, with a falling pitch feel (moving one-pole filter)."""
    noise = rng.standard_normal(n)
    out = np.zeros(n); y = 0.0
    cut = np.linspace(0.25, 0.03, n)
    for i in range(n):
        y += cut[i] * (noise[i] - y); out[i] = y
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return out * e


def hit(n, rng):
    t = np.arange(n) / SR
    low = np.sin(2 * np.pi * (55 + 40 * np.exp(-t * 20)) * t) * np.exp(-t * 6)
    shimmer = rng.standard_normal(n) * np.exp(-t * 18) * 0.15
    return low + shimmer


def riser(n, rng):
    t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    out = np.zeros(n); y = 0.0
    for i in range(n):
        c = 0.02 + 0.3 * t[i]; y += c * (noise[i] - y); out[i] = y
    return out * t ** 2


def main():
    out_path = sys.argv[1]
    total = float(sys.argv[2]) if len(sys.argv) > 2 else 119.0
    n = int(total * SR)
    rng = np.random.default_rng(3)
    mix = np.zeros((n, 2))
    A = 110.0
    chords = [[A, A * 1.2, A * 1.5, A * 2],                    # Am
              [87.31, 110.0, 130.81, 174.61],                   # F
              [130.81, 164.81, 196.0, 261.63],                  # C
              [98.0, 123.47, 146.83, 196.0]]                    # G
    bar = 4 * BEAT
    clen = 2 * bar
    k = 0
    t0 = 0.0
    while t0 < total:
        ch = chords[k % 4]
        n0, n1 = int(t0 * SR), min(n, int((t0 + clen + 1.5) * SR))
        seg = pad([f * 2 for f in ch], n1 - n0, rng) * env(n1 - n0, 1.2, 1.5)[:, None]
        mix[n0:n1] += 0.55 * seg
        sub = np.sin(2 * np.pi * (ch[0] / 2) * np.arange(n1 - n0) / SR) * env(n1 - n0, 0.4, 1.2)
        mix[n0:n1] += 0.22 * sub[:, None]
        if 18.0 <= t0 < total - 6:                               # soft plucked arpeggio, eighth notes
            notes = [ch[1] * 4, ch[2] * 4, ch[3] * 4, ch[2] * 4]
            lvl = 0.05 if 33.3 <= t0 < 93.0 else 0.08
            for e8 in range(int(clen / (BEAT / 2))):
                i = int((t0 + e8 * BEAT / 2) * SR)
                if i >= n: break
                seg = pluck(notes[e8 % 4], min(int(0.6 * SR), n - i))
                pan = 0.35 if e8 % 2 else 0.65
                mix[i:i + len(seg), 0] += lvl * (1 - pan) * seg; mix[i:i + len(seg), 1] += lvl * pan * seg
        t0 += clen; k += 1
    # the pulse: from the title on, softer during the results and their evidence, fuller for the close
    kk, tk = kick(int(0.5 * SR)), tick(int(0.08 * SR), rng)
    b = 0
    while b * BEAT < total:
        t = b * BEAT
        if t >= 12.6 and t < total - 3.0:
            i = int(t * SR)
            lvl = 0.30 if t < 33.3 else (0.22 if t < 93.0 else 0.34)
            if b % 2 == 0:
                seg = kk[: n - i]; mix[i:i + len(seg)] += lvl * seg[:, None]
            if t >= 102.0:                                       # the close: ticks on the off-beats
                j = int((t + BEAT / 2) * SR)
                if j < n:
                    seg = tk[: n - j]; mix[j:j + len(seg), 0] += 0.05 * seg; mix[j:j + len(seg), 1] += 0.06 * seg
        b += 1
    fx = json.loads((Path(__file__).resolve().parent / "sfx.json").read_text())
    def add(seg, t, lvl):
        i = int(t * SR)
        if i >= n: return
        seg = seg[: n - i]
        if seg.ndim == 1: seg = np.stack([seg, seg], 1)
        mix[i:i + len(seg)] += lvl * seg
    for t in fx["whoosh"]:
        w = whoosh(int(0.7 * SR), rng); add(np.stack([w, np.roll(w, 300)], 1), t - 0.35, 0.35)
    for t in fx["hit"]:
        add(hit(int(0.8 * SR), rng), t, 0.32)
    for t in fx["tick"]:
        add(tick(int(0.06 * SR), rng), t, 0.10)
    for t0, t1 in fx["riser"]:
        add(riser(int((t1 - t0) * SR), rng), t0, 0.22)
    # overall shape: quiet intro, a fade out at the end
    t = np.arange(n) / SR
    shape = np.clip(0.55 + 0.45 * (t - 6) / 6, 0.55, 1.0)
    shape *= np.clip((total - t) / 4.0, 0, 1)
    mix *= shape[:, None]
    mix /= np.max(np.abs(mix)) + 1e-9
    mix *= 0.5
    import wave
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    print("wrote", out_path, f"{total:.1f} s")


if __name__ == "__main__":
    main()
