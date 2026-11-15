#!/usr/bin/env python3
"""Renders every scene of the videos and joins them (ffmpeg concat, no re-encode).
usage: python video/build.py [promo | demo_full | explainer | demo | all] [--join-only]
Writes video/build/<scene>.mp4 and the videos in media/."""
import importlib, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import style

VIDEOS = [("promo", "corewar_pitch_1min59.mp4"),        # the pitch, cut as a promo (pitch.py: the earlier, explanatory cut)
          ("demo_full", "corewar_demo_full.mp4"),       # the full demo
          ("explainer", "corewar_explainer.mp4"),       # shorter cuts: the presentation alone,
          ("demo", "corewar_demo.mp4")]                 # and the run alone

def join(scenes, dst):
    lst = os.path.join(style.OUT, os.path.basename(dst) + ".txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{os.path.join(style.OUT, name)}.mp4'\n" for name, _, _ in scenes)
    tmp = dst[:-4] + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, dst)
    print("wrote", dst, f"({sum(d for _, _, d in scenes):.1f} s)", flush=True)

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    what = args[0] if args else "all"
    media = os.path.join(style.ROOT, "media"); os.makedirs(media, exist_ok=True)
    for mod, out in VIDEOS:
        if what not in ("all", mod):
            continue
        if "--join-only" not in sys.argv:          # each video in its own process: demo_full.py sets its own theme
            subprocess.run([sys.executable, os.path.join(HERE, mod + ".py"), "all"], check=True)
        m = importlib.import_module(mod)
        join(m.SCENES, os.path.join(media, out))
