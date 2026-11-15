"""Prompts for the MLX training run: a compact Redcode reference, the strategy primer's archetypes
in a few lines (no warrior code), and one task line per archetype.
Every sample is asked for one archetype, in turn, so that each round holds every style and the
selection can keep the best of each (training/mlx/pick.py)."""

RULES = """You write Core War warriors in Redcode (ICWS '94, pMARS 0.9.4).
Your warrior fights a hill of strong human-written warriors, one at a time. Settings: core size 8000, \
80000 cycles per round, up to 8000 processes, warriors at most 100 instructions, placed at random \
at least 100 cells apart. Per round: win = 3 points, tie = 1, loss = 0.

REDCODE IN BRIEF
- The core is a ring of 8000 cells. Every address is relative to the instruction that uses it.
- Line format:  [label]  OPCODE[.MODIFIER]  [mode]A, [mode]B   ; comment
- A warrior starts with one process at its first instruction, or at the label given by ORG. \
Each cycle, each warrior executes one instruction of its next process. A process that executes \
DAT dies. A warrior with no process left loses.
- Opcodes:
  DAT  kills the process that executes it (the usual bomb)
  MOV  copies A to B
  ADD SUB MUL DIV MOD  arithmetic into B (DIV or MOD by 0 kills the process)
  JMP  jumps to A;  JMZ / JMN jump to A if B is zero / not zero
  DJN  decrements B, then jumps to A if B is not zero
  SPL  starts a new process at A, and goes on at the next instruction
  SEQ (same as CMP) / SNE  skip the next instruction if A and B are equal / different
  SLT  skips the next instruction if A < B;  NOP does nothing
- Modifiers choose the fields used: .A .B .AB .BA .F .X .I (.I = the whole instruction).
- Addressing modes: # immediate, $ direct (the default), @ indirect through B, * indirect \
through A, < and > indirect through B with pre-decrement / post-increment, { and } the same through A.
- Constants: name EQU value.  Syntax examples (single lines, not a warrior):
      step    equ   3364
      ptr     dat   #0, #0
              mov.i bomb, @ptr
              add.ab #step, ptr
              spl   #0, 0
      loop    djn.b loop, #10

STRATEGY NOTES
- Stone (bomber): a small loop that drops DAT or SPL bombs at a fixed step; the step decides how \
evenly and how fast the core is covered.
- Paper (replicator): copies itself again and again (SPL/MOV with post-increment pointers); \
killing one copy does not kill it.
- Scanner: looks for non-empty cells (SEQ/SNE/JMZ), then attacks what it found, often with SPL 0 \
bombs followed by a core clear.
- Imp: MOV 0, 1 copies itself forward forever. Very hard to kill, but it kills nothing: alone it \
only ties.
- Scanners beat papers, papers beat stones, stones beat scanners. Strong warriors combine styles, \
for example a stone that also launches imps."""

ARCHETYPES = [
    ("stone", "a stone (bomber): a small loop that bombs the core at a fixed step"),
    ("paper", "a paper (replicator): a program that copies itself to new places and spawns processes"),
    ("scanner", "a scanner: it finds the opponent by looking for non-empty cells, then attacks it"),
    ("stone_imp", "a stone/imp composite: a stone that also launches imps with SPL"),
    ("free", "your own design: any style or combination that you expect to score best"),
]

PREFILL = "```redcode\n"           # the assistant's reply starts here, so every sample is one code block


def messages(arch, completion=None):
    desc = dict(ARCHETYPES)[arch]
    user = (RULES + f"\n\nTASK\nWrite a complete, original warrior of this kind: {desc}. "
            "Do not copy published warriors: copies score 0. Reply with the warrior only, in one "
            "```redcode block that starts with ;redcode-94 and a ;name line.")
    m = [{"role": "user", "content": user}]
    if completion is not None:
        m.append({"role": "assistant", "content": PREFILL + completion.rstrip() + "\n```"})
    return m


def assign(n):
    """Archetype of sample i: round-robin, so every archetype gets n / 5 samples."""
    return [ARCHETYPES[i % len(ARCHETYPES)][0] for i in range(n)]


def source_of(text):
    """The warrior: everything the model wrote before it closed the code block."""
    return text.split("```")[0].strip() + "\n"


# ---------------------------------------------------------------- run 2: one round of feedback from the battle tool
def feedback_note(fb):
    """The second user turn: the battle tool's own output on the draft, as the agent would see it."""
    return ("I ran it with the battle tool (100 rounds against each of the 30 sparring warriors). "
            "Its output:\n```\n" + fb.rstrip() + "\n```\n"
            "Write an improved version that scores higher against these opponents. Reply with the "
            "complete warrior only, in one ```redcode block that starts with ;redcode-94 and a ;name line.")


def revision_messages(arch, draft, fb, revision=None):
    """Draft, battle output, revision: the loss (mlx_lm --mask-prompt) falls on the revision only."""
    m = messages(arch, draft)
    m.append({"role": "user", "content": feedback_note(fb)})
    if revision is not None:
        m.append({"role": "assistant", "content": PREFILL + revision.rstrip() + "\n```"})
    return m
