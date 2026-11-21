import json
import numpy as np
from scipy import stats

def cov(d):
    v = list(d.values())
    return np.mean([{"yes":1,"partial":.5,"no":0}.get(x,0) for x in v]) if v else np.nan
def edge(d):
    v = list(d.values())
    return np.mean([1.0 if x=="yes" else 0.0 for x in v]) if v else np.nan
def ora(d):
    v = list(d.values())
    return np.mean([1.0 if x else 0.0 for x in v]) if v else np.nan

def metrics(res):
    return {"coverage": cov(res.get("condition_coverage", {})),
            "edge": edge(res.get("edge_coverage", {})),
            "oracle": ora(res.get("oracle_correct", {}))}

methods = {}
for l in open("outputs/eval2/run1/scores.jsonl"):
    r = json.loads(l)
    methods.setdefault(r["method"], {})[r["req_id"]] = metrics(r["result"])
for l in open("outputs/eval2/ablation_scores.jsonl"):
    r = json.loads(l)
    methods.setdefault(r["config"], {})[r["req_id"]] = metrics(r["result"])

order = ["baseline", "refined", "abl_no_edge", "abl_no_cov"]
print(f"{'Metric':12}" + "".join(f"{m:>16}" for m in order))
for k in ["coverage", "edge", "oracle"]:
    row = f"{k:12}"
    for m in order:
        vals = [v[k] for v in methods.get(m, {}).values() if not np.isnan(v[k])]
        row += f"{np.mean(vals):>16.3f}" if vals else f"{'-':>16}"
    print(row)

print("\nPaired Wilcoxon (refined vs ablation, common requirements only):")
ref = methods.get("refined", {})
for cfg in ["abl_no_edge", "abl_no_cov"]:
    ab = methods.get(cfg, {})
    common = sorted(set(ref) & set(ab))
    for k in ["coverage", "edge"]:
        rb, abv = [], []
        for rid in common:
            a, b = ref[rid][k], ab[rid][k]
            if not (np.isnan(a) or np.isnan(b)):
                rb.append(a); abv.append(b)
        if len(rb) >= 10:
            try:
                p = stats.wilcoxon(rb, abv).pvalue
                print(f"  refined vs {cfg} [{k}]: n={len(rb)}, p={p:.4f}")
            except Exception as e:
                print(f"  refined vs {cfg} [{k}]: n={len(rb)}, wilcoxon failed: {e}")
        else:
            print(f"  refined vs {cfg} [{k}]: n={len(rb)} (too few paired samples)")
