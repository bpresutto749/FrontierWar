## Lessons from earlier attempts at this task

These come from the failure analysis of earlier agent runs on this exact task.

1. The sparring pool is 10 warriors: treat it as a small validation set, not as
   the test. In earlier runs, the agent that pushed its sparring score highest
   (above a strong human warrior's score on the same pool) did worst on the
   hidden hill. Do not keep tuning constants once differences are within noise.
2. Build your own wider test set. Write simple warriors of each major archetype
   (stones that bomb with DAT and SPL, imp spirals and imp rings, silk-style
   papers, scanners, core clears, quick-scans) and check every candidate against
   them as well as the sparring pool, with random start positions (pMARS `-F`
   seeds or no `-f`) as well as the fixed series.
3. Competitive '94 hills have long been dominated by composites: a quick-scan
   opening followed by a stone/imp or paper body. Three of the four earlier
   agents submitted a lone scanner. On the sparring pool it lost most against the imp-based
   warriors (many ties and losses), and the agents named this weakness without
   fixing it.
4. Use the whole time budget. Earlier agents stopped after 8 to 28 of 45 minutes.
