"""Second-benchmark transfer pilot: Spider 2.0-lite comparator.

Applies the FROZEN Arm B probes and FROZEN matched-control rules, unchanged, to
Spider 2.0-lite gold execution results. No new operator is defined. No probe
semantics are altered.

Declared-key note: the frozen preconditions exclude "key" columns, sourced in
ELT-Bench from sort_key.json. Spider 2.0-lite declares no key for a result set,
so the declared-key set is empty and every column is a non-key column. This is
the same predicate evaluated against an empty key declaration, not a redefinition.

Probes whose MEANING depends on a declared key (GC1 "row multiplicity at declared
grain"; RV1 "tied key group") have no referent here and are recorded
NOT_APPLICABLE rather than adapted.

Evaluation is invoked as the benchmark does: score = compare(pred=perturbed,
gold=gold) with the instance's own condition_cols and ignore_order. score 1 =
accepted (probe survives); 0 = rejected.
"""
import os, csv, json, glob, hashlib, importlib.util, warnings
warnings.filterwarnings("ignore")
import pandas as pd, numpy as np

os.chdir(os.path.dirname(os.path.abspath(__file__)))
GOLD = "/tmp/claude-0/-home-claude/24371440-c60c-5159-bdb4-869b4a1e437c/scratchpad/bench2/spider2/spider2-lite/evaluation_suite/gold"

def load(tag):
    s = importlib.util.spec_from_file_location(f"c_{tag}", f"evaluator/cmp_{tag}.py")
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
DRIVER, UTILS = load("driver"), load("utils")

META = {json.loads(l)["instance_id"]: json.loads(l)
        for l in open(f"{GOLD}/spider2lite_eval.jsonl")}

def hsh(df): return hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()[:16]

# ---- FROZEN helpers (identical predicates; key set is empty here) ----
def numeric_cols(df, keys=()):
    out = []
    for c in df.columns:
        if c.lower() in {k.lower() for k in keys}: continue
        s = pd.to_numeric(df[c], errors="coerce")
        if s.notna().sum() >= max(3, 0.5 * df[c].notna().sum()) and df[c].notna().sum() > 0:
            out.append(c)
    return out

def _null_and_zero_col(df, keys=()):
    for c in numeric_cols(df, keys):
        s = pd.to_numeric(df[c], errors="coerce")
        if df[c].isna().any() and (s == 0).any(): return c
    return None

# ---- FROZEN probes (verbatim rules) ----
def probe_PP1(df):
    if len(df) < 5: return None, None
    return df.iloc[:-max(1, int(len(df) * 0.2))].reset_index(drop=True), None

def probe_ME3(df):
    for c in numeric_cols(df):
        s = pd.to_numeric(df[c], errors="coerce"); nn = s.dropna()
        if len(nn) and nn.between(0, 1).all() and nn[nn != 0].nunique() >= 3:
            m = df.copy(); m[c] = s * 100; return m, c
    return None, None

def probe_AB1(df):
    c = _null_and_zero_col(df)
    if c is None: return None, None
    m = df.copy(); m[c] = pd.to_numeric(m[c], errors="coerce").fillna(0); return m, c

def probe_AB1R(df):
    c = _null_and_zero_col(df)
    if c is None: return None, None
    m = df.copy(); s = pd.to_numeric(m[c], errors="coerce")
    m[c] = s.mask(s == 0, np.nan); return m, c

def probe_AB2(df):
    for c in df.columns:
        if df[c].isna().any():
            m = df.copy(); m[c] = m[c].astype(object).where(m[c].notna(), "N/A"); return m, c
    return None, None

# ---- FROZEN matched controls ----
def ctl_rowdrop(df, n, col):
    if len(df) <= n or n < 1: return None
    st = max(0, len(df)//2 - n//2)
    return df.drop(df.index[st:st+n]).reset_index(drop=True)
def ctl_AOR_scale(df, n, col):
    m = df.copy(); m[col] = pd.to_numeric(m[col], errors="coerce") * 1.5; return m
def ctl_IR_constfill(df, n, col):
    m = df.copy(); m[col] = pd.to_numeric(m[col], errors="coerce").fillna(999999); return m
def ctl_IR_constzero(df, n, col):
    m = df.copy(); s = pd.to_numeric(m[col], errors="coerce")
    m[col] = s.mask(s == 0, 999999); return m
def ctl_IR_sentinel(df, n, col):
    m = df.copy(); m[col] = m[col].astype(object).where(m[col].notna(), "ZZZQ"); return m

PROBES = {"PP1": (probe_PP1, ctl_rowdrop), "ME3": (probe_ME3, ctl_AOR_scale),
          "AB1": (probe_AB1, ctl_IR_constfill), "AB1R": (probe_AB1R, ctl_IR_constzero),
          "AB2": (probe_AB2, ctl_IR_sentinel)}
NOT_APPLICABLE = {"GC1": "probe meaning is row multiplicity at a DECLARED grain; no key declared",
                  "RV1": "probe requires a tied DECLARED-key group; no key declared"}

def exact_differs(a, b):
    if a.shape != b.shape or list(a.columns) != list(b.columns): return True
    for c in a.columns:
        x, y = a[c], b[c]
        nx, ny = x.isna().to_numpy(), y.isna().to_numpy()
        if not np.array_equal(nx, ny): return True
        if (x.astype(str).to_numpy()[~nx] != y.astype(str).to_numpy()[~ny]).any(): return True
    return False

def score(mod, pred, gold, meta):
    try:
        return "SURVIVED" if mod.compare_pandas_table(
            pred.copy(), gold.copy(), meta.get("condition_cols"),
            meta.get("ignore_order", False)) == 1 else "rejected"
    except Exception as e:
        return f"ERROR:{type(e).__name__}"

rows, seen = [], 0
for path in sorted(glob.glob(f"{GOLD}/exec_result/*.csv")):
    iid = os.path.basename(path)[:-4].rsplit("_", 1)[0]
    meta = META.get(iid)
    if meta is None: continue
    try: gold = pd.read_csv(path)
    except Exception: continue
    if gold.empty or len(gold.columns) < 2: continue

    made = False
    for pid, (pf, cf) in PROBES.items():
        mut, col = pf(gold)
        if mut is None or not exact_differs(gold, mut):
            rows.append(dict(benchmark="spider2-lite", instance_id=iid, probe_id=pid,
                applicable="NOT_APPLICABLE" if mut is None else "INADMISSIBLE",
                reference_hash=hsh(gold), probe_hash="", control_hash="",
                probe_verdict_driver="", control_verdict_driver="",
                probe_verdict_utils="", notes="precondition unmet" if mut is None else "equivalent"))
            continue
        n = abs(len(mut) - len(gold)) or 1
        ctl = cf(gold, n, col)
        ok = ctl is not None and exact_differs(gold, ctl)
        rows.append(dict(benchmark="spider2-lite", instance_id=iid, probe_id=pid,
            applicable="applicable", reference_hash=hsh(gold), probe_hash=hsh(mut),
            control_hash=hsh(ctl) if ok else "",
            probe_verdict_driver=score(DRIVER, mut, gold, meta),
            control_verdict_driver=score(DRIVER, ctl, gold, meta) if ok else "NONE",
            probe_verdict_utils=score(UTILS, mut, gold, meta),
            notes=f"col={col}" if col else ""))
        made = True
    for pid, why in NOT_APPLICABLE.items():
        rows.append(dict(benchmark="spider2-lite", instance_id=iid, probe_id=pid,
            applicable="NOT_APPLICABLE", reference_hash=hsh(gold), probe_hash="",
            control_hash="", probe_verdict_driver="", control_verdict_driver="",
            probe_verdict_utils="", notes=why))
    if made: seen += 1
    if seen >= 15: break

with open("results/spider2_pilot.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

adm = [r for r in rows if r["applicable"] == "applicable"]
print(f"instances with >=1 admissible probe: {seen}   admissible instances: {len(adm)}\n")
print(f"{'probe':<6}{'n':>4}  {'driver: probe rej':>18}{'driver: ctl rej':>17}{'utils: probe rej':>18}")
print("-" * 65)
for pid in PROBES:
    s = [r for r in adm if r["probe_id"] == pid]
    if not s: print(f"{pid:<6}{0:>4}   (no eligible instance in pilot window)"); continue
    c = [r for r in s if r["control_verdict_driver"] in ("rejected", "SURVIVED")]
    print(f"{pid:<6}{len(s):>4}  "
          f"{sum(1 for r in s if r['probe_verdict_driver']=='rejected'):>10}/{len(s):<7}"
          f"{sum(1 for r in c if r['control_verdict_driver']=='rejected'):>9}/{len(c):<7}"
          f"{sum(1 for r in s if r['probe_verdict_utils']=='rejected'):>10}/{len(s):<7}")
print("-" * 65)
c = [r for r in adm if r["control_verdict_driver"] in ("rejected", "SURVIVED")]
print(f"{'TOTAL':<6}{len(adm):>4}  "
      f"{sum(1 for r in adm if r['probe_verdict_driver']=='rejected'):>10}/{len(adm):<7}"
      f"{sum(1 for r in c if r['control_verdict_driver']=='rejected'):>9}/{len(c):<7}"
      f"{sum(1 for r in adm if r['probe_verdict_utils']=='rejected'):>10}/{len(adm):<7}")
print(f"\nNOT_APPLICABLE rows: {sum(1 for r in rows if r['applicable']=='NOT_APPLICABLE')}")
