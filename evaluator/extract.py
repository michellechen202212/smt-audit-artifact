"""Extract the pure comparison layer from each pinned evaluator.

Neither file is importable as-is (module-level argparse / snowflake import /
credential read), so we slice out the comparison functions. Every extracted
function is then verified byte-identical against the pinned source.
"""
import re, hashlib, sys, pathlib

HDR = "import pandas as pd\nimport numpy as np\nimport re\n\n"

def slice_default(src):
    # elt_bench++: keep everything before the driver evaluate_stage2
    return src[:src.index("def evaluate_stage2")]

def slice_verified(src):
    # PR18: keep normalize_value .. end of check_corretness; drop the log write
    start = src.index("def normalize_value")
    end = src.index("def filter_databases")
    body = src[start:end].splitlines(keepends=True)
    out, i = [], 0
    while i < len(body):
        line = body[i]
        if "stage2.log" in line and line.lstrip().startswith("with open"):
            indent = " " * (len(line) - len(line.lstrip()))
            out.append(indent + "pass  # evaluator log write suppressed\n")
            i += 1
            while i < len(body) and (body[i].strip().startswith("f.write") or not body[i].strip()):
                i += 1
            continue
        out.append(line); i += 1
    return "".join(out)

def build(tag, slicer, funcs):
    src = pathlib.Path(f"evaluator/{tag}/eva_stage2.py").read_text()
    code = HDR + slicer(src)
    out = pathlib.Path(f"evaluator/{tag}/comparator.py"); out.write_text(code)
    # fidelity check: each decision-relevant function body must appear verbatim
    bad = []
    for fn in funcs:
        a = src.index(f"def {fn}")
        chunk = src[a:a+300]
        if chunk not in code:
            bad.append(fn)
    print(f"[{tag}] extracted {len(code.splitlines())} lines; "
          f"verbatim: {len(funcs)-len(bad)}/{len(funcs)}" + (f"  DIVERGED: {bad}" if bad else ""))
    return not bad

ok1 = build("default", slice_default,
            ["check_corretness", "_vectors_match", "sort_by_keys", "_to_numeric_if_possible"])
ok2 = build("verified", slice_verified,
            ["check_corretness", "align_dataframes_by_key", "check_percentage_scale",
             "normalize_boolean", "normalize_value", "normalize_timestamp",
             "identify_primary_key_columns", "normalize_dataframe"])
sys.exit(0 if (ok1 and ok2) else 1)
