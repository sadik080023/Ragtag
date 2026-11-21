import json

human = json.load(open("data/annotations/human_answers.json"))
recs = {}
for l in open("outputs/eval2/run1/scores.jsonl"):
    r = json.loads(l)
    recs[(r["req_id"], r["method"])] = r

H2J = {"y": "yes", "p": "partial", "n": "no"}
total, agree = 0, 0
cat = {"conditions": [0, 0], "edges": [0, 0]}  # [agree, total]
mismatches = []

for rid, h in human.items():
    checklist = None
    for m in ["baseline", "refined"]:
        if (rid, m) in recs:
            checklist = recs[(rid, m)]["checklist"]
            break
    if not checklist:
        continue
    for side, method in [("b", "baseline"), ("r", "refined")]:
        if (rid, method) not in recs:
            continue
        res = recs[(rid, method)]["result"]
        cc, ec = res.get("condition_coverage", {}), res.get("edge_coverage", {})
        for hv, cond in zip(h["conditions"][side], checklist["conditions"]):
            jv = cc.get(cond)
            if hv is None or jv is None:
                continue
            total += 1; cat["conditions"][1] += 1
            if H2J[hv] == jv:
                agree += 1; cat["conditions"][0] += 1
            else:
                mismatches.append((rid, method, "cond", cond[:50], hv, jv))
        for hv, edge in zip(h["edges"][side], checklist["edge_scenarios"]):
            jv = ec.get(edge)
            if hv is None or jv is None:
                continue
            total += 1; cat["edges"][1] += 1
            if (hv == "y") == (jv == "yes"):
                agree += 1; cat["edges"][0] += 1
            else:
                mismatches.append((rid, method, "edge", edge[:50], hv, jv))

print(f"TOTAL comparable verdicts: {total}")
print(f"Overall agreement: {agree}/{total} = {agree/total*100:.1f}%")
for k in ["conditions", "edges"]:
    a, t = cat[k]
    if t:
        print(f"  {k}: {a}/{t} = {a/t*100:.1f}%")
print(f"\nMismatches ({len(mismatches)}):")
for m in mismatches[:15]:
    print(f"  {m[0]}/{m[1]}/{m[2]}: '{m[3]}' human={m[4]} judge={m[5]}")
