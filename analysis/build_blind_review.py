"""Build a blinded semantic-equivalence review package.

Reconstructs each confirmatory Arm B case in the clean comparator subset
(ME3, AB1, AB1R) using the SAME code path as analysis/run_armB.py, verifies both
stored hashes, and emits a reviewer-facing package that carries no operator IDs,
verdicts, family names, predictions or expected labels.

The A/B assignment is randomised with a fixed seed and recorded ONLY in the
private key directory.
"""
import os, csv, io, json, glob, hashlib, random, shutil, warnings
warnings.filterwarnings("ignore")
import pandas as pd, numpy as np, yaml

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RULES   = yaml.safe_load(open("preregistration/witness_rules.yaml"))
ROW_CAP = RULES["row_cap"]
SORT_KEYS = json.load(open("evaluator/default/sort_key.json"))
SPECS   = json.load(open("/tmp/task_specs.json"))
SEED    = 20260929
CLEAN   = ("ME3", "AB1", "AB1R")

# ---- identical helpers to analysis/run_armB.py (copied, not re-derived) ----
def hsh(df):
    return hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()[:16]

def numeric_cols(df, keys):
    out = []
    for c in df.columns:
        if c.lower() in {k.lower() for k in keys}: continue
        s = pd.to_numeric(df[c], errors="coerce")
        if s.notna().sum() >= max(3, 0.5 * df[c].notna().sum()) and df[c].notna().sum() > 0:
            out.append(c)
    return out

def _null_and_zero_col(df, keys):
    for c in numeric_cols(df, keys):
        s = pd.to_numeric(df[c], errors="coerce")
        if df[c].isna().any() and (s == 0).any():
            return c
    return None

def probe_ME3(df, keys):
    for c in numeric_cols(df, keys):
        s = pd.to_numeric(df[c], errors="coerce"); nn = s.dropna()
        if len(nn) and nn.between(0, 1).all() and nn[nn != 0].nunique() >= 3:
            m = df.copy(); m[c] = s * 100
            return m, c
    return None, None

def probe_AB1(df, keys):
    c = _null_and_zero_col(df, keys)
    if c is None: return None, None
    m = df.copy(); m[c] = pd.to_numeric(m[c], errors="coerce").fillna(0)
    return m, c

def probe_AB1R(df, keys):
    c = _null_and_zero_col(df, keys)
    if c is None: return None, None
    m = df.copy(); s = pd.to_numeric(m[c], errors="coerce")
    m[c] = s.mask(s == 0, np.nan)
    return m, c

PROBES = {"ME3": probe_ME3, "AB1": probe_AB1, "AB1R": probe_AB1R}

# ---------------------------------------------------------------- inputs
rows = [r for r in csv.DictReader(open("results/armB_results.csv"))
        if r["admissible"] == "admissible"
        and r["evaluator_version"] == "verified"
        and r["operator_id"] in CLEAN]
rows.sort(key=lambda r: (r["model_id"], r["operator_id"]))
assert len(rows) == 34, f"expected 34 clean cases, found {len(rows)}"
# Shuffle case order under the fixed seed so that two cases derived from the same
# source table never land on adjacent case IDs. Without this, a reviewer could
# infer the study design from adjacency alone.
_order = random.Random(SEED + 1)
for _ in range(500):
    _order.shuffle(rows)
    if all(rows[i]["model_id"] != rows[i+1]["model_id"] for i in range(len(rows)-1)):
        break
else:
    raise SystemExit("could not find a non-adjacent ordering")

PKG  = "blind_review"
PRIV = "blind_review_private"
for d in (PKG, PRIV):
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)

rng = random.Random(SEED)
manifest, key, audit = [], [], []

for i, r in enumerate(rows, 1):
    cid = f"case_{i:03d}"
    db, tbl = r["model_id"].split(".", 1)
    path = f"corpus/{db}/{tbl}.csv"
    keys = SORT_KEYS.get(db, {}).get(tbl, [])

    rec = {"case_id": cid, "model_id": r["model_id"], "operator_id": r["operator_id"],
           "stored_ref_hash": r["reference_output_hash"],
           "stored_mut_hash": r["mutant_output_hash"]}

    if not os.path.isfile(path):
        rec.update(reconstructed="NO", reason="corpus table not present"); audit.append(rec); continue

    base = pd.read_csv(path, nrows=ROW_CAP)
    pert, col = PROBES[r["operator_id"]](base, keys)
    if pert is None:
        rec.update(reconstructed="NO", reason="probe preconditions not met on reload"); audit.append(rec); continue

    ref_ok = hsh(base) == r["reference_output_hash"]
    mut_ok = hsh(pert) == r["mutant_output_hash"]
    rec.update(recomputed_ref_hash=hsh(base), recomputed_mut_hash=hsh(pert),
               ref_hash_match="YES" if ref_ok else "NO",
               mut_hash_match="YES" if mut_ok else "NO",
               affected_column=col)
    if not (ref_ok and mut_ok):
        rec.update(reconstructed="NO", reason="hash mismatch"); audit.append(rec); continue
    rec.update(reconstructed="YES", reason="")

    # ---- randomised A/B assignment (fixed seed); mapping kept private only
    base_is_A = rng.random() < 0.5
    out_A, out_B = (base, pert) if base_is_A else (pert, base)

    d = os.path.join(PKG, cid); os.makedirs(d)
    out_A.to_csv(os.path.join(d, "output_A.csv"), index=False)
    out_B.to_csv(os.path.join(d, "output_B.csv"), index=False)

    # ---- context.txt: documented facts only, no operator/family/verdict/label
    spec = SPECS.get(r["model_id"], {})
    desc = (spec.get("model_description") or "").strip()
    # corpus headers are upper-cased by the warehouse; spec keys are lower-case
    coldesc = {k.lower(): v for k, v in (spec.get("columns", {}) or {}).items()}
    L = [f"CASE {cid}", ""]
    L.append("Record domain (from the public task specification):")
    L.append(f"  {desc if desc else 'Not specified.'}")
    L.append("")
    L.append("Columns, with datatype and the documented description where one exists:")
    for c in out_A.columns:
        dt = str(out_A[c].dtype)
        nn = int(out_A[c].isna().sum()) + int(out_B[c].isna().sum())
        dd = (coldesc.get(c.lower()) or "").strip()
        L.append(f"  - {c}  [dtype in file A: {dt}]")
        L.append(f"      documented description: {dd if dd else 'Column semantics beyond its name and datatype are not specified.'}")
    L.append("")
    L.append(f"Rows in output_A.csv: {len(out_A)}")
    L.append(f"Rows in output_B.csv: {len(out_B)}")
    L.append("")
    L.append("Both files were produced by data transformations over the same source data.")
    L.append("No claim is made here about which file, if either, is correct.")
    L.append("Empty CSV fields denote absent values; a literal 0 denotes the number zero.")
    open(os.path.join(d, "context.txt"), "w").write("\n".join(L) + "\n")

    manifest.append({"case_id": cid, "context_file": f"{cid}/context.txt",
                     "output_A_file": f"{cid}/output_A.csv",
                     "output_B_file": f"{cid}/output_B.csv",
                     "row_count_A": len(out_A), "row_count_B": len(out_B),
                     "column_count": len(out_A.columns)})

    key.append({"case_id": cid, "model_id": r["model_id"], "operator_id": r["operator_id"],
                "affected_column": col,
                "A_is": "unperturbed" if base_is_A else "perturbed",
                "B_is": "perturbed" if base_is_A else "unperturbed",
                "verdict_verified": r["evaluator_verdict"],
                "control_verdict_verified": r["control_verdict"],
                "reference_output_hash": r["reference_output_hash"],
                "mutant_output_hash": r["mutant_output_hash"],
                "prediction": r["prediction"]})
    audit.append(rec)

with open(os.path.join(PKG, "manifest.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(manifest[0])); w.writeheader(); w.writerows(manifest)
with open(os.path.join(PRIV, "answer_key.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(key[0])); w.writeheader(); w.writerows(key)
json.dump(audit, open(os.path.join(PRIV, "reconstruction_audit.json"), "w"), indent=1)

open(os.path.join(PKG, "README_FOR_REVIEWER.txt"), "w").write(
"""You are reviewing paired outputs from data transformations.

For each case, judge whether output A and output B have the same meaning for a
downstream consumer, different meaning, or whether the provided context is
insufficient to decide.

Do not assume either side is correct.

Each case directory contains:
  context.txt     column names, datatypes, and documented column descriptions
  output_A.csv    one output
  output_B.csv    the other output

manifest.csv lists every case.
""")

nA = sum(1 for k in key if k["A_is"] == "unperturbed")
print(f"cases written: {len(manifest)} / {len(rows)}")
print(f"hash verification: ref {sum(1 for a in audit if a.get('ref_hash_match')=='YES')}/{len(rows)}, "
      f"pert {sum(1 for a in audit if a.get('mut_hash_match')=='YES')}/{len(rows)}")
print(f"A/B balance: A unperturbed in {nA}, perturbed in {len(key)-nA} (seed {SEED})")
failed = [a for a in audit if a.get("reconstructed") != "YES"]
print("failed reconstructions:", failed if failed else "NONE")
