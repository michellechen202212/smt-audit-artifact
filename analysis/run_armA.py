"""Arm A - SQL-level fidelity anchor.

Applies CONFIRMATORY catalogue operators (operators/catalog_v1.yaml) to a genuine
ELT-Bench reference transformation, with matched conventional controls, on a
witness satisfying the frozen structural requirements.

Role (per protocol): establish that Arm B's declared semantic distinctions can
arise from plausible transformation-level edits. NOT a prevalence estimate.
"""
import os, sys, csv, io, hashlib, warnings, importlib.util
warnings.filterwarnings("ignore")
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = ["witnesses", "references"]
import pandas as pd
import witness_w1 as W
from reference_port import REFERENCE

def load(tag):
    s = importlib.util.spec_from_file_location(f"c_{tag}", f"evaluator/{tag}/comparator.py")
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
DEFAULT, VERIFIED = load("default"), load("verified")
KEYS = ["driver_id"]

# ---- CONFIRMATORY operators from catalog_v1.yaml whose preconditions hold here.
# (operator_id, family, anchor, replacement, matched control anchor/replacement, control_id)
SEM = [
 ("GC1","grain_cardinality",
  "  SELECT DISTINCT driver_id AS driver_id\n  FROM shipping.shipment",
  "  SELECT driver_id AS driver_id\n  FROM shipping.shipment"),
 ("ME1","measures",
  "SELECT T2.driver_id AS driver_id, COUNT(*) AS num_shipments_2017",
  "SELECT T2.driver_id AS driver_id, COUNT(DISTINCT T1.cust_id) AS num_shipments_2017"),
 ("ME3","measures",
  "AS DOUBLE)\n      * 100 / COUNT(*) AS per",
  "AS DOUBLE)\n      * 1 / COUNT(*) AS per"),
 ("PP1","population_predicates",
  "LEFT JOIN num_shipments_2017_cte T2 ON T1.driver_id = T2.driver_id",
  "INNER JOIN num_shipments_2017_cte T2 ON T1.driver_id = T2.driver_id"),
 ("PP2","population_predicates",
  "WHEN T2.cust_name ILIKE 'Autoware Inc' THEN 1",
  "WHEN T2.cust_name ILIKE '%Autoware%' THEN 1"),
 ("AB1","absence",
  "  CASE WHEN T2.num_shipments_2017 IS NULL THEN 0 ELSE T2.num_shipments_2017 END\n    AS num_shipments_2017",
  "  T2.num_shipments_2017 AS num_shipments_2017"),
 ("AB2","absence",
  "  T4.per AS per_shipment_placed_by_Autoware_Inc",
  "  COALESCE(CAST(T4.per AS VARCHAR), 'N/A') AS per_shipment_placed_by_Autoware_Inc"),
 ("RV1","representative_value",
  "    rank() OVER (PARTITION BY driver_id ORDER BY ship_date, weight DESC) AS date_rank",
  "    row_number() OVER (PARTITION BY driver_id ORDER BY ship_date, weight DESC) AS date_rank"),
 ("RV2","representative_value",
  "rank() OVER (PARTITION BY driver_id ORDER BY ship_date, weight DESC)",
  "rank() OVER (PARTITION BY driver_id ORDER BY ship_date, weight ASC)"),
 ("TM2","temporal",
  "WHERE EXTRACT(YEAR FROM T1.ship_date) = 2017",
  "WHERE EXTRACT(YEAR FROM T1.ship_date) >= 2017"),
]

# Matched conventional controls (Tuya 2007), same affected column, same bin.
CTL = {
 "GC1": ("CTL-SDL","  LEFT JOIN weight_first_shipment_cte T6 ON T1.driver_id = T6.driver_id AND T6.date_rank = 1",
         "  LEFT JOIN weight_first_shipment_cte T6 ON T1.driver_id = T6.driver_id AND T6.date_rank <= 2"),
 "ME1": ("CTL-AOR","SELECT T2.driver_id AS driver_id, COUNT(*) AS num_shipments_2017",
         "SELECT T2.driver_id AS driver_id, COUNT(*) + 3 AS num_shipments_2017"),
 "ME3": ("CTL-AOR","AS DOUBLE)\n      * 100 / COUNT(*) AS per",
         "AS DOUBLE)\n      * 150 / COUNT(*) AS per"),
 "PP1": ("CTL-IR","FROM shipping.driver T1\n  LEFT JOIN num_shipments_2017_cte",
         "FROM (SELECT * FROM shipping.driver WHERE driver_id <> 4) T1\n  LEFT JOIN num_shipments_2017_cte"),
 "PP2": ("CTL-IR","WHEN T2.cust_name ILIKE 'Autoware Inc' THEN 1",
         "WHEN T2.cust_name ILIKE 'Other Co' THEN 1"),
 "AB1": ("CTL-IR","  CASE WHEN T2.num_shipments_2017 IS NULL THEN 0 ELSE T2.num_shipments_2017 END\n    AS num_shipments_2017",
         "  CASE WHEN T2.num_shipments_2017 IS NULL THEN 999999 ELSE T2.num_shipments_2017 END\n    AS num_shipments_2017"),
 "AB2": ("CTL-IR","  T4.per AS per_shipment_placed_by_Autoware_Inc",
         "  COALESCE(CAST(T4.per AS VARCHAR), 'ZZZQ') AS per_shipment_placed_by_Autoware_Inc"),
 "RV1": ("CTL-IR","AND T6.date_rank = 1","AND T6.date_rank = 2"),
 "RV2": ("CTL-IR","AND T6.date_rank = 1","AND T6.date_rank = 2"),
 "TM2": ("CTL-CRP","WHERE EXTRACT(YEAR FROM T1.ship_date) = 2017",
         "WHERE EXTRACT(YEAR FROM T1.ship_date) = 2018"),
}

def apply(find, repl):
    assert REFERENCE.count(find) == 1, f"anchor not unique ({REFERENCE.count(find)}): {find[:50]!r}"
    return REFERENCE.replace(find, repl)

def run(sql):
    try: return W.fresh().execute(sql).df(), None
    except Exception as e: return None, f"{type(e).__name__}: {e}"

def hsh(df): return hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()[:16]
def rt(df, s):
    b = io.StringIO(); df.to_csv(b, index=False); b.seek(0)
    return pd.read_csv(b, dtype=str, keep_default_na=True) if s else pd.read_csv(b)

def differs(a, b):
    if a.shape != b.shape: return True
    ka, kb = (x.sort_values(KEYS).reset_index(drop=True) for x in (a, b))
    try:
        pd.testing.assert_frame_equal(ka, kb, check_dtype=False, rtol=0, atol=0); return False
    except AssertionError: return True

def v_verified(r, m):
    _, u, mi = VERIFIED.check_corretness(rt(r, False), rt(m, False))
    return "SURVIVED" if (not u and not mi) else "rejected"
def v_default(r, m):
    a = DEFAULT.sort_by_keys(rt(r, True), KEYS); b = DEFAULT.sort_by_keys(rt(m, True), KEYS)
    return "SURVIVED" if DEFAULT.check_corretness(a, b)["match"] else "rejected"

ref, err = run(REFERENCE); assert err is None, err
rows = []
for oid, fam, f, r in SEM:
    mut, e = run(apply(f, r))
    if e:
        rows.append(dict(model_id="shipping.drivers", arm="A", operator_id=oid, mutation_family=fam,
                         witness_id="witness_w1", applicable="applicable", admissible="INADMISSIBLE:"+e[:40],
                         reference_output_hash=hsh(ref), mutant_output_hash="", evaluator_version="-",
                         evaluator_verdict="", matched_control_id="", control_verdict="",
                         pk_alignment_regime="", root_cause_category="")); continue
    if not differs(ref, mut):
        rows.append(dict(model_id="shipping.drivers", arm="A", operator_id=oid, mutation_family=fam,
                         witness_id="witness_w1", applicable="applicable", admissible="INADMISSIBLE:equivalent",
                         reference_output_hash=hsh(ref), mutant_output_hash=hsh(mut), evaluator_version="-",
                         evaluator_verdict="", matched_control_id="", control_verdict="",
                         pk_alignment_regime="", root_cause_category="")); continue
    cid, cf, cr = CTL[oid]
    ctl, ce = run(apply(cf, cr))
    ctl_ok = ce is None and differs(ref, ctl)
    for ver, fn in (("default", v_default), ("verified", v_verified)):
        rows.append(dict(model_id="shipping.drivers", arm="A", operator_id=oid, mutation_family=fam,
                         witness_id="witness_w1", applicable="applicable", admissible="admissible",
                         reference_output_hash=hsh(ref), mutant_output_hash=hsh(mut),
                         evaluator_version=ver, evaluator_verdict=fn(ref, mut),
                         matched_control_id=cid, control_verdict=fn(ref, ctl) if ctl_ok else "NONE",
                         pk_alignment_regime="inferred_key", root_cause_category=""))

with open("results/armA_results.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

print(f"{'op':<6}{'family':<24}{'admissible':<14}{'default':>10}{'verified':>10}{'ctl(vfy)':>11}")
print("-" * 75)
seen = set()
for r in rows:
    if r["operator_id"] in seen or r["evaluator_version"] == "-":
        if r["evaluator_version"] == "-":
            print(f"{r['operator_id']:<6}{r['mutation_family']:<24}{r['admissible'][:13]:<14}")
        continue
    d = next(x for x in rows if x["operator_id"] == r["operator_id"] and x["evaluator_version"] == "default")
    v = next(x for x in rows if x["operator_id"] == r["operator_id"] and x["evaluator_version"] == "verified")
    print(f"{r['operator_id']:<6}{r['mutation_family']:<24}{'admissible':<14}"
          f"{d['evaluator_verdict']:>10}{v['evaluator_verdict']:>10}{v['control_verdict']:>11}")
    seen.add(r["operator_id"])

adm = [r for r in rows if r["admissible"] == "admissible"]
for ver in ("default", "verified"):
    s = [r for r in adm if r["evaluator_version"] == ver]
    c = [r for r in s if r["control_verdict"] in ("rejected", "SURVIVED")]
    sr = sum(1 for r in s if r["evaluator_verdict"] == "rejected")
    cr = sum(1 for r in c if r["control_verdict"] == "rejected")
    print(f"\n{ver}:  SMDR {sr}/{len(s)}   CMDR {cr}/{len(c)}   "
          f"Delta {100*(cr/len(c) if c else 0) - 100*(sr/len(s) if s else 0):+.1f} pts")
