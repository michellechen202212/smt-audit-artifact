#!/usr/bin/env bash
# Fetches the pinned third-party sources this artifact does NOT redistribute,
# and verifies each against the hash recorded in repo_commit_manifest.json.
#
# Rationale: the audited repository ships no top-level LICENSE, so no license
# grant covers redistributing its evaluator source, key metadata or reference
# SQL. This script reconstructs them from the pinned commits instead, which is
# also stronger evidence that the audit ran against the benchmark's real code.
set -euo pipefail

EB=https://github.com/uiuc-kang-lab/ELT-Bench.git
DEFAULT_SHA=fcf3129df49ce5ce63ff46b2bbbbba1eaf9ec055   # branch elt_bench++
VERIFIED_SHA=c99baa6eaef9c258ebfa8bd675ea7d37a7470252  # refs/pull/18/head

mkdir -p .src evaluator/default evaluator/verified references corpus
if [ ! -d .src/eltbench/.git ]; then
  git clone -q --filter=blob:none "$EB" .src/eltbench
  git -C .src/eltbench fetch -q origin "refs/pull/18/head:pr18"
fi
G="git -C .src/eltbench"

$G show "$DEFAULT_SHA:evaluation/eva_stage2.py"  > evaluator/default/eva_stage2.py
$G show "$DEFAULT_SHA:evaluation/sort_key.json"  > evaluator/default/sort_key.json
$G show "$VERIFIED_SHA:evaluation/eva_stage2.py" > evaluator/verified/eva_stage2.py
$G show "$VERIFIED_SHA:evaluation/shipping/drivers.sql" > references/shipping__drivers.reference.sql
$G show "$VERIFIED_SHA:example/retails/customers.sql"   > references/retails__customers.reference.sql
$G show "$VERIFIED_SHA:example/retails/nations.sql"     > references/retails__nations.reference.sql

echo "--- verifying against repo_commit_manifest.json ---"
python3 - <<'PY'
import json, hashlib, sys
m = json.load(open("repo_commit_manifest.json"))
exp = {"evaluator/default/eva_stage2.py":  m["evaluators"]["default"]["sha256"],
       "evaluator/verified/eva_stage2.py": m["evaluators"]["verified"]["sha256"],
       "references/shipping__drivers.reference.sql": m["reference_sql"]["sha256"]}
bad = 0
for p, e in exp.items():
    a = hashlib.sha256(open(p, "rb").read()).hexdigest()
    ok = a == e
    bad += not ok
    print(f"  {'OK  ' if ok else 'FAIL'} {p}")
sys.exit(1 if bad else 0)
PY

echo "--- Arm B corpus (180 released output tables) ---"
BASE="reproducibility_artifacts/swe-agent-predictions"
$G ls-tree -r --name-only "$VERIFIED_SHA:$BASE" | grep '\.csv$' | while read -r rel; do
  mkdir -p "corpus/$(dirname "$rel")"
  $G show "$VERIFIED_SHA:$BASE/$rel" > "corpus/$rel"
done
python3 - <<'PY'
import json, hashlib, glob
m = json.load(open("preregistration/freeze_manifest.json"))
h = hashlib.sha256()
files = sorted(glob.glob("corpus/*/*.csv"))
for c in files:
    h.update(hashlib.sha256(open(c, "rb").read()).digest())
ok = h.hexdigest() == m["corpus_merkle_sha256"]
print(f"  corpus files: {len(files)} (expected {m['corpus_files']})")
print(f"  corpus merkle: {'OK' if ok else 'MISMATCH'}")
PY
echo "done. now: python3 analysis/run_armB.py"
