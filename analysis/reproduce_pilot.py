"""Independent reproduction of the exploratory 10+5 pilot.

Comparators are re-extracted from PINNED commits by evaluator/extract.py and
verified byte-identical to the pinned sources. Nothing is imported from the
earlier development artifact except the operator definitions and witness, which
are the objects under test.
"""
import sys, io, csv, hashlib, warnings, pathlib
warnings.filterwarnings("ignore")
sys.path[:0] = ["witnesses", "references", "mutants", "evaluator/default", "evaluator/verified"]
import pandas as pd
import witness_w1 as W
import pilot_operators as OPS
from reference_port import REFERENCE

sys.path.insert(0, "evaluator/default");  import importlib.util
def load(tag):
    spec = importlib.util.spec_from_file_location(f"cmp_{tag}", f"evaluator/{tag}/comparator.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
DEFAULT  = load("default")
VERIFIED = load("verified")

SORT_KEY = ["driver_id"]

def run(sql):
    try:    return W.fresh().execute(sql).df(), None
    except Exception as e: return None, f"{type(e).__name__}: {e}"

def h(df):
    b = io.StringIO(); df.to_csv(b, index=False)
    return hashlib.sha256(b.getvalue().encode()).hexdigest()[:12]

def rt(df, as_str):
    b = io.StringIO(); df.to_csv(b, index=False); b.seek(0)
    return pd.read_csv(b, dtype=str, keep_default_na=True) if as_str else pd.read_csv(b)

def differs(a, b):
    if a.shape != b.shape: return True, f"shape {a.shape} vs {b.shape}"
    ka, kb = (x.sort_values(SORT_KEY).reset_index(drop=True) for x in (a, b))
    try:
        pd.testing.assert_frame_equal(ka, kb, check_dtype=False, rtol=0, atol=0)
        return False, "equivalent on witness"
    except AssertionError as e:
        return True, e.args[0].splitlines()[0][:60]

def v_verified(ref, mut):
    g, p = rt(ref, False), rt(mut, False)
    m, u, miss = VERIFIED.check_corretness(g, p)
    return (not u and not miss), u + miss

def v_default(ref, mut):
    g, p = rt(ref, True), rt(mut, True)
    g, p = DEFAULT.sort_by_keys(g, SORT_KEY), DEFAULT.sort_by_keys(p, SORT_KEY)
    r = DEFAULT.check_corretness(g, p)
    return r["match"], r["unmatched"] + r["missed"]

ref_df, err = run(REFERENCE); assert err is None, err
rows = []
for arm, group in (("semantic", OPS.SEMANTIC), ("conventional", OPS.CONVENTIONAL)):
    for mid, fam, prop, find, repl in group:
        sql = OPS.apply(find, repl)
        mut, err = run(sql)
        if err:
            rows.append(dict(arm=arm, mutation_id=mid, family=fam, property=prop,
                             admissibility="inadmissible:not_executable", evidence=err[:60],
                             ref_hash=h(ref_df), mut_hash="", v_default="", v_verified="")); continue
        d, why = differs(ref_df, mut)
        if not d:
            rows.append(dict(arm=arm, mutation_id=mid, family=fam, property=prop,
                             admissibility="inadmissible:equivalent_on_witness", evidence=why,
                             ref_hash=h(ref_df), mut_hash=h(mut), v_default="", v_verified="")); continue
        dok, _ = v_default(ref_df, mut); vok, _ = v_verified(ref_df, mut)
        rows.append(dict(arm=arm, mutation_id=mid, family=fam, property=prop,
                         admissibility="admissible", evidence=why,
                         ref_hash=h(ref_df), mut_hash=h(mut),
                         v_default="SURVIVED" if dok else "rejected",
                         v_verified="SURVIVED" if vok else "rejected"))

with open("results/pilot_reproduction.csv", "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)

print(f"{'id':<5}{'arm':<13}{'family':<22}{'admissible':<12}{'default':<10}{'verified':<10}")
print("-"*72)
for r in rows:
    print(f"{r['mutation_id']:<5}{r['arm']:<13}{r['family']:<22}"
          f"{('yes' if r['admissibility']=='admissible' else 'NO'):<12}"
          f"{r['v_default']:<10}{r['v_verified']:<10}")

def rate(arm, key):
    a = [r for r in rows if r["arm"]==arm and r["admissibility"]=="admissible"]
    rej = [r for r in a if r[key]=="rejected"]
    return len(rej), len(a)

print("\nDetection rates (rejected / admissible):")
for arm in ("semantic","conventional"):
    for key,name in (("v_default","default (elt_bench++)"),("v_verified","Verified (PR#18)")):
        n,d = rate(arm,key)
        print(f"  {arm:<13} {name:<24} {n}/{d} = {100*n/d:.0f}%")
s_v,_=rate("semantic","v_verified"); c_v,_=rate("conventional","v_verified")
print(f"\nDelta_verified = CMDR - SMDR = {100*c_v/5:.0f}% - {100*s_v/10:.0f}% = {100*c_v/5-100*s_v/10:.0f} pts")
