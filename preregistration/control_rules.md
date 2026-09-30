# Matched conventional control construction (FROZEN)

Matching is on **observable output**, never on SQL syntax.

1. **Same target.** The control perturbs the same column(s) — or, for row-set
   probes, the same number of rows — as its semantic partner.
2. **Same magnitude bin.** Bins: `row_set`, `value_gt_1pct`, `value_le_1pct`.
   The control must fall in its partner's bin.
3. **Same admissibility rule**, evaluated independently of both evaluators.
4. **Operator pool** (Tuya et al. 2007): ROR, AOR, LCR, IR, SC/SDL.
5. **No declared semantic property.** A control must not realize any
   `expected_semantic_distinction` from the frozen catalogue. Controls use
   arbitrary constants (999999, 'ZZZQ') or arbitrary scale factors (×1.5)
   precisely so they carry no data-modelling meaning.
6. **Pairing preserved.** Each control carries its partner's `matched_control_id`
   and is analysed paired.
7. **Disclosed overlap.** Tuya's NL category already mutates NULL handling, so
   absence-family probes are matched against non-NULL controls (IR fills) only.
   Residual comparability risk is reported as a threat.
8. **Unmatched probes are reported, not dropped.** If no control in the same bin
   can be constructed, the instance is recorded with `matched_control_id = NONE`
   and excluded from CMDR but retained in SMDR, with counts reported.
