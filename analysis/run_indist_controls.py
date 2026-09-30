"""EXPLORATORY (post-hoc) control-robustness check.

NOT confirmatory. The frozen confirmatory controls are unchanged and remain the
reported result. This analysis addresses one specific reviewer objection:

  "Controls such as 999999 or 'ZZZQ' are easier to detect merely because they are
   out-of-distribution, so the semantic/control gap is an artifact."

Construction: for each value-level probe, an ALTERNATIVE control replaces exactly
the SAME cells with an IN-DISTRIBUTION value - a value actually observed elsewhere
in the same column - preserving dtype and empirical support, and encoding no
semantic relationship. If the separation survives, out-of-distribution
detectability cannot explain it.

AB2 is excluded: its distinction is erased at CSV parse time, not by the
comparator (reported separately).
"""
import os, io, csv, glob, json, warnings, importlib.util, math, random
warnings.filterwarnings("ignore")
import pandas as pd, numpy as np
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load(tag):
    s=importlib.util.spec_from_file_location(f"c_{tag}",f"evaluator/{tag}/comparator.py")
    m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
DEFAULT, VERIFIED = load("default"), load("verified")
SK=json.load(open("evaluator/default/sort_key.json"))
CAP=2000; rng=random.Random(20260928)

def rt(df,s):
    b=io.StringIO(); df.to_csv(b,index=False); b.seek(0)
    return pd.read_csv(b,dtype=str,keep_default_na=True) if s else pd.read_csv(b)
def v_ver(r,m):
    _,u,mi=VERIFIED.check_corretness(rt(r,False),rt(m,False)); return "rejected" if (u or mi) else "SURVIVED"
def v_def(r,m,k):
    a=DEFAULT.sort_by_keys(rt(r,True),k); b=DEFAULT.sort_by_keys(rt(m,True),k)
    return "SURVIVED" if DEFAULT.check_corretness(a,b)["match"] else "rejected"
def exact_differs(a,b):
    if a.shape!=b.shape: return True
    for c in a.columns:
        x,y=a[c],b[c]
        nx,ny=x.isna().to_numpy(),y.isna().to_numpy()
        if not np.array_equal(nx,ny): return True
        if (x.astype(str).to_numpy()[~nx]!=y.astype(str).to_numpy()[~ny]).any(): return True
    return False
def numeric_cols(df,keys):
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
def me3_col(df,keys):
    for c in numeric_cols(df,keys):
        s=pd.to_numeric(df[c],errors="coerce"); nn=s.dropna()
        if len(nn) and nn.between(0,1).all() and nn[nn!=0].nunique()>=3: return c

def indist_pool(series, exclude):
    """Observed values from the same column, excluding the value being replaced."""
    vals=pd.to_numeric(series,errors="coerce").dropna()
    vals=vals[~vals.isin(exclude)]
    return vals.unique().tolist()

rows=[]
for path in sorted(glob.glob("corpus/*/*.csv")):
    db=os.path.basename(os.path.dirname(path)); t=os.path.basename(path)[:-4]
    keys=SK.get(db,{}).get(t,[])
    try: ref=pd.read_csv(path,nrows=CAP)
    except Exception: continue
    if ref.empty: continue

    jobs=[]
    c=null_zero_col(ref,keys)
    if c:
        s=pd.to_numeric(ref[c],errors="coerce")
        # AB1: nulls -> 0 ; in-distribution control: nulls -> an observed non-zero value
        pool=indist_pool(ref[c],[0])
        if pool:
            sem=ref.copy(); sem[c]=s.fillna(0)
            ctl=ref.copy(); ctl[c]=s.fillna(rng.choice(pool))
            jobs.append(("AB1",c,sem,ctl))
        # AB1R: zeros -> null ; in-distribution control: zeros -> observed non-zero value
        if pool:
            sem=ref.copy(); sem[c]=s.mask(s==0,np.nan)
            ctl=ref.copy(); ctl[c]=s.mask(s==0,rng.choice(pool))
            jobs.append(("AB1R",c,sem,ctl))
    c=me3_col(ref,keys)
    if c:
        s=pd.to_numeric(ref[c],errors="coerce")
        # ME3: x100 ; in-distribution control: permute the column's own observed values
        sem=ref.copy(); sem[c]=s*100
        perm=s.dropna().sample(frac=1,random_state=7).to_numpy()
        ctl=ref.copy(); col=s.copy(); col[col.notna()]=perm; ctl[c]=col
        jobs.append(("ME3",c,sem,ctl))

    for op,col,sem,ctl in jobs:
        if not exact_differs(ref,sem) or not exact_differs(ref,ctl): continue
        for ver in ("default","verified"):
            fn=(lambda r,m: v_def(r,m,keys)) if ver=="default" else v_ver
            rows.append(dict(model_id=f"{db}.{t}",operator_id=op,column=col,
                             evaluator_version=ver,semantic_verdict=fn(ref,sem),
                             indist_control_verdict=fn(ref,ctl)))

with open("results/exploratory_indist_controls.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

print("EXPLORATORY: in-distribution matched controls (same cells, observed values)\n")
for ver in ("default","verified"):
    R=[r for r in rows if r["evaluator_version"]==ver]
    sr=sum(1 for r in R if r["semantic_verdict"]=="rejected")
    cr=sum(1 for r in R if r["indist_control_verdict"]=="rejected")
    b01=sum(1 for r in R if r["semantic_verdict"]!="rejected" and r["indist_control_verdict"]=="rejected")
    b10=sum(1 for r in R if r["semantic_verdict"]=="rejected" and r["indist_control_verdict"]!="rejected")
    d=b01+b10
    p=(sum(math.comb(d,k) for k in range(0,min(b01,b10)+1))*2/(2**d)) if d else 1.0
    print(f"{ver}: eligible pairs {len(R)}")
    print(f"   semantic rejected        {sr}/{len(R)} = {100*sr/len(R):.1f}%")
    print(f"   in-dist control rejected {cr}/{len(R)} = {100*cr/len(R):.1f}%")
    print(f"   Delta {100*cr/len(R)-100*sr/len(R):+.1f} pts   discordant={d} (b01={b01}, b10={b10})"
          f"   exact two-sided p={p:.3g}")
    for op in ("ME3","AB1","AB1R"):
        t=[r for r in R if r["operator_id"]==op]
        if not t: continue
        print(f"     {op}: semantic {sum(1 for r in t if r['semantic_verdict']=='rejected')}/{len(t)}"
              f"   in-dist control {sum(1 for r in t if r['indist_control_verdict']=='rejected')}/{len(t)}")
    print()
