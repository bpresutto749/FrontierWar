# Credits and licences

Our own code and documents are under the MIT licence (`LICENSE`). The third-party parts
listed below are not: they keep their own licences and authors. This covers every copy of
pMARS (`pmars/` and the copies under `harbor/`), the reference documents in `doc/` other
than `doc/strategy_primer.md`, and the warriors in `data/`, `training/train_hill/` and
`runs/codeclash-ladder-2026-07/`.

- **pMARS 0.9.4.** The Core War simulator (`pmars/`, GPL v2, see `pmars/COPYING` and
  `pmars/AUTHORS`). Our copy comes from the CodeClash fork
  (github.com/CodeClash-ai/CoreWar), built unmodified in KotH-server mode
  (`-DEXT94 -DSERVER -DPERMUTATE -DRWLIMIT`: no graphics, no debugger). Its battle
  results are identical to the CodeClash build; we checked this on test battles.
- **Language reference.** `doc/` (the Redcode reference, the ICWS '94 draft standard
  and the pMARS manual) comes from the same repository.
- **Human warriors.** The hidden hill, the sparring pool, the reference and the
  CodeClash part of the corpus are the 264 human warriors of CodeClash's CC:Ladder
  (`origin/human/*` branches). Their Elo ranking comes from
  `configs/ladder/rungs/corewar.yaml` of github.com/CodeClash-ai/CodeClash.
  - The authors credited in the files on the hill, the sparring pool and the reference
    are Andy Pierce, Anton Marsden, Beppe, bjoern guenzel, Campbell Fraser, Christian
    Schmidt, David Moore, elkauka, Fizmo & Roy, Ian Oversby, inversed, John K W, John
    Metcalf, John Wilkinson, M R Bremer, Matt Hastings, Michal Janeczek, P. Kline,
    Philip Kendall, Robert Macrae, Roy van Rijn, Scott Nelson, Stefan Strack, Steve
    Gunnell, W. Mintardjo and Wayne Sheppard.
  - The reference, **Toxic**, is by John Metcalf.
- **Second corpus.** 317 more human warriors from the Digital Red Queen repository
  (github.com/SakanaAI/drq, Apache 2.0). We use them only for the copy report and the
  training hill.
- **Prior LLM warriors.** `runs/codeclash-ladder-2026-07/` holds the final warriors of
  Claude Opus 4.8, GPT-5.5, Claude Sonnet 5 and Gemini 3.5 Flash from CodeClash's July
  2026 CC:Ladder Core War runs (their LadderTournament branches). We include them as
  outside evidence, scored with our hill.
