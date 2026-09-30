"""Confirmatory analysis - follows preregistration/analysis_plan.md exactly."""
import os, csv, math, collections
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

rows = list(csv.DictReader(open("results/armB_results.csv")))

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0, c-h), min(1, c+h))

def fmt(k, n):
    if n == 0: return "n/a"
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {100*k/n:5.1f}%  [{100*lo:4.1f},{100*hi:5.1f}]"

adm = [r for r in rows if r["admissible"] == "admissible" and r["evaluator_version"] != "-"]

print("="*78)
print("APPLICABILITY AND ADMISSIBILITY (denominators, per frozen analysis plan)")
print("="*78)
uniq = {}
for r in rows:
    k = (r["model_id"], r["operator_id"])
    if k not in uniq: uniq[k] = r
per_op = collections.defaultdict(lambda: collections.Counter())
for (m, o), r in uniq.items():
    per_op[o][r["applicable"] if r["applicable"] == "NOT_APPLICABLE" else r["admissible"]] += 1
print(f"{'op':<6}{'family':<24}{'applicable':>11}{'admissible':>12}{'not_appl':>10}{'inadm':>8}")
print("-"*78)
fam_of = {r["operator_id"]: r["mutation_family"] for r in rows}
for o in ["GC1","PP1","RV1","ME3","AB1","AB1R","AB2"]:
    c = per_op[o]
    na = c["NOT_APPLICABLE"]; ad = c["admissible"]; inad = c["INADMISSIBLE"]
    print(f"{o:<6}{fam_of[o]:<24}{ad+inad:>11}{ad:>12}{na:>10}{inad:>8}")

print()
print("="*78)
print("RQ1 - SEMANTIC DISCRIMINATIVE POWER (SMDR by evaluator version)")
print("="*78)
for ver in ("default", "verified"):
    s = [r for r in adm if r["evaluator_version"] == ver]
    rej = sum(1 for r in s if r["evaluator_verdict"] == "rejected")
    print(f"  SMDR_{ver:<9} {fmt(rej, len(s))}")

print()
print("="*78)
print("RQ2 - SELECTIVITY (CMDR, Delta)")
print("="*78)
for ver in ("default", "verified"):
    s = [r for r in adm if r["evaluator_version"] == ver]
    c = [r for r in s if r["control_verdict"] in ("rejected", "SURVIVED")]
    srej = sum(1 for r in s if r["evaluator_verdict"] == "rejected")
    crej = sum(1 for r in c if r["control_verdict"] == "rejected")
    smdr = srej/len(s) if s else 0
    cmdr = crej/len(c) if c else 0
    print(f"  {ver}")
    print(f"     SMDR  {fmt(srej, len(s))}")
    print(f"     CMDR  {fmt(crej, len(c))}")
    print(f"     Delta = {100*(cmdr-smdr):+.1f} pts")
    disc = sum(1 for r in s if r["control_verdict"] in ("rejected","SURVIVED")
               and (r["evaluator_verdict"]=="rejected") != (r["control_verdict"]=="rejected"))
    print(f"     discordant pairs = {disc}  ->  McNemar {'permitted' if disc>=20 else 'NOT permitted (<20), descriptive only'}")

print()
print("="*78)
print("FAMILY x EVALUATOR (survival of semantic probes)")
print("="*78)
print(f"{'operator':<8}{'family':<24}{'default':>22}{'verified':>22}")
print("-"*78)
for o in ["GC1","PP1","RV1","ME3","AB1","AB1R","AB2"]:
    line = f"{o:<8}{fam_of[o]:<24}"
    for ver in ("default","verified"):
        s = [r for r in adm if r["operator_id"]==o and r["evaluator_version"]==ver]
        rej = sum(1 for r in s if r["evaluator_verdict"]=="rejected")
        line += f"{fmt(rej,len(s)):>22}"
    print(line)

print()
print("="*78)
print("PK-ALIGNMENT REGIME STRATIFICATION (Verified evaluator)")
print("="*78)
for reg in sorted({r["pk_alignment_regime"] for r in adm}):
    s = [r for r in adm if r["evaluator_version"]=="verified" and r["pk_alignment_regime"]==reg]
    rej = sum(1 for r in s if r["evaluator_verdict"]=="rejected")
    print(f"  {reg:<22} SMDR {fmt(rej,len(s))}")

print()
print("="*78)
print("ADVANCE PREDICTION SCORING (registered before the run)")
print("="*78)
s = [r for r in adm if r["evaluator_version"]=="verified" and r["prediction_correct"] in ("True","False")]
ok = sum(1 for r in s if r["prediction_correct"]=="True")
print(f"  overall  {fmt(ok,len(s))}")
for o in ["GC1","PP1","RV1","ME3","AB1","AB1R","AB2"]:
    t = [r for r in s if r["operator_id"]==o]
    k = sum(1 for r in t if r["prediction_correct"]=="True")
    pred = t[0]["prediction"] if t else "-"
    print(f"    {o:<6} predicted {pred:<9} {fmt(k,len(t))}")
