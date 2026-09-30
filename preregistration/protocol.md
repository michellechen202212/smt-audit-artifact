# Preregistration-ready protocol — Semantic Mutation Audit of ELT-Bench evaluators

Status: ready to register. **Nothing below may change after registration except
by a dated amendment recorded in this file.**

## 1. Objective

Measure whether execution-based data-engineering benchmark evaluators can
distinguish semantically different but syntactically valid transformations, and
identify the evaluator mechanisms responsible for any failures.

## 2. Subjects (pinned)

| Factor | Value |
|---|---|
| Repository | `github.com/uiuc-kang-lab/ELT-Bench` |
| Default evaluator | commit `fcf3129df49ce5ce63ff46b2bbbbba1eaf9ec055` (branch `elt_bench++`, 2026-08-03), `evaluation/eva_stage2.py`, blob `c57aac34`, sha256 `4b024391…` |
| Verified evaluator | commit `c99baa6eaef9c258ebfa8bd675ea7d37a7470252` (`refs/pull/18/head`, 2026-06-12), `evaluation/eva_stage2.py`, blob `09a36dba`, sha256 `0487c53f…` |
| Relationship | **No common ancestor**; neither ref is an ancestor of the other |
| Naming | "default evaluator" / "Verified evaluator". Neither is called *the official evaluator*. |

Evaluator version is a first-class factor. No detection rate is ever reported
without it.

## 3. Hypotheses

- **H1 (RQ1).** Both evaluators reject fewer than 100% of witness-validated
  semantic mutants. Directional; magnitude unspecified.
- **H2 (RQ2).** For at least one evaluator version, `Delta_v = CMDR_v − SMDR_v > 0`
  — i.e. detection is *selectively* lower for semantic mutants than for matched
  conventional mutants. This is the falsifiable core: `Delta_v ≈ 0` refutes
  selectivity and reduces the finding to "the evaluator is uniformly tolerant."
- **H3 (RQ3).** Surviving semantic mutants concentrate in identifiable
  alignment/normalization mechanisms, and the concentration differs between the
  two versions.

Per-operator advance predictions are registered in `operators/catalog_v1.yaml`
(`known_evaluator_interaction_if_any`): 6 of 22 predicted to survive, 16
predicted to be rejected. Prediction accuracy is itself reported.

## 4. Design

Two arms, never pooled into a single headline number.

### Arm A — SQL-level semantic mutation (high fidelity, small n)

Unit: `(reference, operator, witness, evaluator_version)`.

Reference admission, in order:
1. **Published references.** `evaluation/shipping/drivers.sql` (PR#18 only) and
   `example/retails/{customers,nations}.sql`.
2. **Recovered references.** For a preregistered random sample of models,
   reconstruct SQL from `data_model.yaml` + source schemas. A recovered reference
   is admissible **only if it reproduces the benchmark ground-truth CSV exactly
   under the evaluation state**, compared with exact equality (not the
   evaluator's own tolerant comparator — otherwise recovery inherits the
   permissiveness under test).
3. Report: attempted / recovered / rejected, with rejection reasons.

Known limitation registered in advance: `shipping/drivers.sql` matches its
`data_model.yaml` column specification exactly (8/8, ordered) but its **output has
not been verified against the ground-truth CSV**. It is treated as *recovered,
pending verification* until that check is run, not as a published reference.

### Arm B — evaluator probes over ground-truth outputs (broad coverage)

Unit: `(model, operator, evaluator_version)`. Applied to ground-truth outputs
across the 203 data models.

These are **semantic output perturbations / evaluator probes**, never called SQL
mutations. Each must carry an explicit declared semantic distinction from the
catalog; arbitrary CSV edits are excluded by construction. Arm B answers only:
*how often do alignment/normalization rules erase a declared semantic
difference?* It does not establish that each perturbation arises from a plausible
query.

Probes are admitted only where the model's schema satisfies the operator's
`witness_requirements` (e.g. AB1 needs a nullable column; RV1 needs a tie).
Applicability counts per operator are reported.

## 5. Witness methodology

Witness structural requirements are fixed a priori per operator in the catalog.
Two phases, strictly separated:

- **Calibration (complete, closed).** The discrimination loop — extend the
  witness until an operator is admissible — was used in the exploratory pilot and
  is now finished. The pilot witness is archived as `witnesses/witness_w1.py`.
- **Confirmatory (binding).** Witnesses are generated from the frozen structural
  requirements **before** any evaluator is run, and are **never modified in
  response to an evaluator outcome**. An operator that is inadmissible on its
  witness is reported as inadmissible; the witness is not repaired.

Witness generation for Arm A references: parse each reference with SQLGlot,
extract join keys, grouping keys, ordering keys and nullable columns, and emit a
minimal state satisfying every applicable operator's requirements. Deterministic,
seeded, released with the artifact.

## 6. Admissibility

A semantic mutant instance is admissible iff:
1. reference and mutant both execute;
2. the mutant parses as valid SQL;
3. a witness state `I_w` satisfies `P(I_w) ≠ P'(I_w)` under **exact** comparison
   (not the evaluator under test);
4. exactly one declared semantic property is changed — enforced by single-anchor
   edits, with anchor uniqueness checked mechanically, and confirmed by a second
   reader for every admitted instance.

Arm B analogue: the perturbation must realise the operator's declared
`expected_semantic_distinction`, checked by exact comparison against the
unperturbed ground truth.

## 7. Metrics

```
SMDR_v = (validated semantic mutant instances rejected by evaluator v)
         / (validated semantic mutant instances)

CMDR_v = (matched conventional mutant instances rejected by evaluator v)
         / (validated conventional mutant instances)

Delta_v = CMDR_v - SMDR_v
```

Stratify by: semantic family; PK-inference regime (inferred `_id`-shaped key vs
all-column fallback); arm; implicated normalization; and leakage class
(literature-derived vs pilot-derived).

Statistics: report exact counts and Wilson intervals. McNemar only on genuinely
paired semantic/control instances on the same reference, column and witness, and
only if ≥20 discordant pairs; otherwise descriptive counts only. No test is run
on the pilot's n=15.

## 8. Analysis plan (fixed in advance)

1. Per-arm, per-version SMDR/CMDR/Delta with intervals.
2. Family × version survival matrix.
3. Root-cause attribution: each survivor assigned to exactly one mechanism
   (`alignment_rowset`, `null_zero_equivalence`, `scale_normalization`,
   `tolerance`, `boolean_normalization`, `timestamp_truncation`, `other`) by
   ablating that mechanism and re-running. Attribution is *mechanical*, not
   interpretive.
4. Prediction scoring: registered vs observed.
5. Leakage-stratified re-analysis using literature-derived operators only.

## 9. Stopping rule

Arm B runs to completion over all applicable (model, operator) pairs. Arm A runs
over all admissible references. No interim peeking is used to adjust operators,
witnesses, or metrics.

## 10. Deviations register

Any departure from this protocol is recorded here with a date and rationale, and
reported in the paper.

| Date | Deviation | Rationale |
|---|---|---|
| — | — | — |
