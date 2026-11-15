# Core War strategy primer

This is a short summary of community knowledge about the ICWS '94 hills. It contains no
warrior code. The language itself is documented in `redcode/`, `guide.htm` and
`icws94-standard.txt`.

## Archetypes

- **Imp.** `MOV 0, 1` copies itself one cell ahead forever.
  - Imps are very hard to kill and kill almost nothing, so on their own they mostly tie.
  - Several imps spaced CORESIZE/n apart and executed in turn form an *imp ring* or
    *imp spiral*, which is sturdier.
- **Stone (bomber).** A small loop that drops bombs (DAT to kill, SPL to slow) at a
  fixed step through the core.
  - It is small, fast and hard to find.
  - The choice of step matters: it decides how evenly and how fast the core gets
    covered.
- **Paper (replicator).** Copies itself to new places, again and again, and spawns many
  processes.
  - Killing one copy does not kill the warrior, so DAT bombs alone rarely beat it.
  - "Silk" papers copy with `SPL`/`MOV` pairs and post-increment pointers.
- **Scanner.** Looks for non-empty cells (`SEQ`/`SNE`/`JMZ`), then attacks what it
  found.
  - Typical attacks: a few bombs, a carpet of `SPL 0` bombs that stuns the target, or a
    switch into a core clear.
  - A scanner has to avoid detecting itself, and its speed is measured in cells per
    cycle (0.5c, 0.66c, ...).
- **Core clear.** Overwrites the whole core in sequence, typically with SPL first
  (stun), then DAT (kill).
  - Clears are used to finish off stunned opponents. They are often the last phase of a
    scanner.
- **Quick-scan (qscan).** A fast, unrolled scan of many cells right at the start of the
  round.
  - It catches an opponent before the opponent has booted or replicated.
  - When it finds nothing, it hands over to the main warrior.
- **Vampire.** Bombs with `JMP` "fangs" that redirect enemy processes into a pit that
  makes them harmless or useful.
- **P-space switcher.** Uses the private p-space memory, which persists between the
  rounds of a battle, to pick a strategy in each round from earlier results. For
  example, it can switch after a loss.

## How they interact (the classic triangle)

- Scanners tend to beat papers: they find and stun the many copies.
- Papers tend to beat stones: there are too many copies to bomb.
- Stones tend to beat scanners: a stone is small and bombs while the scanner is still
  looking.
- Imps add ties against warriors that cannot catch them. *Imp gates* (a cell that is
  decremented on every pass) are the usual defence.

The strongest warriors rarely use one archetype alone. Common composites:

| composite | idea |
|---|---|
| stone/imp | the stone wins against scanners and the imps secure ties against papers |
| paper/imp | papers that also launch imps |
| qscan → body | a quick-scan opening followed by any of the above |

## Practical techniques

- **Boot.** Copy the working code far from where it was loaded, often leaving a decoy
  behind, so that opponents aiming at the start position hit the wrong place.
- **Decoys.** Cells that look like code, to waste a scanner's time.
- **Step choice.** Steps are usually chosen so the bombing or scanning pattern covers
  the core evenly, and so that the warrior does not hit itself before the pass ends.
- **Testing.** Strength is relative: a warrior is only as good as the set of opponents
  it was tested against.
  - Test against a varied set.
  - Use random start positions (pMARS without `-f`, or with different `-F` offsets).
  - Do not trust differences that are smaller than the noise between runs.
