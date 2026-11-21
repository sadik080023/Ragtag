import json, os, time, glob
from datetime import datetime
from llm_client import chat, MODEL

SCORER_SYSTEM = open("src/evaluate2.py").read().split('SCORER_SYSTEM = """')[1].split('"""')[0]

def extract_json(text):
    text = text.replace("```json", "").replace("```", "")
    try:
        s, e = text.index("{"), text.rindex("}") + 1
        return json.loads(text[s:e])
    except Exception:
        return None

checklists = json.load(open("data/annotations/conditions.json"))
os.makedirs("outputs/eval2", exist_ok=True)
out_f = "outputs/eval2/ablation_scores.jsonl"
done = set()
if os.path.exists(out_f):
    for l in open(out_f):
        r = json.loads(l)
        done.add((r["config"], r["req_id"]))

fout = open(out_f, "a")
for f in sorted(glob.glob("outputs/ablation/*.jsonl")):
    cfg = os.path.basename(f).replace("_run1.jsonl", "")
    for l in open(f):
        r = json.loads(l)
        rid, tcs = r["req_id"], r["test_cases"]
        if (cfg, rid) in done or not isinstance(tcs, list):
            continue
        cl = checklists.get(rid)
        if not cl:
            continue
        prompt = ("REQUIREMENT:\n" + r.get("requirement", "") + "\n\nCONDITION CHECKLIST:\n"
                  + json.dumps(cl["conditions"], ensure_ascii=False) + "\n\nEDGE-SCENARIO CHECKLIST:\n"
                  + json.dumps(cl["edge_scenarios"], ensure_ascii=False) + "\n\nTEST CASES:\n"
                  + json.dumps(tcs, ensure_ascii=False) + "\n\nFill the checklist. Output ONLY the JSON.")
        s = None
        for _ in range(3):
            raw = chat([{"role": "system", "content": SCORER_SYSTEM},
                        {"role": "user", "content": prompt}], temperature=0.0)
            s = extract_json(raw)
            if s and "condition_coverage" in s:
                break
            time.sleep(5)
        if not s:
            print(f"[FAIL] {cfg}/{rid}", flush=True)
            continue
        fout.write(json.dumps({"config": cfg, "req_id": rid, "method": cfg,
                               "timestamp": datetime.now().isoformat(),
                               "checklist": cl, "result": s}, ensure_ascii=False) + "\n")
        fout.flush()
        print(f"[OK] {cfg}/{rid}", flush=True)
        time.sleep(3)
fout.close()
print("scoring done", flush=True)
