# BLIND_REVIEW_AUDIT

Reconstruction and blinding audit for the independent semantic-equivalence
review package. Every case was rebuilt with the same code path as
`analysis/run_armB.py` and checked against the hashes stored in
`results/armB_results.csv`.

## Scope

Clean comparator-level confirmatory subset only: the 34 cases underlying the
headline result. Excluded by construction: AB2, exploratory in-distribution
controls, row-set probes, pilot cases, evaluator outcomes, and the matched
arbitrary controls. The reviewer sees only the paired outputs themselves.

Cases requested: 34. Cases built: 34. Failed: 0.

## Per-case verification

| case | source row located | reconstructed | unperturbed hash | perturbed hash | A/B randomised |
|---|---|---|---|---|---|
| case_001 | YES | YES | YES | YES | YES |
| case_002 | YES | YES | YES | YES | YES |
| case_003 | YES | YES | YES | YES | YES |
| case_004 | YES | YES | YES | YES | YES |
| case_005 | YES | YES | YES | YES | YES |
| case_006 | YES | YES | YES | YES | YES |
| case_007 | YES | YES | YES | YES | YES |
| case_008 | YES | YES | YES | YES | YES |
| case_009 | YES | YES | YES | YES | YES |
| case_010 | YES | YES | YES | YES | YES |
| case_011 | YES | YES | YES | YES | YES |
| case_012 | YES | YES | YES | YES | YES |
| case_013 | YES | YES | YES | YES | YES |
| case_014 | YES | YES | YES | YES | YES |
| case_015 | YES | YES | YES | YES | YES |
| case_016 | YES | YES | YES | YES | YES |
| case_017 | YES | YES | YES | YES | YES |
| case_018 | YES | YES | YES | YES | YES |
| case_019 | YES | YES | YES | YES | YES |
| case_020 | YES | YES | YES | YES | YES |
| case_021 | YES | YES | YES | YES | YES |
| case_022 | YES | YES | YES | YES | YES |
| case_023 | YES | YES | YES | YES | YES |
| case_024 | YES | YES | YES | YES | YES |
| case_025 | YES | YES | YES | YES | YES |
| case_026 | YES | YES | YES | YES | YES |
| case_027 | YES | YES | YES | YES | YES |
| case_028 | YES | YES | YES | YES | YES |
| case_029 | YES | YES | YES | YES | YES |
| case_030 | YES | YES | YES | YES | YES |
| case_031 | YES | YES | YES | YES | YES |
| case_032 | YES | YES | YES | YES | YES |
| case_033 | YES | YES | YES | YES | YES |
| case_034 | YES | YES | YES | YES | YES |

**All 34 cases: source row located, reconstruction exact, both stored hashes matched,**
**A/B assignment randomised.** No case was substituted, dropped, or approximated.

Hash basis: `sha256(df.to_csv(index=False))[:16]`, identical to the function in
`analysis/run_armB.py`. Corpus tables are re-read with the frozen `row_cap` of 2000.

## Blinding measures

| Measure | Status |
|---|---|
| Operator IDs (ME3/AB1/AB1R) absent from package | verified, 0 occurrences |
| Mutation-family names absent | verified |
| Evaluator verdicts absent | verified |
| Predictions / root-cause categories absent | verified |
| Paper conclusions, study name, venue absent | verified |
| Which side is unperturbed not indicated | filenames are `output_A.csv` / `output_B.csv` only |
| Forbidden filenames (`reference`, `mutant`, `semantic`, `control`) | 0 present |
| Manifest carries no operator, family, label or verdict | verified |
| Private key stored outside the reviewer package | `blind_review_private/`, sibling directory |

**A/B balance:** the unperturbed output is A in 16 cases and B in 18.
Assignment is drawn from a fixed seed (20260929), so the package is reproducible,
and the mapping appears only in `blind_review_private/answer_key.csv`.

## Structural leak found and fixed

The first build assigned case IDs in sorted order, which placed the two cases
derived from the same source table at adjacent IDs (15 such adjacencies). A
reviewer could have inferred the study design from adjacency alone: two
near-identical tables differing in opposite directions on the same column.
Case order is now shuffled under a fixed seed with the constraint that no two
adjacent cases share a source table. **Adjacent same-table pairs: 0.**

## Bug found and fixed during build

Corpus column headers are upper-cased by the warehouse while the public task
specification uses lower-case names, so the first build silently fell back to
"Column semantics beyond its name and datatype are not specified." for every
column. The lookup is now case-insensitive and **337 of 337 columns carry their
verbatim documented description**. Had this gone unnoticed, the package would
have been misleadingly context-poor and the review correspondingly uninformative.

## Context policy

`context.txt` contains only: the documented record-domain sentence, the column
list with datatypes, and each column's verbatim description from the public task
specification. Where no description exists, the prescribed sentence is used
instead. No semantic meaning is inferred, and no column is singled out as the
one that differs.

**Disclosure that matters for interpretation:** 53 column descriptions in the
package state NULL handling verbatim, e.g. "replace NULL values with 0". This is
genuine public specification text and the brief directs that documented NULL or
zero semantics be included, so it is included. It does mean some cases carry
stronger documented grounding than others, and a reviewer may find those easier
to judge in either direction. Suppressing it would have been cherry-picking
context to make the pairs look harder than the public specification makes them.

## Leakage scan

Recursive scan over `blind_review/` for: AB1, AB1R, ME3, GC1, PP1, RV1, AB2,
semantic, mutant, reference, Verified, default evaluator, SURVIVED, rejected,
prediction, root_cause, FORGE, SMDR, CMDR, Delta, operator_id, mutation_family,
witness, admissible, confirmatory, hypothesis, Arm A, Arm B, ELT-Bench,
"scale mutation", "percentage points", fraction, absence, missingness.

Result: **no hit in any reviewer-facing prose, header, manifest row or filename.**
Hits occur only in two places, both benign:

1. **Inside the data itself.** Cases drawn from a discussion-forum corpus contain
   post text using the ordinary English words *perturbation*, *prediction*,
   *family*, *hypothesis* and *absence*; one case contains a school named "Delta
   Vista High". These are benchmark data values, not study metadata.
2. **The prescribed fallback sentence** "Column semantics beyond its name and
   datatype are not specified", which the brief specifies verbatim.

CSV headers and filenames were also inspected by hand: the only filenames in the
package are `README_FOR_REVIEWER.txt`, `manifest.csv`, `context.txt`,
`output_A.csv`, `output_B.csv`.

## What this review can and cannot establish

This is an **independent LLM sanity check**, not human validation, and must not be
described as human validation in the paper or anywhere else. It can indicate
whether an independent model, given only documented context, reads the paired
outputs as carrying different meaning. It cannot establish domain-expert
consensus, and a favourable result does not substitute for the human
equivalence study named as future work.

Because the review runs on the 34 clean comparator cases only, its outcome speaks
to those cases and to no other part of the study.
