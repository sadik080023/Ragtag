import json, glob
reqs = {json.loads(l)["req_id"]: json.loads(l)["requirement"] for l in open(sorted(glob.glob("outputs/baseline/*_run1.jsonl"))[0])}
for f in glob.glob("outputs/ablation/*.jsonl"):
    recs = [json.loads(l) for l in open(f)]
    for r in recs:
        r["requirement"] = reqs.get(r["req_id"], "")
    with open(f, "w") as fo:
        for r in recs:
            fo.write(json.dumps(r, ensure_ascii=False) + "\n")
print("requirements added")
