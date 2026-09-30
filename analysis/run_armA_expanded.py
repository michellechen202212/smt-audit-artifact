"""Arm A (expanded) - SQL-level fidelity anchor over three repository-provided
transformations.

Provenance, stated exactly:
  * shipping.drivers  - repository-provided transformation (PR#18 only); output
    schema matches elt-bench/.../shipping/data_model.yaml exactly (8/8, ordered).
  * retails.customers - repository-provided transformation (example/); output
    schema matches tasks/retails/data_model.yaml exactly (8/8, ordered).
  * retails.nations   - same, 8/8 ordered.
NONE has been verified to reproduce the benchmark ground-truth CSV, because those
CSVs are not retrievable in this environment. We therefore call them
"repository-provided transformations whose output schema matches the task
specification", never "validated reference transformations".

Operators are the FROZEN catalogue ones only. No operator was created to fit these
transformations. Inapplicable operators are recorded NOT_APPLICABLE.
"""
import os, sys, csv, io, hashlib, warnings, importlib.util
warnings.filterwarnings("ignore")
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = ["witnesses", "references"]
import pandas as pd

def load(tag):
    s = importlib.util.spec_from_file_location(f"c_{tag}", f"evaluator/{tag}/comparator.py")
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
DEFAULT, VERIFIED = load("default"), load("verified")

import witness_w1, witness_retails
from reference_port import REFERENCE as SHIPPING

SUBJECTS = {
 "shipping.drivers":   (SHIPPING, witness_w1, ["driver_id"]),
 "retails.customers":  (open("references/retails_customers_port.sql").read(), witness_retails, ["c_custkey"]),
 "retails.nations":    (open("references/retails_nations_port.sql").read(), witness_retails, ["n_nationkey"]),
}

# (subject, operator, semantic anchor/replacement, control id, control anchor/replacement)
EDITS = {
"shipping.drivers": [
 ("GC1","grain_cardinality",
  "  SELECT DISTINCT driver_id AS driver_id\n  FROM shipping.shipment",
  "  SELECT driver_id AS driver_id\n  FROM shipping.shipment",
  "CTL-SDL","AND T6.date_rank = 1","AND T6.date_rank <= 2"),
 ("ME1","measures",
  "SELECT T2.driver_id AS driver_id, COUNT(*) AS num_shipments_2017",
  "SELECT T2.driver_id AS driver_id, COUNT(DISTINCT T1.cust_id) AS num_shipments_2017",
  "CTL-AOR","SELECT T2.driver_id AS driver_id, COUNT(*) AS num_shipments_2017",
  "SELECT T2.driver_id AS driver_id, COUNT(*) + 3 AS num_shipments_2017"),
 ("ME3","measures",
  "AS DOUBLE)\n      * 100 / COUNT(*) AS per","AS DOUBLE)\n      * 1 / COUNT(*) AS per",
  "CTL-AOR","AS DOUBLE)\n      * 100 / COUNT(*) AS per","AS DOUBLE)\n      * 150 / COUNT(*) AS per"),
 ("PP1","population_predicates",
  "LEFT JOIN num_shipments_2017_cte T2 ON T1.driver_id = T2.driver_id",
  "INNER JOIN num_shipments_2017_cte T2 ON T1.driver_id = T2.driver_id",
  "CTL-IR","FROM shipping.driver T1\n  LEFT JOIN num_shipments_2017_cte",
  "FROM (SELECT * FROM shipping.driver WHERE driver_id <> 4) T1\n  LEFT JOIN num_shipments_2017_cte"),
 ("PP2","population_predicates",
  "WHEN T2.cust_name ILIKE 'Autoware Inc' THEN 1","WHEN T2.cust_name ILIKE '%Autoware%' THEN 1",
  "CTL-IR","WHEN T2.cust_name ILIKE 'Autoware Inc' THEN 1","WHEN T2.cust_name ILIKE 'Other Co' THEN 1"),
 ("AB1","absence",
  "  CASE WHEN T2.num_shipments_2017 IS NULL THEN 0 ELSE T2.num_shipments_2017 END\n    AS num_shipments_2017",
  "  T2.num_shipments_2017 AS num_shipments_2017",
  "CTL-IR","  CASE WHEN T2.num_shipments_2017 IS NULL THEN 0 ELSE T2.num_shipments_2017 END\n    AS num_shipments_2017",
  "  CASE WHEN T2.num_shipments_2017 IS NULL THEN 999999 ELSE T2.num_shipments_2017 END\n    AS num_shipments_2017"),
 ("RV1","representative_value",
  "    rank() OVER (PARTITION BY driver_id ORDER BY ship_date, weight DESC) AS date_rank",
  "    row_number() OVER (PARTITION BY driver_id ORDER BY ship_date, weight DESC) AS date_rank",
  "CTL-IR","AND T6.date_rank = 1","AND T6.date_rank = 2"),
 ("RV2","representative_value",
  "rank() OVER (PARTITION BY driver_id ORDER BY ship_date, weight DESC)",
  "rank() OVER (PARTITION BY driver_id ORDER BY ship_date, weight ASC)",
  "CTL-IR","AND T6.date_rank = 1","AND T6.date_rank = 2"),
 ("TM2","temporal",
  "WHERE EXTRACT(YEAR FROM T1.ship_date) = 2017","WHERE EXTRACT(YEAR FROM T1.ship_date) >= 2017",
  "CTL-CRP","WHERE EXTRACT(YEAR FROM T1.ship_date) = 2017","WHERE EXTRACT(YEAR FROM T1.ship_date) = 2018"),
],
"retails.customers": [
 ("GC1","grain_cardinality",
  "  SELECT DISTINCT c_custkey\n  FROM retails.customer T1",
  "  SELECT c_custkey\n  FROM retails.customer T1",
  "CTL-SDL","  AND T4.price_rank = 1","  AND T4.price_rank <= 2"),
 ("ME1","measures",
  "SELECT o_custkey,\n    COUNT(*) AS num_orders",
  "SELECT o_custkey,\n    COUNT(DISTINCT o_totalprice) AS num_orders",
  "CTL-AOR","SELECT o_custkey,\n    COUNT(*) AS num_orders",
  "SELECT o_custkey,\n    COUNT(*) + 3 AS num_orders"),
 ("PP1","population_predicates",
  "  LEFT JOIN orders_cte T2 ON T1.c_custkey = T2.o_custkey",
  "  INNER JOIN orders_cte T2 ON T1.c_custkey = T2.o_custkey",
  "CTL-IR","FROM retails.customer T1\n  LEFT JOIN orders_cte",
  "FROM (SELECT * FROM retails.customer WHERE c_custkey <> 103) T1\n  LEFT JOIN orders_cte"),
 ("PP2","population_predicates",
  "AND T2.n_name ILIKE 'United States'","AND T2.n_name ILIKE 'United States%'",
  "CTL-IR","AND T2.n_name ILIKE 'United States'","AND T2.n_name ILIKE 'Canada'"),
 ("AB1","absence",
  "  CASE\n    WHEN T2.num_orders IS NULL THEN 0\n    ELSE T2.num_orders\n  END AS num_orders",
  "  T2.num_orders AS num_orders",
  "CTL-IR","  CASE\n    WHEN T2.num_orders IS NULL THEN 0\n    ELSE T2.num_orders\n  END AS num_orders",
  "  CASE\n    WHEN T2.num_orders IS NULL THEN 999999\n    ELSE T2.num_orders\n  END AS num_orders"),
 ("AB2","absence",
  "  T2.average_total_price_per_order,",
  "  COALESCE(CAST(T2.average_total_price_per_order AS VARCHAR),'N/A') AS average_total_price_per_order,",
  "CTL-IR","  T2.average_total_price_per_order,",
  "  COALESCE(CAST(T2.average_total_price_per_order AS VARCHAR),'ZZZQ') AS average_total_price_per_order,"),
 ("RV1","representative_value",
  "    RANK() over(\n      PARTITION by o_custkey\n      ORDER BY o_totalprice DESC,\n        o_orderdate\n    ) AS price_rank",
  "    ROW_NUMBER() over(\n      PARTITION by o_custkey\n      ORDER BY o_totalprice DESC,\n        o_orderdate\n    ) AS price_rank",
  "CTL-IR","  AND T4.price_rank = 1","  AND T4.price_rank = 2"),
 ("RV2","representative_value",
  "      ORDER BY o_totalprice DESC,\n        o_orderdate\n    ) AS price_rank",
  "      ORDER BY o_totalprice DESC,\n        o_orderdate DESC\n    ) AS price_rank",
  "CTL-IR","  AND T4.price_rank = 1","  AND T4.price_rank = 2"),
],
"retails.nations": [
 ("ME1","measures",
  "SELECT s_nationkey,\n    COUNT(s_suppkey) AS num_suppliers_in_debt",
  "SELECT s_nationkey,\n    COUNT(DISTINCT s_acctbal) AS num_suppliers_in_debt",
  "CTL-AOR","SELECT s_nationkey,\n    COUNT(s_suppkey) AS num_suppliers_in_debt",
  "SELECT s_nationkey,\n    COUNT(s_suppkey) + 3 AS num_suppliers_in_debt"),
 ("ME3","measures",
  "    ) AS DOUBLE\n    ) * 100 / COUNT(s_suppkey) AS per_indebted_suppliers",
  "    ) AS DOUBLE\n    ) * 1 / COUNT(s_suppkey) AS per_indebted_suppliers",
  "CTL-AOR","    ) AS DOUBLE\n    ) * 100 / COUNT(s_suppkey) AS per_indebted_suppliers",
  "    ) AS DOUBLE\n    ) * 150 / COUNT(s_suppkey) AS per_indebted_suppliers"),
 ("PP1","population_predicates",
  "  LEFT JOIN num_customers_cte T3 ON T1.n_nationkey = T3.c_nationkey",
  "  INNER JOIN num_customers_cte T3 ON T1.n_nationkey = T3.c_nationkey",
  "CTL-IR","FROM retails.nation T1\n  LEFT JOIN num_suppliers_in_debt_cte",
  "FROM (SELECT * FROM retails.nation WHERE n_nationkey <> 4) T1\n  LEFT JOIN num_suppliers_in_debt_cte"),
 ("AB1","absence",
  "  CASE\n    WHEN T3.num_customers IS NULL THEN 0\n    ELSE T3.num_customers\n  END AS num_customers",
  "  T3.num_customers AS num_customers",
  "CTL-IR","  CASE\n    WHEN T3.num_customers IS NULL THEN 0\n    ELSE T3.num_customers\n  END AS num_customers",
  "  CASE\n    WHEN T3.num_customers IS NULL THEN 999999\n    ELSE T3.num_customers\n  END AS num_customers"),
 ("AB2","absence",
  "  T6.per_indebted_suppliers\n","  COALESCE(CAST(T6.per_indebted_suppliers AS VARCHAR),'N/A') AS per_indebted_suppliers\n",
  "CTL-IR","  T6.per_indebted_suppliers\n","  COALESCE(CAST(T6.per_indebted_suppliers AS VARCHAR),'ZZZQ') AS per_indebted_suppliers\n"),
]}

# Frozen operators with NO applicable site in a given subject -> NOT_APPLICABLE
ALL_OPS = ["GC1","GC2","GC3","GC4","ME1","ME2","ME3","ME4","PP1","PP2","PP3",
           "TM1","TM2","TM3","TM4","AB1","AB2","AB3","RV1","RV2","RV3","RV4"]

def hsh(df): return hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()[:16]
def rt(df,s):
    b=io.StringIO(); df.to_csv(b,index=False); b.seek(0)
    return pd.read_csv(b,dtype=str,keep_default_na=True) if s else pd.read_csv(b)

def run(sql, wit):
    try: return wit.fresh().execute(sql).df(), None
    except Exception as e: return None, f"{type(e).__name__}: {str(e)[:70]}"

def differs(a,b,keys):
    if a.shape!=b.shape: return True
    try:
        ka,kb=(x.sort_values(keys).reset_index(drop=True) for x in (a,b))
        pd.testing.assert_frame_equal(ka,kb,check_dtype=False,rtol=0,atol=0); return False
    except AssertionError: return True
    except KeyError: return True

def v_ver(r,m):
    _,u,mi=VERIFIED.check_corretness(rt(r,False),rt(m,False))
    return "rejected" if (u or mi) else "SURVIVED"
def v_def(r,m,keys):
    a=DEFAULT.sort_by_keys(rt(r,True),keys); b=DEFAULT.sort_by_keys(rt(m,True),keys)
    return "SURVIVED" if DEFAULT.check_corretness(a,b)["match"] else "rejected"

rows=[]
for subj,(ref_sql,wit,keys) in SUBJECTS.items():
    ref,err=run(ref_sql,wit); assert err is None,(subj,err)
    present={e[0] for e in EDITS[subj]}
    for op in ALL_OPS:
        if op not in present:
            rows.append(dict(model_id=subj,arm="A",operator_id=op,mutation_family="",
                witness_id=wit.__name__,applicable="NOT_APPLICABLE",admissible="",
                reference_output_hash=hsh(ref),mutant_output_hash="",evaluator_version="-",
                evaluator_verdict="",matched_control_id="",control_verdict=""))
    for op,fam,sf,sr,cid,cf,cr in EDITS[subj]:
        if ref_sql.count(sf)!=1:
            rows.append(dict(model_id=subj,arm="A",operator_id=op,mutation_family=fam,
                witness_id=wit.__name__,applicable="applicable",
                admissible=f"INADMISSIBLE:anchor_count={ref_sql.count(sf)}",
                reference_output_hash=hsh(ref),mutant_output_hash="",evaluator_version="-",
                evaluator_verdict="",matched_control_id=cid,control_verdict="")); continue
        mut,e=run(ref_sql.replace(sf,sr),wit)
        if e or not differs(ref,mut,keys):
            rows.append(dict(model_id=subj,arm="A",operator_id=op,mutation_family=fam,
                witness_id=wit.__name__,applicable="applicable",
                admissible="INADMISSIBLE:"+(e if e else "equivalent_on_witness"),
                reference_output_hash=hsh(ref),mutant_output_hash=hsh(mut) if mut is not None else "",
                evaluator_version="-",evaluator_verdict="",matched_control_id=cid,
                control_verdict="")); continue
        ctl,ce=(run(ref_sql.replace(cf,cr),wit) if ref_sql.count(cf)==1 else (None,"anchor"))
        ctl_ok = ce is None and ctl is not None and differs(ref,ctl,keys)
        for ver in ("default","verified"):
            fn=(lambda r,m: v_def(r,m,keys)) if ver=="default" else v_ver
            rows.append(dict(model_id=subj,arm="A",operator_id=op,mutation_family=fam,
                witness_id=wit.__name__,applicable="applicable",admissible="admissible",
                reference_output_hash=hsh(ref),mutant_output_hash=hsh(mut),
                evaluator_version=ver,evaluator_verdict=fn(ref,mut),
                matched_control_id=cid,control_verdict=fn(ref,ctl) if ctl_ok else "NONE"))

with open("results/armA_expanded.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

print(f"{'subject':<20}{'op':<6}{'family':<22}{'default':>10}{'verified':>10}{'ctl(vfy)':>11}")
print("-"*79)
for subj in SUBJECTS:
    for op,fam,*_ in EDITS[subj]:
        d=[r for r in rows if r["model_id"]==subj and r["operator_id"]==op and r["evaluator_version"]=="default"]
        if not d:
            bad=next(r for r in rows if r["model_id"]==subj and r["operator_id"]==op)
            print(f"{subj:<20}{op:<6}{fam:<22}{bad['admissible'][:28]}"); continue
        v=next(r for r in rows if r["model_id"]==subj and r["operator_id"]==op and r["evaluator_version"]=="verified")
        print(f"{subj:<20}{op:<6}{fam:<22}{d[0]['evaluator_verdict']:>10}{v['evaluator_verdict']:>10}{v['control_verdict']:>11}")

adm=[r for r in rows if r["admissible"]=="admissible"]
print()
for ver in ("default","verified"):
    s=[r for r in adm if r["evaluator_version"]==ver]
    c=[r for r in s if r["control_verdict"] in ("rejected","SURVIVED")]
    sr=sum(1 for r in s if r["evaluator_verdict"]=="rejected")
    cr=sum(1 for r in c if r["control_verdict"]=="rejected")
    print(f"{ver:<9} SMDR {sr}/{len(s)} = {100*sr/len(s):.1f}%   CMDR {cr}/{len(c)} = {100*cr/len(c):.1f}%   "
          f"Delta {100*cr/len(c)-100*sr/len(s):+.1f} pts")
na=sum(1 for r in rows if r["applicable"]=="NOT_APPLICABLE")
inad=sum(1 for r in rows if r["admissible"].startswith("INADMISSIBLE"))
print(f"\nsubjects: {len(SUBJECTS)}   NOT_APPLICABLE: {na}   INADMISSIBLE: {inad}   admissible instances: {len(adm)//2} (x2 evaluators)")
