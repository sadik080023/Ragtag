import json, glob
import numpy as np
from scipy import stats

def cov_score(d):
    vals = list(d.values())
    if not vals: return np.nan
    m = {"yes": 1.0, "partial": 0.5, "no": 0.0}
    return np.mean([m.get(v, 0.0) for v in vals])

def edge_score(d):
    vals = list(d.values())
    if not vals: return np.nan
    return np.mean([1.0 if v == "yes" else 0.0 for v in vals])

def oracle_score(d):
    vals = list(d.values())
    if not vals: return np.nan
    return np.mean([1.0 if v else 0.0 for v in vals])

data = {}
for f in glob.glob("outputs/eval2/*/scores.jsonl"):
    for l in open(f):
        r = json.loads(l)
        res = r["result"]
        data.setdefault((r["run"], r["req_id"]), {})[r["method"]] = {
            "coverage": cov_score(res.get("condition_coverage", {})),
            "edge": edge_score(res.get("edge_coverage", {})),
            "oracle": oracle_score(res.get("oracle_correct", {})),
            "dup": float(res.get("duplicate_pairs", 0) or 0),
        }

print(f"Paired records: {len(data)} (expect 105 = 3 runs x 35 reqs)\n")
print(f"{'Metric':22} {'Base':>7} {'Ref':>7} {'MedianB/R':>11} {'p-value':>9} sig")
print("-" * 64)
for name, key in [("Condition coverage", "coverage"), ("Edge-case coverage", "edge"),
                  ("Oracle consistency", "oracle"), ("Duplicate pairs", "dup")]:
    b, r_ = [], []
    for k, v in data.items():
        if "baseline" in v and "refined" in v:
            bv, rv = v["baseline"][key], v["refined"][key]
            if not (np.isnan(bv) or np.isnan(rv)):
                b.append(bv); r_.append(rv)
    b, r_ = np.array(b), np.array(r_)
    try:
        p = stats.wilcoxon(b, r_).pvalue
    except Exception:
        p = float("nan")
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
    print(f"{name:22} {b.mean():>7.3f} {r_.mean():>7.3f} {np.median(b):>5.2f}/{np.median(r_):<5.2f} {p:>9.4f} {sig}")

print("\nPer-run mean coverage (reproducibility check):")
for run in ["run1", "run2", "run3"]:
    bc = [v["baseline"]["coverage"] for k, v in data.items() if k[0] == run and "baseline" in v]
    rc = [v["refined"]["coverage"] for k, v in data.items() if k[0] == run and "refined" in v]
    if bc and rc:
        print(f"  {run}: baseline={np.mean(bc):.3f}  refined={np.mean(rc):.3f}")
