# Automated blinded check — provenance and limits

> **ARTIFACT-ONLY, EXPLORATORY.** This check is **not referenced by the submitted
> paper** and forms no part of its claims. It is retained here as auxiliary
> robustness material only. The paper's results stand on the pre-specified probes,
> same-cell matched controls, Arm A, and mechanism ablation.

## What this is

The 34 clean comparator pairs (`blind_review/`) were judged by a code-capable
language model in three independent sessions. Records: `automated_blinded_check_102.csv`
(102 rows = 34 cases x 3 sessions; columns `session_id`, `case_id`, `classification`).

The sessions received only `context.txt`, `output_A.csv` and `output_B.csv` per case,
with operator identities, evaluator outcomes, which output was unperturbed, and the
study hypothesis withheld. Blinding is audited in `BLIND_REVIEW_AUDIT.md`.

## Results, recomputed from the records

| Outcome | Count |
|---|---|
| Judged different in all three sessions | 25/34 |
| Judged insufficiently specified in all three | 5/34 |
| Split | 4/34 |
| Ever judged equivalent | 0/34 |

The four split cases are `case_004`, `case_005`, `case_008`, `case_011`. All four are
scale cases, on columns `CURRENCY_RATE`, `RATIO_OF_AMERICAN_CASTS`,
`PERCENT_ELIGIBLE_FREE_MEALS_FOR_GRADES_1_THROUGH_12`, `RATIO_OF_HYDROGEN_ELEMENTS`.

## What it is NOT

**This is not human review and is not described as such anywhere in the paper.**
No expert human review was conducted for this study. A model-based check cannot
establish semantic ground truth; three sessions of one model are not three
independent judges in the sense a human agreement study would provide, and no
inter-rater statistic is computed from them.

A human equivalence study — mirroring the validation prior work applied to the
representation-false-rejection direction — remains future work and is named as such
in the paper's threats section.

## Unrecorded detail

The exact model identity and version used for the three sessions is not recorded in
the artifact, because the sessions were run outside the audit environment. Authors
should supply it for the camera-ready. The reviewer prompt is fixed and included
(`CODEX_REVIEWER_PROMPT.txt`), so the check is re-runnable against any named model.
