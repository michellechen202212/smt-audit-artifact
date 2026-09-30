# Result tables (revised)

Corpus: 180 released ELT-Bench output tables, 90 models, pinned at c99baa6. Row cap 2000.

## Table A - CLEAN comparator-level selectivity (AB2 excluded)

Operators ME3, AB1, AB1R. Semantic and control edits touch the **same cells of the same table**.

| evaluator | semantic rejected | control rejected | Delta | discordant | exact two-sided p |
|---|---|---|---|---|---|
| default | 34/34 (100.0%) [89.8,100.0] | 34/34 (100.0%) [89.8,100.0] | +0.0 | 0 | 1 |
| verified | 0/34 (0.0%) [0.0,10.2] | 34/34 (100.0%) [89.8,100.0] | +100.0 | 34 | 1.16e-10 |

Per operator (Verified): ME3 0/10 vs 10/10; AB1 0/12 vs 12/12; AB1R 0/12 vs 12/12.
Per operator (default): all three 34/34 semantic and 34/34 control.


## Table B - AB2 parsing-level erasure (reported separately)

| evaluator | semantic rejected | control rejected |
|---|---|---|
| default | 0/93 (0.0%) [0.0,4.0] | 93/93 (100.0%) [96.0,100.0] |
| verified | 0/93 (0.0%) [0.0,4.0] | 91/93 (97.8%) [92.5,99.4] |

`'N/A'` is coerced back to NaN by `read_csv` during the evaluator's own load, under BOTH
implementations. Mechanism: `csv_na_coercion`, upstream of the comparator. Excluded from the
comparator claim; retained in the frozen dataset.


## Table C - Arm B full detection by operator

| op | family | bin | n | SMDR default | SMDR Verified |
|---|---|---|---|---|---|
| GC1 | grain_cardinality | row_set | 175 | 175/175 (100.0%) [97.9,100.0] | 1/175 (0.6%) [0.1,3.2] |
| PP1 | population_predicates | row_set | 162 | 162/162 (100.0%) [97.7,100.0] | 11/162 (6.8%) [3.8,11.7] |
| RV1 | representative_value | row_set | 4 | 4/4 (100.0%) [51.0,100.0] | 1/4 (25.0%) [4.6,69.9] |
| ME3 | measures | value | 10 | 10/10 (100.0%) [72.2,100.0] | 0/10 (0.0%) [0.0,27.8] |
| AB1 | absence | value | 12 | 12/12 (100.0%) [75.7,100.0] | 0/12 (0.0%) [0.0,24.3] |
| AB1R | absence | value | 12 | 12/12 (100.0%) [75.7,100.0] | 0/12 (0.0%) [0.0,24.3] |
| AB2 | absence | value(parsing) | 93 | 0/93 (0.0%) [0.0,4.0] | 0/93 (0.0%) [0.0,4.0] |
| **POOLED default** | | | 468 | | **375/468 (80.1%) [76.3,83.5]** |
| **POOLED verified** | | | 468 | | **13/468 (2.8%) [1.6,4.7]** |

Row-set bin (Verified): semantic 13/341, control 22/341, Delta +2.6, 9 discordant pairs -> no inferential test.
Uniform rather than selective blindness: row-set differences are erased regardless of semantic content.


## Table D - Arm A expanded (three repository-provided transformations)

Output schemas match their task specifications exactly; **not** verified against ground-truth CSVs.

| subject | op | family | default | Verified | matched control (Verified) |
|---|---|---|---|---|---|
| shipping.drivers | GC1 | grain_cardinality | rejected | SURVIVED | rejected |
| shipping.drivers | ME1 | measures | rejected | rejected | rejected |
| shipping.drivers | ME3 | measures | rejected | SURVIVED | rejected |
| shipping.drivers | PP1 | population_predicates | rejected | SURVIVED | SURVIVED |
| shipping.drivers | PP2 | population_predicates | - | - | INADMISSIBLE:equivalent_on_witness |
| shipping.drivers | AB1 | absence | rejected | SURVIVED | rejected |
| shipping.drivers | RV1 | representative_value | rejected | SURVIVED | rejected |
| shipping.drivers | RV2 | representative_value | rejected | rejected | rejected |
| shipping.drivers | TM2 | temporal | rejected | rejected | rejected |
| retails.customers | GC1 | grain_cardinality | - | - | INADMISSIBLE:equivalent_on_witness |
| retails.customers | ME1 | measures | rejected | rejected | rejected |
| retails.customers | PP1 | population_predicates | rejected | SURVIVED | SURVIVED |
| retails.customers | PP2 | population_predicates | rejected | rejected | rejected |
| retails.customers | AB1 | absence | rejected | SURVIVED | rejected |
| retails.customers | AB2 | absence | SURVIVED | SURVIVED | rejected |
| retails.customers | RV1 | representative_value | rejected | SURVIVED | rejected |
| retails.customers | RV2 | representative_value | - | - | INADMISSIBLE:equivalent_on_witness |
| retails.nations | ME1 | measures | - | - | INADMISSIBLE:equivalent_on_witness |
| retails.nations | ME3 | measures | rejected | rejected | rejected |
| retails.nations | PP1 | population_predicates | rejected | SURVIVED | SURVIVED |
| retails.nations | AB1 | absence | rejected | SURVIVED | rejected |
| retails.nations | AB2 | absence | SURVIVED | SURVIVED | rejected |

**default: SMDR 16/18 (88.9%) [67.2,96.9], CMDR 18/18 (100.0%) [82.4,100.0], Delta +11.1 pts**

**verified: SMDR 6/18 (33.3%) [16.3,56.3], CMDR 15/18 (83.3%) [60.8,94.2], Delta +50.0 pts**

Subjects attempted 3, usable 3. NOT_APPLICABLE 44, INADMISSIBLE 4, admissible mutants 18.


## Table E - EXPLORATORY in-distribution control robustness

Post-hoc, not part of the frozen design. Controls replace the SAME cells with a value observed
elsewhere in the same column (or a permutation of it), preserving dtype and empirical support.

| evaluator | pairs | semantic rejected | in-dist control rejected | Delta | discordant | exact p |
|---|---|---|---|---|---|---|
| default | 32 | 32/32 (100.0%) [89.3,100.0] | 32/32 (100.0%) [89.3,100.0] | +0.0 | 0 | 1 |
| verified | 32 | 0/32 (0.0%) [0.0,10.7] | 32/32 (100.0%) [89.3,100.0] | +100.0 | 32 | 4.66e-10 |

**The separation does not weaken.** Out-of-distribution control values cannot explain it.


## Table F - Mechanism ablation (Verified)

| mechanism | survivors flipped to rejected |
|---|---|
| no single mechanism (redundant pair) | 163 |
| alignment_rowset | 150 |
| null_zero_equivalence | 24 |
| dedup_normalize | 12 |
| scale_normalization | 10 |

| op | survivors | single-mechanism attributed | unattributed |
|---|---|---|---|
| GC1 | 174 | 11 | 163 |
| PP1 | 151 | 151 | 0 |
| AB1 | 12 | 12 | 0 |
| AB1R | 12 | 12 | 0 |
| ME3 | 10 | 10 | 0 |

`dedup_normalize` and `alignment_rowset` are each independently sufficient to erase exact row
duplication, so single-mechanism ablation cannot attribute 163/174 GC1 survivors. Joint ablation
rejects 39/39 in a random 40-table sample (mechanism study, **not** a population estimate).
Consequence: a single comparator patch would not restore row-set sensitivity.
