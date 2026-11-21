import json, os, time, glob, requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
API_KEY, BASE_URL = os.getenv("API_KEY"), os.getenv("BASE_URL")
GEN_MODEL = "glm-4.7-flash"

os.makedirs("outputs/ablation", exist_ok=True)

CONFIGS = {
    "abl_no_edge": ["requirement_coverage", "correctness", "redundancy", "oracle_consistency"],
    "abl_no_cov":  ["correctness", "redundancy", "edge_case_completeness", "oracle_consistency"],
}
DIM_TEXT = {
    "requirement_coverage": "requirement_coverage: functional conditions in the requirement that NO test case covers",
    "correctness": "correctness: test steps that contradict or misinterpret the requirement",
    "redundancy": "redundancy: duplicate or near-duplicate test cases (name them)",
    "edge_case_completeness": "edge_case_completeness: missing boundary/negative/alternative-flow scenarios",
    "oracle_consistency": "oracle_consistency: expected results that contradict the requirement's stated behavior",
}
REFINE_SYSTEM = "You are an expert software test engineer. You improve test cases based on audit feedback."

def chat_gen(messages, temperature=0.2, max_tokens=4096, retries=8):
    last = "unknown"
    for a in range(retries):
        try:
            r = requests.post(BASE_URL + "/chat/completions",
                headers={"Authorization": "Bearer " + API_KEY},
                json={"model": GEN_MODEL, "messages": messages,
                      "temperature": temperature, "max_tokens": max_tokens}, timeout=60)
            if r.status_code == 200:
                c = r.json()["choices"][0]["message"].get("content") or ""
                if c.strip():
                    return c
                last = "empty content"
            else:
                last = f"HTTP {r.status_code}: {r.text[:150]}"
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:150]}"
        w = min(10 * (2 ** a), 90)
        print(f"  [retry {a+1}/{retries}] {last}", flush=True)
        time.sleep(w)
    raise RuntimeError("gen failed: " + last)

def extract(text, o, c):
    text = text.replace("```json", "").replace("```", "")
    try:
        s, e = text.index(o), text.rindex(c) + 1
        return json.loads(text[s:e])
    except Exception:
        return None

def is_valid(x):
    return isinstance(x, list) and len(x) > 0 and all(isinstance(t, dict) and "title" in t for t in x)

def judge_system(dims):
    keys = ", ".join(f'"{d}": ["..."]' for d in dims)
    body = "\n".join(f"{i+1}. {DIM_TEXT[d]}" for i, d in enumerate(dims))
    return ("You are a strict quality auditor for LLM-generated test cases.\nCompare the ORIGINAL REQUIREMENT "
            "with the GENERATED TEST CASES and identify problems in these dimensions:\n" + body +
            f"\nOutput ONLY valid JSON: {{{keys}}}\nEach issue = ONE short sentence. No problem in a dimension = empty list.")

def main():
    bf = sorted(glob.glob("outputs/baseline/*_run1.jsonl"))[0]
    order, base = [], {}
    for l in open(bf):
        r = json.loads(l)
        order.append(r["req_id"]); base[r["req_id"]] = r
    for cfg, dims in CONFIGS.items():
        out = f"outputs/ablation/{cfg}_run1.jsonl"
        done = {}
        if os.path.exists(out):
            for l in open(out):
                r = json.loads(l)
                if is_valid(r.get("test_cases")):
                    done[r["req_id"]] = r
        fout = open(out, "a")
        for rid in order:
            if rid in done:
                print(f"[SKIP] {cfg}/{rid}", flush=True)
                continue
            tcs = base[rid]["test_cases"]
            if not is_valid(tcs):
                continue
            try:
                jp = ("ORIGINAL REQUIREMENT:\n" + base[rid]["requirement"] + "\n\nGENERATED TEST CASES:\n"
                      + json.dumps(tcs, ensure_ascii=False) + "\n\nNow audit them. Output ONLY the JSON.")
                fb = extract(chat_gen([{"role": "system", "content": judge_system(dims)},
                                       {"role": "user", "content": jp}], temperature=0.0), "{", "}") or {}
                time.sleep(2)
                rp = ("ORIGINAL REQUIREMENT:\n" + base[rid]["requirement"] + "\n\nCURRENT TEST CASES:\n"
                      + json.dumps(tcs, ensure_ascii=False) + "\n\nAUDIT FEEDBACK (JSON):\n"
                      + json.dumps(fb, ensure_ascii=False) + "\n\nRevise the test cases: fix every issue listed, "
                      "keep correct ones unchanged, add missing scenarios. Output ONLY a JSON array of revised "
                      "test cases (title, preconditions, test_steps, test_data, expected_result). No fences, no commentary.")
                refined = extract(chat_gen([{"role": "system", "content": REFINE_SYSTEM},
                                            {"role": "user", "content": rp}], temperature=0.2), "[", "]")
                if not is_valid(refined):
                    refined = extract(chat_gen([{"role": "system", "content": REFINE_SYSTEM},
                        {"role": "user", "content": rp + "\n\nIMPORTANT: output ONLY the JSON array."}],
                        temperature=0.0), "[", "]")
            except RuntimeError as e:
                print(f"[FAIL-SKIP] {cfg}/{rid} -> {str(e)[:80]}", flush=True)
                continue
            rec = {"req_id": rid, "config": cfg, "removed_dims": [d for d in DIM_TEXT if d not in dims],
                   "timestamp": datetime.now().isoformat(), "feedback": fb,
                   "test_cases": refined if is_valid(refined) else {"raw": "fail"}}
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n"); fout.flush()
            print(f"[OK] {cfg}/{rid}: {len(rec['test_cases']) if is_valid(refined) else 'FAIL'}", flush=True)
            time.sleep(2)
        fout.close()
        print(f"=== {cfg} done ===", flush=True)

if __name__ == "__main__":
    main()
