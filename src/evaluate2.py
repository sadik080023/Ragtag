import json, os, time, glob
from datetime import datetime
from llm_client import chat, MODEL

SCORER_SYSTEM = """You are a STRICT test coverage checker. You do NOT give opinions — you verify against a checklist.
You receive: a REQUIREMENT, its CONDITION CHECKLIST, its EDGE-SCENARIO CHECKLIST, and a set of TEST CASES.
For EACH condition, decide:
- "yes" = at least one test case explicitly tests this condition
- "partial" = related but the condition itself is not directly tested
- "no" = not tested at all
For EACH edge scenario: "yes" or "no".
Also count how many test cases are duplicates of each other (duplicate_pairs), and for each condition marked yes/partial, check whether its test case's expected_result is consistent with the requirement (oracle_correct per condition: true/false).
Output ONLY JSON:
{"condition_coverage": {"<condition text>": "yes|partial|no", ...},
 "edge_coverage": {"<edge text>": "yes|no", ...},
 "duplicate_pairs": int,
 "oracle_correct": {"<condition text>": true|false, ...}}"""

def extract_json(text):
    text = text.replace("```json", "").replace("```", "")
    try:
        s, e = text.index("{"), text.rindex("}") + 1
        return json.loads(text[s:e])
    except Exception:
        return None

def find_file(pattern):
    files = sorted(glob.glob(pattern))
    return files[0] if files else None

def score(requirement, checklist, tcs):
    prompt = (
        "REQUIREMENT:\n" + requirement + "\n\n"
        "CONDITION CHECKLIST:\n" + json.dumps(checklist["conditions"], ensure_ascii=False) + "\n\n"
        "EDGE-SCENARIO CHECKLIST:\n" + json.dumps(checklist["edge_scenarios"], ensure_ascii=False) + "\n\n"
        "TEST CASES:\n" + json.dumps(tcs, ensure_ascii=False) + "\n\n"
        "Fill the checklist. Output ONLY the JSON."
    )
    for attempt in range(3):
        raw = chat(
            [{"role": "system", "content": SCORER_SYSTEM},
             {"role": "user", "content": prompt}],
            temperature=0.0,
        )
        s = extract_json(raw)
        if s and "condition_coverage" in s:
            return s
        time.sleep(5)
    return None

def main():
    checklists = json.load(open("data/annotations/conditions.json"))
    for run in ["run1", "run2", "run3"]:
        base_f = find_file(f"outputs/baseline/*_{run}.jsonl")
        fb_f   = find_file(f"outputs/feedback/*_{run}.jsonl")
        if not base_f or not fb_f:
            print(f"[WARN] missing files for {run}, skipping")
            continue
        os.makedirs(f"outputs/eval2/{run}", exist_ok=True)
        out_f = f"outputs/eval2/{run}/scores.jsonl"
        done = set()
        if os.path.exists(out_f):
            for l in open(out_f):
                r = json.loads(l)
                done.add((r["req_id"], r["method"]))
        base = {json.loads(l)["req_id"]: json.loads(l) for l in open(base_f)}
        fb   = {json.loads(l)["req_id"]: json.loads(l) for l in open(fb_f)}
        fout = open(out_f, "a")
        n_new = 0
        for rid in base:
            cl = checklists.get(rid)
            if not cl:
                continue
            for method, tcs in [("baseline", base[rid]["test_cases"]),
                                ("refined", fb.get(rid, {}).get("test_cases", []))]:
                if (rid, method) in done or not isinstance(tcs, list):
                    continue
                s = score(base[rid]["requirement"], cl, tcs)
                if s is None:
                    print(f"[FAIL] {run}/{rid}/{method}")
                    continue
                rec = {"run": run, "req_id": rid, "method": method,
                       "timestamp": datetime.now().isoformat(),
                       "checklist": cl, "result": s}
                fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fout.flush()
                n_new += 1
                print(f"[OK] {run}/{rid}/{method}")
                time.sleep(3)
        fout.close()
        print(f"{run}: {n_new} new records")

if __name__ == "__main__":
    main()
