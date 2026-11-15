# Videos

All the videos are drawn frame by frame in Python (Pillow) and encoded with ffmpeg. Every number on
screen comes from this repository; nothing is filmed or hand-edited.

| video | length | what it shows |
|---|---|---|
| [`media/corewar_pitch_1min59.mp4`](../media/corewar_pitch_1min59.mp4) | 1 min 59 | **the pitch, as a promo** (`promo.py`), built on one question and its answer. Q: "Can a frontier AI agent turn practice into a design that wins against opponents it has never seen?" A: "Not yet. They can't find a winning design, escape the traps of practice, or both." The question -> the game -> the test (30 practice opponents, 30 it has never seen) -> the 0-1 scale, copies and fakes score 0 -> 0.71 / 0.84 -> the answer, under the question, with its table (GPT-6.1 sol: no winning design, no traps; Claude Opus 5.5: both) -> why not, 1, the design: the chart of every run (`chart.py`; over 90% of both agents' gap to Toxic is already there in practice) and GPT-6.1 sol's 15,000 games (wins as often, loses 3–5× as often) -> why not, 2, the traps of practice (Claude Opus all three, GPT-6.1 sol none) -> what it measures -> the question, "Not yet", the thesis. `pitch.py` keeps the earlier, explanatory cut. |
| [`media/corewar_demo_full.mp4`](../media/corewar_demo_full.mp4) | 8 min 07 | **the full demo**, told as an inquiry in five chapters named on a bar at the bottom: 1. the test (the game, practice vs hidden opponents, the scale, no shortcut by brute force or by cheating, the oracle and do-nothing runs), 2. the results (both agents' `harbor run`s, 0.71 / 0.84, then "Not yet" under the question: so what goes wrong?), 3. what goes wrong (Claude Opus 5.5, run C5 replayed from its logs, one real game against Blizzard, each trap of practice up close; GPT-6.1 sol avoids them; why the traps matter in everyday coding: so avoid them, and you win?), 4. is that all? (no: GPT-6.1 sol avoids every trap and still scores 0.84; the design, kept back until here: the chart of every run, the 15,000 games, why they fall short on design, why it matters), 5. the answer (the question, "Not yet" and the table, the thesis), then the bonus: training small models (RL_SYNTHESIS.md) |
| [`media/corewar_explainer.mp4`](../media/corewar_explainer.mp4) | 3 min 53 | shorter cut: the presentation alone |
| [`media/corewar_demo.mp4`](../media/corewar_demo.mp4) | 3 min 15 | shorter cut: the run alone (the test, the run, the result, why the gap) |

The full demo uses the same scenes in a dark theme (`VIDEO_THEME=dark`, set by `demo_full.py`). The colours mean the same thing everywhere: red is the AI, green is the human expert, blue is
everything else (headings, opponents, the criteria rail).

## Where the numbers come from

- Rewards, game scores and minutes: `runs/harbor/` (Harbor `result.json`, the verifier's
  `details.json` and `reward.txt`), `results/trajectories_harbor_v4.md`, FAILURES.md.
- The run replay (minutes, practice scores, log lines): run C5's event log and submission
  history in `runs/harbor/v4-opencode-opus-5.5/corewar-hill__X7kqQnj/`.
- The side-by-side game (the AI's program and the reference against Blizzard): replayed by
  `mars.py`, a small ICWS '94 simulator used only for drawing. `demo.py` asserts that each
  replayed game ends as pMARS says, and `check_mars.py` checks 90 rounds against pMARS (90/90).
- The 500-game tallies against Blizzard: the verifier's per-opponent results.
- "0 of 27 AI runs" (the shorter cuts): the 5 shipped (v4) Harbor runs and the 22 earlier ones listed in FAILURES.md.
  The pitch and the full demo add the GPT-6.1 sol runs.
- Every GPT-6.1 sol figure, and every figure comparing the two models: `results/models.json`, written by
  `exploits/compare_models.py` from `runs/harbor/v4-opencode-gpt-6.1/` and `runs/harbor/v4-opencode-opus-5.5/`,
  read by `video/figures.py`.

## Files

| file | content |
|---|---|
| `style.py` | palette, fonts, easing, anti-aliased shapes, panels, the judging-criteria rail, the memory background, `render()` |
| `explainer.py` | the presentation's scenes, one function per scene |
| `demo.py` | the run's scenes (the test, the replay, the result, the game), shared by the demo and the full demo |
| `pitch.py` | the pitch: eleven scenes of its own, 119 seconds |
| `demo_full.py` | the full demo: its own slides, three of `pitch.py`'s, and the run's scenes from `demo.py`; each slide lasts the reading time `audit.py` gives at 4 words per second, plus 0.6 s |
| `mars.py` | the simulator that replays one game for the demo |
| `check_mars.py` | checks `mars.py` against pMARS |
| `figures.py` | the two-model figures, read from `results/models.json` (nothing typed in by hand) |
| `chart.py` | the chart of every run (practice score across, hidden-test score up), shared by the pitch and the full demo |
| `audit.py` | checks a video without encoding it: text out of frame, overlapping text, and reading time per scene |
| `build.py` | renders every scene and joins them into `media/` |

## Rebuild

Needs Python 3 with Pillow and NumPy, ffmpeg with libx264, the Inter fonts (`fonts-inter`) and
DejaVu Sans Mono, and pMARS built by `make pmars`.

```bash
make videos                        # checks, then all the videos -> media/  (scenes in video/build/)
python3 video/build.py pitch       # one video
python3 video/demo.py w11_fight    # one scene -> video/build/w11_fight.mp4
python3 video/audit.py pitch 4     # layout and reading-time check, at 4 words per second
AUDIT_ONLY=f06_game AUDIT_VERBOSE=1 python3 video/audit.py demo_full 4   # one scene, with when each line is read
python3 video/check_mars.py        # the simulator used for drawing agrees with pMARS
```

Font locations can be overridden with `INTER_DIR` and `MONO_PREFIX`, and the scene folder with
`VIDEO_BUILD`.

## Voice-over and music (the 1:59 pitch)

`video/audio/script.json` holds the narration, one line per visual beat, with its start time and
the time by which it must end. `video/audio/mix.py` reads it with Kokoro (82M parameters,
Apache-2.0, run locally with `kokoro-onnx`, voice `af_heart`), refuses any line that would
overrun its beat, synthesises the music bed (`video/audio/music.py`: an A-minor pad, a sub bass
and a soft pulse, no samples), ducks the music under the voice, normalises the whole track to
−16 LUFS with one gain, and muxes it into `media/corewar_pitch_1min59.mp4` (video stream copied).

```bash
pip install kokoro-onnx soundfile
# kokoro-v1.0.onnx and voices-v1.0.bin from github.com/thewh1teagle/kokoro-onnx (release model-files-v1.0)
python3 video/build.py promo --join-only && python3 video/audio/mix.py --models DIR
```
