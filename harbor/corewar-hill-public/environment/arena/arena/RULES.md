# Core War hill: rules

You write one Redcode warrior. It is scored against a hidden hill of 30 human-written
competitive warriors from the public history of the ICWS '94 King-of-the-Hill. The hill
covers the whole strength range, from weak warriors to some of the strongest ever written.

## Simulator and settings

pMARS 0.9.4 runs with the standard '94 hill settings:
- coresize 8000;
- 80000 cycles before a tie;
- 8000 processes per warrior;
- max warrior length 100;
- min distance 100;
- ICWS '94 instruction set with the pMARS extensions (SEQ/SNE/NOP, p-space LDP/STP are
  allowed).

Starting positions follow pMARS's fixed position series (`-f`), so every score is exactly
reproducible. The series is seeded from both warriors' code: any change to yours, even an
unused constant, draws new positions, so differences of about 0.01 between versions are noise.

## Score

Against each hill warrior, your warrior plays 500 rounds. Per round, a win is worth 3
points, a tie 1 and a loss 0. Your hill score is your mean points per round over the whole
hill, divided by 3, so 1 means every round was won.

The reward rescales the hill score so that Dwarf, the classic bomber in `doc/example_dwarf.red`
(hill score 0.1475), gets 0 and a strong human-written warrior (hill score 0.4866) gets 1:

    reward = min(1, max(0, (hill score - 0.1475) / (0.4866 - 0.1475)))

## Validity

- **It must assemble.** The warrior must assemble with pMARS, and it is assembled exactly
  as it is scored: two warriors, 500 rounds. pMARS predefines WARRIORS, ROUNDS and the
  core settings for the preprocessor. A file that does not assemble scores 0.
- **Line and file limits.** pMARS hangs on very long source lines, so comment lines are
  cut to 200 characters and a code line longer than 200 characters makes the file invalid.
  Source files are limited to 20 000 bytes.
- **Write your own warrior.** A near-copy of any published warrior in our corpus of about
  580 (hill and sparring warriors included) scores 0.
  - Near-copy means that, once empty `DAT 0, 0` padding is removed, one of these holds:
    - the assembled code matches with a similarity of 0.8 or more (a copy inside a larger
      file counts);
    - the instruction structure with constants removed matches at 0.9 or more (programs of
      8+ instructions);
    - for a short published warrior that is strong on its own: its instructions appear in
      order (up to 2 extra lines in between) with its step size and most of its numbers
      within 16 of the published ones. The same technique with your own step size is fine.
  - Using published ideas and techniques is fine; submitting someone else's warrior is
    not.

## Sparring pool

There are 30 warriors from the same ladder as the hill, spread over the same strength
range, with ids s01–s30. None of them is on the hill.

They are black boxes: `battle` plays them with exactly the scoring settings (100 rounds by
default, up to 500), but their source and names are not available.

## Time

You have 45 minutes. Every reply from this server ends with a clock: minutes used and
minutes left, counted from your first call to the server. The run itself is stopped 45
minutes after it starts, so the real time left can be a little shorter than the clock shows.
