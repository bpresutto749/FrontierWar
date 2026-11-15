"""A small ICWS '94 MARS, for visualising one round (no p-space: LDP/STP act as NOP).
Scoring in the task is always done by pMARS; this only draws a battle, and is checked
against pMARS round outcomes in check_mars()."""
import re, subprocess, sys
from collections import deque

CORE, MAXCYC, MAXPROC = 8000, 80000, 8000
LINE = re.compile(r"^\s*(START\s+)?([A-Z]{3})\.([A-Z]{1,2})\s+([#$*@{<}>])\s*(-?\d+)\s*,\s*([#$*@{<}>])\s*(-?\d+)")

def parse_listing(text):
    """Warriors from a pMARS listing: list of (name, instructions, start)."""
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("Program "):
            cur = [re.search(r'"(.*?)"', line).group(1), [], 0]; out.append(cur); continue
        if cur is None: continue
        m = LINE.match(line)
        if m:
            if m.group(1): cur[2] = len(cur[1])
            cur[1].append([m.group(2), m.group(3), m.group(4), int(m.group(5)) % CORE, m.group(6), int(m.group(7)) % CORE])
    return out

class Mars:
    def __init__(self, w1, w2, pos2):
        self.core = [["DAT", "F", "$", 0, "$", 0] for _ in range(CORE)]
        self.owner = [0] * CORE           # 0 empty, 1 / 2 last writer
        self.q = [deque(), deque()]
        for k, ((name, ins, start), base) in enumerate(((w1, 0), (w2, pos2))):
            for i, x in enumerate(ins):
                self.core[(base + i) % CORE] = list(x); self.owner[(base + i) % CORE] = k + 1
            self.q[k].append((base + start) % CORE)
        self.cycle = 0; self.writes = []

    def _w(self, addr, who):
        self.owner[addr] = who; self.writes.append((addr, who))

    def operand(self, pc, mode, val, who):
        """(pointer, copy of the instruction it points to). As in ICWS '94, the copy is
        taken after any predecrement and before any postincrement."""
        c = self.core
        if mode == "#": return pc, list(c[pc])
        p = (pc + val) % CORE
        if mode == "$": return p, list(c[p])
        if mode in "*{}":
            if mode == "{": c[p][3] = (c[p][3] - 1) % CORE; self._w(p, who)
            r = (p + c[p][3]) % CORE; cp = list(c[r])
            if mode == "}": c[p][3] = (c[p][3] + 1) % CORE; self._w(p, who)
            return r, cp
        if mode == "<": c[p][5] = (c[p][5] - 1) % CORE; self._w(p, who)
        r = (p + c[p][5]) % CORE; cp = list(c[r])
        if mode == ">": c[p][5] = (c[p][5] + 1) % CORE; self._w(p, who)
        return r, cp

    def step(self, k):
        """Execute one instruction of warrior k (0/1). Returns the executed address or None."""
        q = self.q[k]
        if not q: return None
        pc = q.popleft(); who = k + 1; c = self.core
        ir = list(c[pc]); op, mod = ir[0], ir[1]
        ra, air = self.operand(pc, ir[2], ir[3], who)
        rb, bir = self.operand(pc, ir[4], ir[5], who)
        nxt = (pc + 1) % CORE
        A, B = 3, 5
        def pairs():
            return {"A": [(A, A)], "B": [(B, B)], "AB": [(A, B)], "BA": [(B, A)],
                    "F": [(A, A), (B, B)], "X": [(A, B), (B, A)], "I": [(A, A), (B, B)]}[mod]
        if op == "DAT":
            return pc
        if op == "MOV":
            if mod == "I": c[rb] = list(air)
            else:
                for s, d in pairs(): c[rb][d] = air[s]
            self._w(rb, who); q.append(nxt)
        elif op in ("ADD", "SUB", "MUL", "DIV", "MOD"):
            alive = True
            for s, d in pairs():
                x, y = air[s], bir[d]
                if op == "ADD": v = (y + x) % CORE
                elif op == "SUB": v = (y - x) % CORE
                elif op == "MUL": v = (y * x) % CORE
                elif x == 0: alive = False; continue
                elif op == "DIV": v = y // x
                else: v = y % x
                c[rb][d] = v
            self._w(rb, who)
            if alive: q.append(nxt)
        elif op == "JMP": q.append(ra)
        elif op in ("JMZ", "JMN"):
            fields = {"A": [A], "BA": [A], "B": [B], "AB": [B]}.get(mod, [A, B])
            zero = all(bir[f] == 0 for f in fields)
            jump = zero if op == "JMZ" else not zero
            q.append(ra if jump else nxt)
        elif op == "DJN":
            fields = {"A": [A], "BA": [A], "B": [B], "AB": [B]}.get(mod, [A, B])
            for f in fields:
                c[rb][f] = (c[rb][f] - 1) % CORE; bir[f] = (bir[f] - 1) % CORE
            self._w(rb, who)
            nonzero = not all(bir[f] == 0 for f in fields)
            q.append(ra if nonzero else nxt)
        elif op == "SPL":
            q.append(nxt)
            if len(q) < MAXPROC: q.append(ra)
        elif op in ("SEQ", "CMP", "SNE"):
            if mod == "I": eq = air == bir
            else: eq = all(air[s] == bir[d] for s, d in pairs())
            skip = eq if op != "SNE" else not eq
            q.append((pc + 2) % CORE if skip else nxt)
        elif op == "SLT":
            fields = {"A": [(A, A)], "B": [(B, B)], "AB": [(A, B)], "BA": [(B, A)], "F": [(A, A), (B, B)],
                      "X": [(A, B), (B, A)], "I": [(A, A), (B, B)]}[mod]
            lt = all(air[s] < bir[d] for s, d in fields)
            q.append((pc + 2) % CORE if lt else nxt)
        else:                       # NOP, LDP, STP
            q.append(nxt)
        return pc

    def run(self, on_cycle=None):
        """Play the round. Returns 1 or 2 (winner) or 0 (tie)."""
        while self.cycle < MAXCYC:
            ex = []
            for k in (0, 1):
                ex.append(self.step(k))
                if not self.q[k]:
                    if on_cycle: on_cycle(self, ex)
                    return 2 - k
            self.cycle += 1
            if on_cycle: on_cycle(self, ex)
        return 0

def listing(path_a, path_b, pmars, rounds=1, F=None):
    args = [pmars, "-r", str(rounds), "-b"] + (["-F", str(F)] if F is not None else []) + [path_a, path_b]
    return subprocess.run(args, capture_output=True, text=True).stdout

def pmars_round(path_a, path_b, pmars, F):
    """Winner of one pMARS round with warrior 2 at position F: 1, 2 or 0."""
    out = subprocess.run([pmars, "-r", "1", "-b", "-F", str(F), path_a, path_b], capture_output=True, text=True).stdout
    sc = [int(x) for x in re.findall(r"scores (\d+)", out)]
    if sc[0] > sc[1]: return 1
    if sc[1] > sc[0]: return 2
    return 0
