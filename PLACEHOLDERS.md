# Final placeholder inventory

**Status: the paper contains ZERO unfilled placeholders.** `grep -c 'PH{' paper/main.tex` → 0.
Every number in `paper/main.tex` traces to a file in `results/`.

## Filled from the confirmatory run

| Value | Source |
|---|---|
| SMDR default 80.1% [76.3,83.5]; Verified 2.8% [1.6,4.7] | `results/armB_results.csv` (n=468 each) |
| CMDR default 100%; Verified 31.4% [27.4,35.8] | same |
| Δ default +19.9; Verified +28.6 | same |
| value-bin: 0/127 semantic vs 125/127 control, Δ +98.4, χ²=123.0 | `results/TABLES.md` Table 6 |
| row-set bin: 13/341 vs 22/341, Δ +2.6, 9 discordant (no test) | same |
| per-operator n and rates (175/162/4/10/12/12/93) | `results/TABLES.md` Table 3 |
| mechanism attribution 150/24/12/10 | `results/mechanism_ablation.csv` |
| joint ablation 39/39 | `results/ablation.log` + joint check |
| figure counts 11 → 9 → 9, pk=DRIVER_ID | measured instance, shipping.drivers |
| Arm A 9/10 admissible; Verified 3/9 vs 8/9 (Δ +55.6); default 8/9 vs 9/9 | `results/armA_results.csv` |
| prediction accuracy 77.4% | `results/LEAKAGE_TABLE.md` |
| leakage strata 0/93 vs 13/375 | same |

## Deliberately excluded

| Value | Reason |
|---|---|
| Pilot SMDR 40%, CMDR 100%, Δ 60 pts | Exploratory; 5/10 operators HIGH evaluator-internals leakage. Appears nowhere in the paper. |

## Outstanding empirical work (not placeholders — optional strengthening)

| Item | Effect | Cost |
|---|---|---|
| Arm A over 3–4 references (`example/retails`) | n 9 → ~30; removes the single-subject objection | ~1 day |
| Re-run Arm B on distributed ground-truth CSVs | retires the corpus-provenance threat; corpus path change only | ~1 hour once downloaded |
| Between-table verdict variance | quantifies witness dependence | derivable from existing CSV |
