# Semantic Mutation Testing for Auditing AI Data-Engineering Benchmarks — artifact

Meta-evaluation of execution-based benchmark evaluators. Runs locally; **no cloud data
warehouse required**.

## Quick start

```bash
pip install duckdb pandas pyyaml           # see environment.lock for pinned versions
bash fetch_sources.sh                      # pinned upstream sources + corpus, hash-verified
python3 evaluator/extract.py               # byte-identical comparator extraction (non-zero exit on drift)
python3 analysis/run_armB.py               # Arm B, 180 tables          (~4 min)
python3 analysis/run_armA_expanded.py      # Arm A, 3 transformations
python3 analysis/run_ablation.py           # mechanism ablation          (~5 min)
python3 analysis/analyze.py                # pooled + stratified rates
```

## What is not redistributed here, and why

The audited repository publishes **no top-level LICENSE**, so no license grant covers
redistributing its evaluator source, key metadata, reference SQL, or released output
tables. `fetch_sources.sh` reconstructs all of them from pinned commits and verifies each
against the hashes in `repo_commit_manifest.json` and `preregistration/freeze_manifest.json`.
This is also stronger evidence than a snapshot would be: the audit demonstrably runs
against the benchmark's own code.

| Fetched, not committed | Source |
|---|---|
| `evaluator/default/`, `evaluator/verified/` | `evaluation/eva_stage2.py` at two pinned commits |
| `references/*.reference.sql` | three repository-provided transformations |
| `corpus/` | 180 released output tables (Merkle-verified, 90 models) |

## Layout

```
preregistration/   protocol, operator catalogue, advance predictions, witness rules,
                   control rules, evaluator manifest, freeze_manifest.json (hashes
                   computed BEFORE the confirmatory run)
operators/         frozen catalogue v1.0 (22 operators, 6 families) + leakage audit
witnesses/         witness states built from the frozen structural requirements
references/        DuckDB ports of the three transformations (dialect-only edits)
mutants/           exploratory pilot operators (calibration only)
analysis/          Arm B, Arm A, ablation, in-distribution controls, analysis
results/           per-instance CSVs, TABLES.md, LEAKAGE_TABLE.md
evaluator/         extract.py (fidelity check); pinned sources land here after fetch
paper/main.tex     submitted source
fetch_sources.sh   pinned-source fetch + hash verification
```

Audit records: `FINAL_NUMBER_AUDIT.md` (every headline number recomputed from raw
records), `FINAL_CLAIM_AUDIT.md`, `FINAL_REFERENCE_AUDIT.md`, `BLIND_REVIEW_AUDIT.md`,
`PLACEHOLDERS.md`, `PROTOCOL.md` (including the deviations register).

## Freezing, not preregistration

`preregistration/` means the protocol, operator catalogue, advance predictions, witness
rules and analysis plan were **cryptographically frozen by local hash before the
confirmatory run**. They were **not** registered with an external timestamped service, and
the paper does not claim otherwise.

## Auxiliary, artifact-only material

Neither item below is referenced by the paper, and neither forms part of its claims. Both
are retained for transparency.

| Path | What it is |
|---|---|
| `results/automated_blinded_check_102.csv`, `results/AUTOMATED_BLINDED_CHECK.md`, `CODEX_REVIEWER_PROMPT.txt`, `analysis/build_blind_review.py` | Blinded **model-based** sanity check of the 34 headline pairs: 102 judgements over three sessions. Exploratory. **Not human review** — no expert human review was conducted for this study. |
| `bench2/` | Feasibility audit of transferring the frozen probes to a second comparator (Spider 2.0-lite). Concluded against inclusion; 2 of 7 probes yielded data, 16 pairs, Δ = 0. Underpowered by design; see `bench2/README.md`. |

## Scope and naming

The two audited implementations are called **default** and **Verified**; neither is
described as canonical. Arm A subjects are **repository-provided transformations whose
output schemas match their task specifications** — their outputs were not verified against
the benchmark ground-truth CSVs. Arm B cases are **evaluator probes**; *semantic mutant* is
reserved for Arm A, where an SQL edit plus witness establishes the distinction.

The audited corrections were introduced for documented reasons and validated against human
judgement. This artifact measures a second error direction that prior validation did not
quantify; it is not a claim that those corrections were mistakes.
