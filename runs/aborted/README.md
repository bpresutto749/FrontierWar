Runs D and E (Claude Opus 5.5) were killed after about 14 of 45 minutes by an API
quota error (HTTP 429), not by the agents. Their partial submissions are kept here
for transparency. They are not scored and not counted; they were replaced by
fresh runs D2 and E2 with the same instructions.

Disclosure: while testing the training pipeline on CPU, these two partial files were
scored once on the *training* hill (0.672 and 0.681), along with every other warrior
in runs/. They were never scored on the hidden evaluation hill.
