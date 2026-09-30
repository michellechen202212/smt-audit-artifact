# Analysis plan (FROZEN before the confirmatory run)

## Metrics
SMDR_v = semantic instances rejected by v / admissible semantic instances
CMDR_v = matched control instances rejected by v / admissible control instances
Delta_v = CMDR_v - SMDR_v

Experimental unit: (model/table, operator, witness, evaluator_version).
No rate is reported without its evaluator version.

## Required stratifications
1. semantic family
2. evaluator version (default / Verified)
3. PK-inference / alignment regime (Verified: inferred id-shaped key vs all-column fallback)
4. arm (B output-level / A SQL-level)
5. operator provenance (literature-derived confirmatory / pilot-derived exploratory)
6. normalization mechanism implicated (from ablation)

## Denominators
Report per operator: applicable to N tables; admissible on K instances; rejected D/K.
Do NOT manufacture a single aggregate rate if applicability differs substantially
across families; report the family matrix and a pooled figure only alongside it.

## Statistics
Primary reporting is exact counts plus Wilson 95% intervals.
McNemar is used only on genuinely paired (semantic, control) instances on the same
table and column, and only if discordant pairs >= 20. Otherwise descriptive only.
No test is run on the exploratory pilot (n=15).

## Mechanism attribution (ablation)
A root-cause claim is valid only if all three hold:
 (1) the instance survives with the mechanism enabled;
 (2) the instance is rejected when that mechanism alone is disabled;
 (3) no other evaluator behaviour is altered by the ablation.
Each ablation is a single-function patch, verified by diff against the pinned
comparator. Instances failing (2) are recorded `unattributed`, never reassigned
by interpretation.

## Prediction scoring
Advance predictions are in operator_catalog.csv (`advance_prediction`).
Report accuracy overall and split by whether the operator has pilot history.

## Pre-committed interpretation
Delta_v > 0 supports selective semantic insensitivity.
Delta_v approximately 0 refutes selectivity; the finding would then be general
permissiveness, and the paper must say so.
