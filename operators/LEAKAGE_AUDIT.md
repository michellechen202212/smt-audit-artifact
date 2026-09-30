# Evaluator-internals leakage audit of the exploratory pilot

Deliverable 3 of the brief: *"Identify every way the pilot design used knowledge
of evaluator internals."*

The pilot (`mutants/pilot_operators.py`) was designed **after** reading
`evaluator/verified/eva_stage2.py`. This is a genuine circularity: several
operators were selected because the evaluator's normalization list suggested they
would survive. The pilot is therefore **exploratory/calibration evidence only**,
and the confirmatory catalog (`operators/catalog_v1.yaml`) is derived from
published data-modeling and mutation-testing sources instead.

## Per-operator leakage classification

| ID | Operator | Leakage | Basis |
|----|----------|---------|-------|
| M01 | `DISTINCT` removal | **HIGH** | Chosen after observing `align_dataframes_by_key` deduplicates on an inferred PK |
| M02 | LEFT→INNER join | **HIGH** | Chosen after observing alignment intersects row sets |
| M03 | `COUNT(*)`→`COUNT(DISTINCT)` | none | Standard measure-semantics fault (Kimball grain/additivity) |
| M04 | scale ×100→×1 | **HIGH** | Directly targets `check_percentage_scale` |
| M05 | `= 2017`→`>= 2017` | none | Temporal window fault; also a Tuya ROR instance |
| M06 | tie-break direction | none | Ordering semantics; independent of evaluator |
| M07 | 0→NULL | **HIGH** | Directly targets the unconditional NULL≡0 branch |
| M08 | NULL→0 | **HIGH** | Same branch, opposite direction |
| M09 | `rank`→`row_number` | MEDIUM | Representative-value fault, but tie-row-count interacts with alignment, which was known |
| M10 | threshold 95%→90% | none | Predicate fault; also a Tuya IR/constant instance |

**5 of 10 semantic operators are HIGH leakage, 1 MEDIUM, 4 clean.**

Critically, **all six survivors under the Verified evaluator are HIGH or MEDIUM
leakage** (M01, M02, M04, M07, M08, M09), and **all four clean operators were
rejected** by both evaluators. Read strictly, the pilot's 40% figure is
approximately "the rate at which operators chosen to exploit known normalizations
do exploit them." It demonstrates that the blind spots are *reachable*; it does
**not** estimate how often they are hit by independently-motivated faults.

This is the single largest threat to the paper and must be stated plainly in the
Threats section rather than discovered by a reviewer.

## Consequences for the confirmatory study

1. The 40% number does not appear in the abstract, introduction, or conclusion.
2. The confirmatory catalog is frozen from literature **before** any run, and each
   operator records `known_evaluator_interaction_if_any` as a *prediction made in
   advance*, not a post-hoc explanation.
3. Predictions are registered as directional hypotheses. Operators predicted to
   survive and operators predicted to be rejected are both included; the catalog
   is not filtered by expected outcome.
4. Reporting is stratified by leakage class so a reviewer can read the
   literature-derived subset on its own.
5. The pilot is reported in its own subsection, explicitly labelled exploratory,
   and is used only to motivate the mechanism figure — whose claim (row-set
   semantics can vanish before cell comparison) is a *structural* property of the
   code, verifiable by inspection, and does not depend on the survival rate.
