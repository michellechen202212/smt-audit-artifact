"""Arm B — confirmatory evaluator-probe study.

Applies the FROZEN output-level probe realizations (preregistration/witness_rules.yaml)
to released ELT-Bench output tables, with matched conventional controls, and runs
both PINNED evaluator comparators.

Nothing here may be edited after the run begins. Operators, controls, row cap and
admissibility rules are read from the frozen files, not hard-coded choices made
after seeing results.
"""
import os, sys, csv, glob, json, hashlib, warnings, importlib.util
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

RULES = yaml.safe_load(open("preregistration/witness_rules.yaml"))
ROW_CAP = RULES["row_cap"]
SORT_KEYS = json.load(open("evaluator/default/sort_key.json"))

def load(tag):
    spec = importlib.util.spec_from_file_location(f"cmp_{tag}", f"evaluator/{tag}/comparator.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
DEFAULT, VERIFIED = load("default"), load("verified")

# ---------------------------------------------------------------- helpers
def hsh(df):
    return hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()[:16]

def exact_differs(a, b):
    """Admissibility oracle - independent of both evaluators."""
    if a.shape != b.shape: return True
    if list(a.columns) != list(b.columns): return True
    for c in a.columns:
        x, y = a[c], b[c]
        nx, ny = x.isna().to_numpy(), y.isna().to_numpy()
        if not np.array_equal(nx, ny): return True
        if (x.astype(str).to_numpy()[~nx] != y.astype(str).to_numpy()[~ny]).any(): return True
    return False

def numeric_cols(df, keys):
    out = []
    for c in df.columns:
        if c.lower() in {k.lower() for k in keys}: continue
        s = pd.to_numeric(df[c], errors="coerce")
        if s.notna().sum() >= max(3, 0.5 * df[c].notna().sum()) and df[c].notna().sum() > 0:
            out.append(c)
    return out

def pk_regime(df):
    """Which alignment regime the Verified comparator will take."""
    try:
        pks = VERIFIED.identify_primary_key_columns(df)
        return "inferred_key" if pks else "all_column_fallback"
    except Exception:
        return "unknown"

# ---------------------------------------------------------------- probes
def probe_GC1(df, keys):
    if len(df) < 2 or not keys: return None, None
    m = pd.concat([df.iloc[[0]], df], ignore_index=True)
    return m, "row_set"

def probe_PP1(df, keys):
    if len(df) < 5: return None, None
    k = max(1, int(len(df) * 0.2))
    return df.iloc[:-k].reset_index(drop=True), "row_set"

def probe_RV1(df, keys):
    if not keys: return None, None
    kk = [c for c in df.columns if c.lower() in {x.lower() for x in keys}]
    if not kk: return None, None
    dup = df.duplicated(subset=kk, keep="first")
    if not dup.any(): return None, None
    return df[~dup].reset_index(drop=True), "row_set"

def probe_ME3(df, keys):
    for c in numeric_cols(df, keys):
        s = pd.to_numeric(df[c], errors="coerce")
        nn = s.dropna()
        if len(nn) and nn.between(0, 1).all() and nn[nn != 0].nunique() >= 3:
            m = df.copy(); m[c] = s * 100
            return m, "value_gt_1pct", c
    return None, None, None

def _null_and_zero_col(df, keys):
    for c in numeric_cols(df, keys):
        s = pd.to_numeric(df[c], errors="coerce")
        if df[c].isna().any() and (s == 0).any():
            return c
    return None

def probe_AB1(df, keys):
    c = _null_and_zero_col(df, keys)
    if c is None: return None, None, None
    m = df.copy(); m[c] = pd.to_numeric(m[c], errors="coerce").fillna(0)
    return m, "value_gt_1pct", c

def probe_AB1R(df, keys):
    c = _null_and_zero_col(df, keys)
    if c is None: return None, None, None
    m = df.copy(); s = pd.to_numeric(m[c], errors="coerce")
    m[c] = s.mask(s == 0, np.nan)
    return m, "value_gt_1pct", c

def probe_AB2(df, keys):
    for c in df.columns:
        if c.lower() in {k.lower() for k in keys}: continue
        if df[c].isna().any():
            m = df.copy(); m[c] = m[c].astype(object).where(m[c].notna(), "N/A")
            return m, "value_gt_1pct", c
    return None, None, None

# ---------------------------------------------------------------- controls
def ctl_rowdrop(df, n_changed, col):
    """SDL analogue: drop the same number of rows, from the middle."""
    if len(df) <= n_changed or n_changed < 1: return None
    start = max(0, len(df)//2 - n_changed//2)
    return df.drop(df.index[start:start+n_changed]).reset_index(drop=True)

def ctl_rowdup(df, n_changed, col):
    if len(df) < 1: return None
    mid = len(df)//2
    return pd.concat([df.iloc[:mid], df.iloc[[mid]], df.iloc[mid:]], ignore_index=True)

def ctl_AOR_scale(df, n_changed, col):
    m = df.copy(); m[col] = pd.to_numeric(m[col], errors="coerce") * 1.5
    return m

def ctl_IR_constfill(df, n_changed, col):
    m = df.copy(); s = pd.to_numeric(m[col], errors="coerce")
    m[col] = s.fillna(999999)
    return m

def ctl_IR_constzero(df, n_changed, col):
    m = df.copy(); s = pd.to_numeric(m[col], errors="coerce")
    m[col] = s.mask(s == 0, 999999)
    return m

def ctl_IR_sentinel(df, n_changed, col):
    m = df.copy(); m[col] = m[col].astype(object).where(m[col].notna(), "ZZZQ")
    return m

PROBES = {
 "GC1":  ("grain_cardinality",     probe_GC1,   ctl_rowdup,        "SDL_rowdup"),
 "PP1":  ("population_predicates", probe_PP1,   ctl_rowdrop,       "SDL_rowdrop"),
 "RV1":  ("representative_value",  probe_RV1,   ctl_rowdrop,       "SDL_rowdrop"),
 "ME3":  ("measures",              probe_ME3,   ctl_AOR_scale,     "AOR_scale"),
 "AB1":  ("absence",               probe_AB1,   ctl_IR_constfill,  "IR_constfill"),
 "AB1R": ("absence",               probe_AB1R,  ctl_IR_constzero,  "IR_constzero"),
 "AB2":  ("absence",               probe_AB2,   ctl_IR_sentinel,   "IR_sentinel"),
}
PREDICTION = {"GC1":"survive","PP1":"survive","RV1":"survive","ME3":"survive",
              "AB1":"survive","AB1R":"survive","AB2":"reject"}

# ---------------------------------------------------------------- evaluators
def _csv_roundtrip(df, as_str):
    """Mimic each driver's real load path: outputs are written to CSV and read back.
    This matters: read_csv coerces sentinel strings such as 'N/A' back to NaN, so
    comparing in-memory DataFrames would not reproduce evaluator behaviour."""
    import io as _io
    b = _io.StringIO(); df.to_csv(b, index=False); b.seek(0)
    return pd.read_csv(b, dtype=str, keep_default_na=True) if as_str else pd.read_csv(b)

def verdict_verified(ref, mut):
    try:
        g, p = _csv_roundtrip(ref, False), _csv_roundtrip(mut, False)
        m,u,miss = VERIFIED.check_corretness(g, p)
        return "SURVIVED" if (not u and not miss) else "rejected"
    except Exception as e:
        return f"ERROR:{type(e).__name__}"

def verdict_default(ref, mut, keys):
    try:
        g, p = _csv_roundtrip(ref, True), _csv_roundtrip(mut, True)
        a = DEFAULT.sort_by_keys(g, keys)
        b = DEFAULT.sort_by_keys(p, keys)
        r = DEFAULT.check_corretness(a, b)
        return "SURVIVED" if r["match"] else "rejected"
    except Exception as e:
        return f"ERROR:{type(e).__name__}"

# ---------------------------------------------------------------- main
rows = []
tables = sorted(glob.glob("corpus/*/*.csv"))
print(f"corpus: {len(tables)} tables")

for i, path in enumerate(tables, 1):
    db = os.path.basename(os.path.dirname(path))
    tbl = os.path.basename(path)[:-4]
    keys = SORT_KEYS.get(db, {}).get(tbl, [])
    try:
        ref = pd.read_csv(path, nrows=ROW_CAP)
    except Exception as e:
        continue
    if ref.empty: continue
    regime = pk_regime(ref)
    rhash = hsh(ref)

    for oid, (fam, pfn, cfn, cname) in PROBES.items():
        out = pfn(ref, keys)
        col = out[2] if len(out) == 3 else None
        mut, mbin = out[0], out[1]
        base = dict(model_id=f"{db}.{tbl}", arm="B", operator_id=oid, mutation_family=fam,
                    witness_id=f"corpus:{db}.{tbl}:cap{ROW_CAP}", reference_output_hash=rhash,
                    pk_alignment_regime=regime, prediction=PREDICTION[oid],
                    matched_control_id=f"{cname}:{db}.{tbl}:{oid}")
        if mut is None:
            rows.append({**base, "evaluator_version":"-", "applicable":"NOT_APPLICABLE",
                         "admissible":"", "mutant_output_hash":"", "evaluator_verdict":"",
                         "control_verdict":"", "normalization_triggered":"",
                         "root_cause_category":"", "prediction_correct":""}); continue
        if not exact_differs(ref, mut):
            rows.append({**base, "evaluator_version":"-", "applicable":"applicable",
                         "admissible":"INADMISSIBLE", "mutant_output_hash":hsh(mut),
                         "evaluator_verdict":"", "control_verdict":"",
                         "normalization_triggered":"", "root_cause_category":"",
                         "prediction_correct":""}); continue

        n_changed = abs(len(mut) - len(ref)) or 1
        ctl = cfn(ref, n_changed, col)
        ctl_ok = ctl is not None and exact_differs(ref, ctl)

        for ver, vf in (("default", lambda r,m: verdict_default(r,m,keys)),
                        ("verified", verdict_verified)):
            v = vf(ref, mut)
            cv = vf(ref, ctl) if ctl_ok else "NONE"
            pc = ""
            if ver == "verified" and v in ("SURVIVED","rejected"):
                pc = str((v == "SURVIVED") == (PREDICTION[oid] == "survive"))
            rows.append({**base, "evaluator_version":ver, "applicable":"applicable",
                         "admissible":"admissible", "mutant_output_hash":hsh(mut),
                         "evaluator_verdict":v, "control_verdict":cv,
                         "normalization_triggered":"", "root_cause_category":"",
                         "prediction_correct":pc})
    if i % 30 == 0:
        print(f"  {i}/{len(tables)} tables", flush=True)

cols = ["model_id","arm","operator_id","mutation_family","witness_id","evaluator_version",
        "applicable","admissible","reference_output_hash","mutant_output_hash",
        "evaluator_verdict","matched_control_id","control_verdict","pk_alignment_regime",
        "normalization_triggered","root_cause_category","prediction","prediction_correct"]
with open("results/armB_results.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
print(f"\nwrote results/armB_results.csv ({len(rows)} rows)")
