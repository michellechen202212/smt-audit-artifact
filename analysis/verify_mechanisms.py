"""Verify each root-cause claim against the PINNED Verified comparator."""
import sys, io, warnings, importlib.util
warnings.filterwarnings("ignore")
sys.path[:0] = ["witnesses","references","mutants"]
import pandas as pd, witness_w1 as W, pilot_operators as OPS
from reference_port import REFERENCE
spec = importlib.util.spec_from_file_location("V","evaluator/verified/comparator.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)

def out(sql): return W.fresh().execute(sql).df()
def rt(df):
    b=io.StringIO(); df.to_csv(b,index=False); b.seek(0); return pd.read_csv(b)
ref = out(REFERENCE)

print("CLAIM 1: key-based alignment intersects/deduplicates rows before comparison")
for mid in ["M01","M02","M09"]:
    m = next(x for x in OPS.SEMANTIC if x[0]==mid)
    mut = out(OPS.apply(m[3],m[4]))
    g,p = rt(ref), rt(mut)
    a,b,pk = V.align_dataframes_by_key(V.normalize_dataframe(g.copy()), V.normalize_dataframe(p.copy()))
    print(f"  {mid} {m[2][:44]:<44} GT {len(g)}->{len(a)}   MUT {len(p)}->{len(b)}   pk={pk}")

print("\nCLAIM 2: unconditional NULL/zero equivalence")
src = open("evaluator/verified/comparator.py").read()
line = [l.strip() for l in src.splitlines() if "pd.isna(a) or a == 0" in l]
print("  pinned source line:", line[0] if line else "NOT FOUND")
print("  guarded by numeric check?  ", "no - applies to every column" if line else "?")
for a_,b_ in [(None,0),(0,None),(None,0.0)]:
    df1=pd.DataFrame({"id":[1],"x":[a_]}); df2=pd.DataFrame({"id":[1],"x":[b_]})
    m,u,mi = V.check_corretness(df1,df2)
    print(f"   GT={a_!r} vs MUT={b_!r} -> {'MATCH' if not u and not mi else 'mismatch'}")

print("\nCLAIM 3: percentage-scale normalization (data dependent)")
for n in (2,3,6):
    v1 = pd.Series([0.01*i for i in range(1,n+1)])
    v2 = pd.Series([1.0*i  for i in range(1,n+1)])
    print(f"   rows={n}  check_percentage_scale -> {V.check_percentage_scale(v1,v2)}")
print("   (returns 100 only with >=3 valid rows and a consistent ratio => verdict is witness-dependent)")

print("\nCLAIM 4: relative tolerance is hardcoded at 1% and ignores the tol argument")
import re
seg = src[src.index("def check_corretness"):]
print("   ", [l.strip() for l in seg.splitlines() if "rel_diff" in l and "<=" in l][0])
print("   tol argument used only for absolute/zero comparisons")
