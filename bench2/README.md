# Second-benchmark transfer — EXPLORATORY, ARTIFACT-ONLY

> **Not referenced by the submitted paper and forms no part of its claims.**

A feasibility audit asking whether the frozen Arm B probes transfer, unchanged, to an
independently developed evaluator. See `SECOND_BENCHMARK_FEASIBILITY.md`.

Outcome: the methodology transfers mechanically to Spider 2.0-lite (pinned, local, no
cloud), but only 2 of 7 probes yielded eligible data, giving 16 paired instances with
Δ = 0 and zero discordant pairs. **Underpowered by design as a 15-instance pilot**, and
therefore excluded from the paper rather than reported as a replication attempt.

Retained for transparency: an explored direction, honestly recorded, including its
negative result. Anyone citing the Δ = 0 figure should note it rests on two probes and
sixteen pairs.

One observation worth a follow-up study: the Spider 2.0-lite driver's comparator applies
an unconditional NaN-to-zero mapping, mirroring a mechanism found in the audited
ELT-Bench implementation. The frozen probes could not measure it here for lack of
eligible data, and designing a probe around it would breach the anti-circularity rule
the frozen catalogue exists to enforce.
