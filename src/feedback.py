import json, os, time
from datetime import datetime
from llm_client import chat, MODEL

RUN_ID = "run3"
os.makedirs("outputs/feedback", exist_ok=True)
IN  = f"outputs/baseline/{MODEL.replace('.', '_')}_{RUN_ID}.jsonl"
OUT = f"outputs/feedback/{MODEL.replace('.', '_')}_{RUN_ID}.jsonl"

JUDGE_SYSTEM = """You are a strict quality auditor for LLM-generated test cases.
Compare the ORIGINAL REQUIREMENT with the GENERATED TEST CASES and identify problems in 5 dimensions:
1. requirement_coverage: functional conditions in the requirement that NO test case covers
2. correctness: test steps that contradict or misinterpret the requirement
3. redundancy: duplicate or near-duplicate test cases (name them)
4. edge_case_completeness: missing boundary/negative/alternative-flow scenarios
5. oracle_consistency: expected results that contradict the requirement's stated behavior
Output ONLY valid JSON of this exact shape:
{"requirement_coverage": ["..."], "correctness": ["..."], "redundancy": ["..."], "edge_case_completeness": ["..."], "oracle_consistency": ["..."]}
Each issue = ONE short sentence. No problem in a dimension = empty list."""

REFINE_SYSTEM = "You are an expert software test engineer. You improve test cases based on audit feedback."

def is_valid(x):
    return isinstance(x, list) and len(x) > 0 and all(isinstance(t, dict) and "title" in t for t in x)

def extract_json(text, opener, closer):
    text = text.replace("```json", "").replace("```", "")
    try:
        s, e = text.index(opener), text.rindex(closer) + 1
        return json.loads(text[s:e])
    except Exception:
        return None

def main():
    reqs = {json.loads(l)["req_id"]: json.loads(l) for l in open(IN)}
    order = [json.loads(l)["req_id"] for l in open(IN)]
    done = {}
    if os.path.exists(OUT):
        for l in open(OUT):
            r = json.loads(l)
            if is_valid(r.get("test_cases")):
                done[r["req_id"]] = r
    results = dict(done)

    for rid in order:
        r = reqs[rid]
        tcs = r["test_cases"]
        if not is_valid(tcs):
            print(f"[SKIP] {rid}: baseline parse fail (run baseline.py first)")
            continue
        if rid in done:
            print(f"[SKIP] {rid}: already done")
            continue

        judge_prompt = (
            "ORIGINAL REQUIREMENT:\n" + r["requirement"] + "\n\n"
            "GENERATED TEST CASES:\n" + json.dumps(tcs, ensure_ascii=False) + "\n\n"
            "Now audit them with the 5 dimensions. Output ONLY the JSON."
        )
        fb_raw = chat(
            [{"role": "system", "content": JUDGE_SYSTEM},
             {"role": "user", "content": judge_prompt}],
            temperature=0.0,
        )
        feedback = extract_json(fb_raw, "{", "}")
        if feedback is None:
            feedback = {"raw_judge": fb_raw[:500]}
        n_issues = sum(len(v) for v in feedback.values()) if isinstance(feedback, dict) else "?"
        time.sleep(2)

        refine_prompt = (
            "ORIGINAL REQUIREMENT:\n" + r["requirement"] + "\n\n"
            "CURRENT TEST CASES:\n" + json.dumps(tcs, ensure_ascii=False) + "\n\n"
            "AUDIT FEEDBACK (JSON):\n" + json.dumps(feedback, ensure_ascii=False) + "\n\n"
            "Revise the test cases: fix every issue listed in the feedback, keep correct ones unchanged, "
            "add the missing scenarios. Output ONLY a JSON array of the revised test cases with the same "
            "schema (title, preconditions, test_steps, test_data, expected_result). "
            "No markdown fences, no commentary — ONLY the JSON array."
        )
        msgs = [
            {"role": "system", "content": REFINE_SYSTEM},
            {"role": "user", "content": refine_prompt},
        ]
        refined_raw = chat(msgs, temperature=0.2, max_tokens=4096)
        refined = extract_json(refined_raw, "[", "]")
        if not is_valid(refined):
            print(f"[REPAIR] {rid}: first parse failed, asking model to fix...")
            msgs.append({"role": "assistant", "content": refined_raw})
            msgs.append({"role": "user", "content": "Your output was not valid JSON. Output ONLY the corrected JSON array now. No fences, no commentary."})
            repair_raw = chat(msgs, temperature=0.0, max_tokens=4096)
            refined = extract_json(repair_raw, "[", "]")

        status = len(refined) if is_valid(refined) else "PARSE-FAIL"
        results[rid] = {
            "req_id": rid, "requirement": r["requirement"],
            "model": MODEL, "run_id": RUN_ID, "iteration": 1,
            "timestamp": datetime.now().isoformat(),
            "judge_feedback": feedback,
            "num_issues_found": n_issues,
            "test_cases": refined if is_valid(refined) else {"raw": "see-retry"},
        }
        print(f"[OK] {rid}: issues={n_issues}, refined={status}")
        time.sleep(2)

    with open(OUT, "w") as f:
        for rid in order:
            if rid in results:
                f.write(json.dumps(results[rid], ensure_ascii=False) + "\n")
    print("Saved to", OUT)

if __name__ == "__main__":
    main()
