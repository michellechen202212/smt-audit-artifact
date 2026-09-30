"""Phase 4 - mechanism ablation.

A root-cause claim is valid only if:
  (1) the instance survives with the mechanism enabled;
  (2) the instance is rejected when that mechanism ALONE is disabled;
  (3) no unrelated evaluator behaviour changes.

Each ablation is a single textual patch on the pinned Verified comparator,
applied in isolation. The patch is asserted to match exactly once, so the
ablation cannot silently alter anything else.
"""
import os, csv, glob, json, importlib.util, warnings, collections
warnings.filterwarnings("ignore")
import pandas as pd, numpy as np, yaml
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE = open("evaluator/verified/comparator.py").read()

ABLATIONS = {
 # disable unconditional exact-duplicate removal (applies to BOTH sides)
 "dedup_normalize": (
   "    df_norm = df_norm.drop_duplicates()\n",
   "    pass  # ABLATED: exact-duplicate removal\n"),
 # disable unconditional NULL == 0 equivalence
 "null_zero_equivalence": (
   "            if (pd.isna(a) or a == 0) and (pd.isna(b) or b == 0):\n"
   "                match_count += 1\n"
   "                continue\n",
   "            if False:  # ABLATED: null/zero equivalence\n"
   "                match_count += 1\n"
   "                continue\n"),
 # disable percentage-scale auto-rescaling
 "scale_normalization": (
   "        scale_factor = check_percentage_scale(v1_normalized, v2_normalized)\n",
   "        scale_factor = 1  # ABLATED: percentage-scale normalization\n"),
 # disable key-based row alignment (compare as given)
 "alignment_rowset": (
   "    df_gt_aligned, df_pred_aligned, pk_col = align_dataframes_by_key("
   "df_gt_norm.copy(), df_norm.copy())\n",
   "    df_gt_aligned, df_pred_aligned, pk_col = df_gt_norm, df_norm, None  "
   "# ABLATED: key alignment\n"),
}

def build(name):
    if name == "none":
        src = BASE
    else:
        find, repl = ABLATIONS[name]
        assert BASE.count(find) == 1, f"patch anchor not unique for {name}: {BASE.count(find)}"
        src = BASE.replace(find, repl)
    path = f"/tmp/abl_{name}.py"; open(path, "w").write(src)
    spec = importlib.util.spec_from_file_location(f"abl_{name}", path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

MODS = {n: build(n) for n in ["none"] + list(ABLATIONS)}
print("ablations built (single-anchor patches verified unique):", list(ABLATIONS))

# rebuild the probes we need (same frozen code path as run_armB)
import importlib.util as iu
spec = iu.spec_from_file_location("rb", "analysis/run_armB.py")

RULES = yaml.safe_load(open("preregistration/witness_rules.yaml"))
CAP = RULES["row_cap"]
SORT_KEYS = json.load(open("evaluator/default/sort_key.json"))

def numeric_cols(df, keys):
    out=[]
    for c in df.columns:
        if c.lower() in {k.lower() for k in keys}: continue
        s=pd.to_numeric(df[c],errors="coerce")
        if s.notna().sum()>=max(3,0.5*df[c].notna().sum()) and df[c].notna().sum()>0: out.append(c)
    return out
def null_zero_col(df,keys):
    for c in numeric_cols(df,keys):
        s=pd.to_numeric(df[c],errors="coerce")
        if df[c].isna().any() and (s==0).any(): return c
def P_GC1(df,k):
    return pd.concat([df.iloc[[0]],df],ignore_index=True) if len(df)>=2 and k else None
def P_PP1(df,k):
    return df.iloc[:-max(1,int(len(df)*0.2))].reset_index(drop=True) if len(df)>=5 else None
def P_ME3(df,k):
    for c in numeric_cols(df,k):
        s=pd.to_numeric(df[c],errors="coerce"); nn=s.dropna()
        if len(nn) and nn.between(0,1).all() and nn[nn!=0].nunique()>=3:
            m=df.copy(); m[c]=s*100; return m
def P_AB1(df,k):
    c=null_zero_col(df,k)
    if c: m=df.copy(); m[c]=pd.to_numeric(m[c],errors="coerce").fillna(0); return m
def P_AB1R(df,k):
    c=null_zero_col(df,k)
    if c:
        m=df.copy(); s=pd.to_numeric(m[c],errors="coerce"); m[c]=s.mask(s==0,np.nan); return m

PROBES={"GC1":P_GC1,"PP1":P_PP1,"ME3":P_ME3,"AB1":P_AB1,"AB1R":P_AB1R}
# expected responsible mechanism, registered in advance
EXPECT={"GC1":"dedup_normalize","PP1":"alignment_rowset","ME3":"scale_normalization",
        "AB1":"null_zero_equivalence","AB1R":"null_zero_equivalence"}

def _rt(df):
    import io as _io
    b=_io.StringIO(); df.to_csv(b,index=False); b.seek(0); return pd.read_csv(b)

def verdict(mod, ref, mut):
    try:
        m,u,miss = mod.check_corretness(_rt(ref), _rt(mut))
        return "SURVIVED" if (not u and not miss) else "rejected"
    except Exception as e:
        return f"ERROR:{type(e).__name__}"

rows=[]
for path in sorted(glob.glob("corpus/*/*.csv")):
    db=os.path.basename(os.path.dirname(path)); tbl=os.path.basename(path)[:-4]
    keys=SORT_KEYS.get(db,{}).get(tbl,[])
    try: ref=pd.read_csv(path,nrows=CAP)
    except Exception: continue
    if ref.empty: continue
    for oid,pf in PROBES.items():
        mut=pf(ref,keys)
        if mut is None: continue
        base=verdict(MODS["none"],ref,mut)
        if base!="SURVIVED": continue          # only survivors need attribution
        flips={n:verdict(MODS[n],ref,mut) for n in ABLATIONS}
        responsible=[n for n,v in flips.items() if v=="rejected"]
        rows.append(dict(model_id=f"{db}.{tbl}",operator_id=oid,baseline=base,
                         expected_mechanism=EXPECT[oid],
                         flipped_by=";".join(responsible) if responsible else "NONE",
                         n_mechanisms_flipping=len(responsible),
                         attribution=("attributed" if len(responsible)==1 else
                                      "unattributed" if not responsible else "multiple"),
                         matches_expected=str(responsible==[EXPECT[oid]])))

with open("results/mechanism_ablation.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

print(f"\nsurvivors analysed: {len(rows)}")
print(f"{'operator':<8}{'survivors':>10}{'attributed':>12}{'matches expected':>18}{'unattributed':>14}")
print("-"*64)
agg=collections.defaultdict(lambda: collections.Counter())
for r in rows:
    a=agg[r["operator_id"]]; a["n"]+=1
    a["attr"]+= r["attribution"]=="attributed"
    a["match"]+= r["matches_expected"]=="True"
    a["un"]+= r["attribution"]=="unattributed"
for o,c in agg.items():
    print(f"{o:<8}{c['n']:>10}{c['attr']:>12}{c['match']:>18}{c['un']:>14}")
print("-"*64)
t=collections.Counter()
for r in rows: t[r["flipped_by"]]+=1
print("\nmechanism responsible (single-mechanism ablation flips survivor -> rejected):")
for k,v in t.most_common(): print(f"  {k or 'NONE':<28} {v}")
