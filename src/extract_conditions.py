import json, os, time
from llm_client import chat, MODEL

os.makedirs("data/annotations", exist_ok=True)
OUT = "data/annotations/conditions.json"

EXTRACT_SYSTEM = """You analyze software requirements for test evaluation.
Given a REQUIREMENT, output ONLY a JSON object:
{"conditions": ["atomic functional condition 1", ...], "edge_scenarios": ["boundary/negative scenario 1", ...]}
Rules:
- conditions: each must be separately TESTABLE (a test case can verify it). 3-8 items.
- edge_scenarios: boundary values, negative flows, alternative flows a tester should check. 2-5 items.
- Write them in English, short and precise."""

def extract_json(text):
    text = text.replace("```json", "").replace("```", "")
    try:
        s, e = text.index("{"), text.rindex("}") + 1
        obj = json.loads(text[s:e])
        if "conditions" in obj and "edge_scenarios" in obj:
            return obj
    except Exception:
        pass
    return None

def main():
    done = {}
    if os.path.exists(OUT):
        done = json.load(open(OUT))
    reqs = json.load(open("data/raw/requirements_seed.json"))
    for r in reqs:
        if r["id"] in done:
            print(f"[SKIP] {r['id']}")
            continue
        prompt = f"REQUIREMENT:\n{r['text']}\n\nExtract conditions and edge scenarios. Output ONLY the JSON."
        obj = None
        for _ in range(3):
            raw = chat(
                [{"role": "system", "content": EXTRACT_SYSTEM},
                 {"role": "user", "content": prompt}],
                temperature=0.0,
            )
            obj = extract_json(raw)
            if obj:
                break
            time.sleep(2)
        if obj is None:
            print(f"[FAIL] {r['id']}")
            continue
        done[r["id"]] = obj
        json.dump(done, open(OUT, "w"), ensure_ascii=False, indent=1)
        print(f"[OK] {r['id']}: {len(obj['conditions'])} conditions, {len(obj['edge_scenarios'])} edges")
        time.sleep(2)

if __name__ == "__main__":
    main()
