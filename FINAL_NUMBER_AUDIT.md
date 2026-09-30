# FINAL_NUMBER_AUDIT

Every headline number recomputed from raw per-instance records
(`results/*.csv`) by `results/number_audit_raw.txt`, then compared against the
paper, `results/TABLES.md` and `README.md`. **Source of truth is the raw
per-instance record**, never the prettier value.

Legend: **C** = confirmatory, **E** = exploratory.

| # | Claim | Raw source | Recomputed | Paper | Status |
|---|---|---|---|---|---|
| 1 | Clean comparator, Verified, semantic rejected (C) | `armB_results.csv`, ops ME3+AB1+AB1R | 0/34 | 0/34 | **PASS** |
| 2 | Clean comparator, Verified, controls rejected (C) | same | 34/34 | 34/34 | **PASS** |
| 3 | Exact two-sided paired p, 34 pairs (C) | 34 discordant, b01=34, b10=0 | 1.16415e-10 | $1.2\times10^{-10}$ | **PASS** |
| 4 | Clean comparator, default, both conditions (C) | same | 34/34 and 34/34 | 34/34 both | **PASS** |
| 5 | Exploratory in-dist, Verified (E) | `exploratory_indist_controls.csv` | 0/32 vs 32/32 | 0/32 vs 32/32 | **PASS** |
| 6 | Exploratory in-dist exact p (E) | 32 discordant, one direction | 4.65661e-10 | $4.7\times10^{-10}$ | **PASS** |
| 7 | Exploratory in-dist, default (E) | same | 32/32 both | 32/32 both | **PASS** |
| 8 | Arm A default semantic/control (C) | `armA_expanded.csv` | 16/18, 18/18 | 16/18, 18/18 | **PASS** |
| 9 | Arm A Verified semantic/control (C) | same | 6/18, 15/18, Δ +50.0 | 6/18, 15/18, Δ +50.0 | **PASS** |
| 10 | Arm A NOT_APPLICABLE | same | 44 | 44 | **PASS** |
| 11 | Arm A INADMISSIBLE | same | 4 | 4 | **PASS** |
| 12 | Arm A admissible mutants | same | 18 | 18 | **PASS** |
| 13 | Arm A operator sites applicable | same | 22 | 22 | **PASS** |
| 14 | Arm A subjects | same | 3 | 3 | **PASS** |
| 15 | Ablation: key intersection | `mechanism_ablation.csv` | 150 | 150 | **PASS** |
| 16 | Ablation: null/zero equivalence | same | 24 | 24 | **PASS** |
| 17 | Ablation: duplicate removal | same | 12 | 12 | **PASS** |
| 18 | Ablation: percentage-scale | same | 10 | 10 | **PASS** |
| 19 | Total survivors analysed | same | 359 (150+24+12+10+163) | 359 | **PASS** |
| 20 | GC1 survivors / unattributed | same | 174 / 163 | 174 / 163 | **PASS** |
| 21 | Joint ablation (E, mechanism sample) | joint-ablation check, seed 7, 40 tables | 39/39 | 39/39 | **PASS** |
| 22 | Population-loss example | `shipping.drivers`, Verified | 11 → 9, aligned 9/9, MATCH | 11 → 9 → 9, match | **PASS** |
| 23 | Corpus tables / models | `corpus/` | 180 / 90 | 180 / 90 | **PASS** |
| 24 | Frozen operators / families | `catalog_v1.yaml` | 22 / 6 | 22 / 6 | **PASS** |
| 25 | Advance predictions "reject" | same | 16 of 22 | 16 of 22 | **PASS** |
| 26 | Prediction accuracy | `armB_results.csv` | 362/468 = 77.4% | 77.4% | **PASS** |
| 27 | Incorrect prediction was AB2 | same | AB2 0/93 correct; all others ≥75% | AB2 | **PASS** |
| 28 | AB2, both evaluators, semantic | same | 0/93 and 0/93 | 0/93 each | **PASS** |
| 29 | Row-set bin, Verified (C) | same | 13/341 vs 22/341, 9 discordant | 13/341, 22/341, Δ +2.6, 9 disc. | **PASS** |
| 30 | Pooled Arm B SMDR | same | 375/468, 13/468 | 80.1%, 2.8% (Table I only) | **PASS** |
| 31 | Pooled Arm B CMDR | same | 468/468, 147/468 | 100%, 31.4% | **PASS** |
| 32 | Arm B realizable operators | `witness_rules.yaml` | **6 operators / 7 probes / 16 not realizable** | was "7 of 22 … remaining 15" | **FAIL → CORRECTED** |

## Discrepancy found and corrected

**Item 32.** The paper stated *"Seven of the 22 frozen operators admit a faithful
output-level realisation; the remaining 15 are recorded NOT_REALIZABLE."* Both
figures were wrong, and they did not sum to 22.

The frozen `witness_rules.yaml` lists **seven probes** (GC1, PP1, RV1, ME3, AB1,
AB1R, AB2) but AB1R is explicitly recorded as the reverse direction of catalogue
operator **AB1**, so only **six distinct catalogue operators** are realized.
The `not_realizable_at_output_level` list contains **16** entries.
Check: 6 + 16 = 22. ✓

Corrected text: *"Six of the 22 frozen operators admit a faithful output-level
realisation, yielding seven probes because absence is probed in both directions;
the remaining 16 are recorded NOT_REALIZABLE…"*

No result, rate, denominator or statistic changes — the 468 admissible instances
were always counted per probe, not per operator. Only the descriptive sentence was
wrong.

## Statistical audit

- **34-pair confirmatory result.** Exact two-sided binomial (sign) test on
  discordant pairs: b01 = 34, b10 = 0, p = 1.16415e-10. Appropriate — paired,
  binary, and exact rather than an asymptotic approximation. The earlier
  $\chi^2$ figure has been retired in favour of the exact test.
- **32-pair exploratory result.** Same exact paired test: b01 = 32, b10 = 0,
  p = 4.65661e-10. Labelled exploratory in the paper, tables and README.
- **Row-set probes.** 9 discordant pairs, below the pre-specified threshold of 20.
  **No inferential test is reported**; descriptive counts only. This is stated in
  the paper.
- No chi-square approximation remains anywhere in the paper.

## Confirmatory vs exploratory labelling

| Result | Label in paper |
|---|---|
| 0/34 vs 34/34 comparator | confirmatory (unlabelled = default) |
| Arm A 18 mutants | confirmatory, "fidelity anchor" |
| Row-set 13/341 | confirmatory, no test |
| AB2 0/93 | confirmatory, reported as parsing-level, excluded from comparator claim |
| In-distribution controls | **"A post-hoc check, not part of the frozen design"** |
| Joint ablation 39/39 | **"a mechanism study, not a population estimate"** |
