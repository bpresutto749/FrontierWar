#!/usr/bin/env python3
"""Adds the voice-over and the music bed to the 1:59 pitch (media/corewar_pitch_1min59.mp4).
The voice is Kokoro (82M, Apache-2.0) run locally with kokoro-onnx, voice af_heart; each line
of script.json starts at its time and must end before the next visual beat. The music is
synthesised by music.py and ducked under the voice.
  pip install kokoro-onnx soundfile
  model files: kokoro-v1.0.onnx and voices-v1.0.bin from github.com/thewh1teagle/kokoro-onnx releases
usage: python3 video/audio/mix.py [--models DIR] [--video media/corewar_pitch_1min59.mp4]"""
import argparse, json, os, subprocess, sys, tempfile, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def synth(models, lines, out_dir):
    import soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro(str(Path(models) / "kokoro-v1.0.onnx"), str(Path(models) / "voices-v1.0.bin"))
    sr = None
    for key, t0, t1, text in lines:
        samples, sr = k.create(text, voice="af_heart", speed=1.05, lang="en-us")
        dur = len(samples) / sr
        if dur > t1 - t0:
            sys.exit(f"{key}: the line lasts {dur:.2f} s but has {t1 - t0:.2f} s: shorten it")
        sf.write(out_dir / f"{key}.wav", samples, sr)
        print(f"  {key} {t0:6.1f}s  {dur:4.2f}/{t1 - t0:4.2f} s  {text}", flush=True)
    return sr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=os.environ.get("KOKORO_DIR", "/tmp/tts"))
    ap.add_argument("--video", default=str(ROOT / "media" / "corewar_pitch_1min59.mp4"))
    a = ap.parse_args()
    lines = json.load(open(HERE / "script.json"))
    tmp = Path(tempfile.mkdtemp(prefix="voice_"))
    sr = synth(a.models, lines, tmp)
    total = 119.0
    voice = np.zeros(int(total * sr), np.float32)
    import soundfile as sf
    for key, t0, _, _ in lines:
        s, _ = sf.read(tmp / f"{key}.wav", dtype="float32")
        i = int(t0 * sr); voice[i:i + len(s)] += s[: len(voice) - i]
    vpath, mpath = tmp / "voice.wav", tmp / "music.wav"
    sf.write(vpath, voice, sr)
    subprocess.run([sys.executable, str(HERE / "music.py"), str(mpath), str(total)], check=True)
    out = a.video[:-4] + ".tmp.mp4"
    graph = ("[1:a]aresample=44100,pan=stereo|c0=c0|c1=c0,highpass=f=70,"
             "acompressor=threshold=0.1:ratio=3:attack=5:release=120[v];"
             "[v]asplit=2[v1][v2];"
             "[0:a]volume=0.2[m0];"
             "[m0][v1]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=600:makeup=1[m];"
             "[m][v2]amix=inputs=2:normalize=0:weights=1.0 1.0[out]")
    raw = tmp / "mix.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mpath), "-i", str(vpath), "-filter_complex", graph,
                    "-map", "[out]", "-ar", "44100", str(raw)], check=True)
    # one gain for the whole track (a dynamic normaliser would lift the music between lines)
    meas = subprocess.run(["ffmpeg", "-nostats", "-i", str(raw), "-af", "ebur128", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    lufs = float(meas.split("Integrated loudness:")[1].split("I:")[1].split("LUFS")[0])
    gain = -16.0 - lufs
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.video, "-i", str(raw),
                    "-filter_complex", f"[1:a]volume={gain:.2f}dB,alimiter=limit=0.89:level=false[out]",
                    "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                    "-t", str(total), "-movflags", "+faststart", out], check=True)
    print(f"loudness {lufs:.1f} LUFS -> -16 LUFS (gain {gain:+.1f} dB)")
    os.replace(out, a.video)
    print("wrote", a.video, "with voice-over and music")


if __name__ == "__main__":
    main()
