# FINAL_CLAIM_AUDIT

Every empirical and methodological sentence in the PDF audited against the
artifact. Numeric verification is in `FINAL_NUMBER_AUDIT.md`; this document checks
*claim strength, scope and attribution*.

For each claim: denominator, numerator, evaluator version, confirmatory vs
exploratory, AB2 in/out, Arm A vs B, comparator-level vs pipeline-level.

---

## Corrections applied in this pass

### Correction 1 — evaluator-contrast claim was too strong (§IV-B)

**Was:** *"That the same edits are fully detected by one implementation and never
by the other is direct evidence that they are genuine semantic differences rather
than arbitrary corruption."*

This overreached. An evaluator contrast establishes evaluator-specific
sensitivity; it cannot establish semantic ground truth, since both implementations
could in principle be wrong about what matters.

**Now:** *"That the same edits are fully detected by one implementation and never
by the other shows that the observed separation is evaluator-specific rather than
an artifact of which cells were perturbed. The semantic standing of the edits
rests instead on the declared operator semantics, their literature grounding, the
admissibility rule, and their transformation-level realisation in Arm A."*

The semantic warrant is now explicitly sourced to the four places that can carry
it, and the evaluator contrast is used only for the narrower claim it supports.

### Correction 2 — "measures" softened to "probe" (abstract and §VI)

**Was (abstract):** *"a meta-evaluation method that measures the second."*
**Now:** *"a meta-evaluation method that provides a controlled way to probe the second."*

**Was (conclusion):** *"Semantic mutation testing measures the second by seeding…"*
**Now:** *"Semantic mutation testing provides a controlled way to probe the second, by seeding…"*

Rationale: Arm B does not establish domain-expert semantic ground truth for every
perturbation, so "measure" overstated what the method delivers for semantic false
acceptance in general.

### Correction 3 — factual error in operator counts (§III-B)

**Was:** *"Seven of the 22 frozen operators admit a faithful output-level
realisation; the remaining 15 are recorded NOT_REALIZABLE."*
**Now:** *"Six of the 22 frozen operators admit a faithful output-level
realisation, yielding seven probes because absence is probed in both directions;
the remaining 16 are recorded NOT_REALIZABLE."*

The old figures did not sum to 22. AB1R is the reverse direction of catalogue
operator AB1, so seven probes realize six distinct operators. No rate, denominator
or statistic is affected. See `FINAL_NUMBER_AUDIT.md` item 32.

---

## Claim-by-claim verification (no further changes needed)

| Claim (§) | Scope check | Verdict |
|---|---|---|
| Abstract: "rejects 34 of 34 arbitrary edits and 0 of 34 structured semantic edits to the same cells" | Arm B, Verified, confirmatory, AB2 **excluded**, comparator-level. Denominator 34 = ME3(10)+AB1(12)+AB1R(12). | Accurate |
| Abstract: "while the other rejects all 68" | default: 34 semantic + 34 control = 68. Correct arithmetic, correct version named. | Accurate |
| Abstract: "two redundant row-set mechanisms" | Verified only; supported by ablation + joint check. Does not claim prevalence. | Accurate |
| Abstract: "cryptographically frozen before execution" | No external registration claimed. | Accurate |
| §I: "An evaluator can become more robust … less discriminative with respect to structured semantic differences." | Framed as a general possibility, not as a measured property of a named system. | Accurate |
| §I novelty sentence | Says prior work documents *which* normalisations reduce false rejection; does not claim prior work ignored false acceptance. | Accurate |
| §II-A two-level split | "semantic mutant" reserved for Arm A; Arm B = "evaluator probes"/"structured semantic-risk perturbations". Verified: `semantic mutant` occurs twice, both definitional/Arm A. | Accurate |
| §II-B: "16 of 22 operators are predicted rejected" | Recomputed from catalogue: 16. | Accurate |
| §II-B: "not as preregistration" | Explicit disclaimer present. | Accurate |
| §III-A: "Two divergent evaluator implementations exist" | Git-ancestry claim removed; no stronger history claim made. | Accurate |
| §III-B Arm A provenance | "repository-provided transformations whose output schemas match their task specifications exactly"; explicit statement that ground-truth reproduction was **not** verified. | Accurate |
| §III-B: "Arm A … is not a prevalence estimate" | Stated in §III-B and repeated in threats. | Accurate |
| §IV-A: SMDR 80.1% / 2.8% | Arm B pooled, both versions named, confined to Table I and one sentence; abstract does not use it. | Accurate |
| §IV-A: "per-operator denominators … carry the claim" | Pre-empts the uneven-applicability objection. | Accurate |
| §IV-B row-set | "not selectively but uniformly blind"; 9 discordant pairs, **no test reported**. | Accurate |
| §IV-B exploratory | Opens "A post-hoc check, not part of the frozen design". | Accurate |
| §IV-C AB2 | Labelled parsing-level, excluded from comparator claim, concedes the reviewer's point, notes it was the one wrong prediction. | Accurate |
| §IV-D mechanisms | Counts match ablation records; joint ablation labelled "a mechanism study, not a population estimate". | Accurate |
| §IV-D: "a single comparator patch would not restore row-set sensitivity" | Follows from redundancy: each mechanism alone is sufficient. Supported by 163 unattributed + 39/39 joint. | Accurate |
| §IV-E Arm A totals | 22 sites, 44 NOT_APPLICABLE, 4 inadmissible, 18 admissible, 6/18 vs 15/18. All recomputed. | Accurate |
| §IV-E witness dependence | Cites ME3 surviving on one subject and rejected on another — a real observed instance, not hypothetical. | Accurate |
| §IV-E anti-circularity | "operator foreknowledge may explain which cells were selected, but cannot explain why the evaluator accepts one edit and rejects the matched edit when both touch the same cells." | Accurate |
| §V-A tone | Uses "trade-off", "discrimination cost", "permissiveness". Verified absent: "broken", "worse", "invalid", "mistake". | Accurate |
| §V-A generalisation | Claims the *mechanisms* are common to execution-based benchmarks and the catalogue transfers; does **not** claim results generalise. | Accurate |
| §V-B threats | Ten threats including corpus provenance, Arm B fidelity, subject provenance, coverage, uneven applicability, witness dependence, operator selection, control comparability, Arm A size. | Accurate |
| §VI conclusion | Claims only: validate both directions; method is a practical audit; evaluator behaviour can erase differences via alignment/normalisation/parsing. No prevalence claim, no "Verified is worse". | Accurate |

## Terminology audit

| Term | Required usage | Observed |
|---|---|---|
| "same cells of the same table" | abstract, matched-control method, RQ2 results, anti-circularity | **5 occurrences**, all four required locations |
| "semantic mutant" | Arm A only | 2 occurrences, both Arm A/definitional |
| "evaluator probe" / "structured semantic-risk perturbation" | Arm B | Used throughout Arm B |
| "validated reference" / "ground-truth transformation" | must not appear | **0 occurrences** |
| "genuine reference transformation" | must not appear | **0 occurrences** |
| "preregistered" | must not appear as a claim | 1 occurrence, in the sentence disclaiming it |
| "common ancestor" | removed | **0 occurrences** |

## Reproducibility verification

- `evaluator/extract.py` re-run: comparison functions **byte-identical** to pinned
  sources (4/4 default, 8/8 Verified); exits non-zero on drift.
- Caches cleared and **Arm B re-run from scratch**: output is **byte-for-byte
  identical** to the previously reported `armB_results.csv`. No result depends on
  a stale intermediate.
- Both evaluator paths use the real CSV round-trip load path.
- Freeze manifest re-verified: 12 frozen files unmodified, corpus Merkle hash
  matches.
