import json, os, time
from datetime import datetime
from llm_client import chat, MODEL
from sentence_transformers import SentenceTransformer, util

RUN_ID = "run3"
os.makedirs("outputs/baseline", exist_ok=True)
OUT = f"outputs/baseline/{MODEL.replace('.', '_')}_{RUN_ID}.jsonl"

BANK = [
  {
    "requirement": "The system shall allow a user to register with a username, email, and password. The username must be unique.",
    "test_cases": [
      {"title": "Register with unique username", "preconditions": ["User is on the registration page"], "test_steps": ["Enter a unique username", "Enter a valid email", "Enter a password", "Submit the form"], "test_data": ["username: newuser1", "email: newuser1@test.com"], "expected_result": "Account is created and confirmation message is shown."},
      {"title": "Register with duplicate username", "preconditions": ["Username 'admin' already exists"], "test_steps": ["Enter username 'admin'", "Fill other valid fields", "Submit"], "test_data": ["username: admin"], "expected_result": "Registration is rejected with a message that the username is already taken."},
      {"title": "Register with invalid email", "preconditions": ["User is on the registration page"], "test_steps": ["Enter valid username", "Enter email without '@'", "Submit"], "test_data": ["email: notanemail"], "expected_result": "Form shows a validation error for the email field."}
    ]
  },
  {
    "requirement": "The system shall allow users to add items to a wishlist. Each wishlist can hold at most 50 items.",
    "test_cases": [
      {"title": "Add item to empty wishlist", "preconditions": ["User is logged in", "Wishlist is empty"], "test_steps": ["Open a product page", "Click 'Add to wishlist'"], "test_data": ["product: P001"], "expected_result": "Product is added to the wishlist and the wishlist count becomes 1."},
      {"title": "Add item when wishlist is full", "preconditions": ["Wishlist already has 50 items"], "test_steps": ["Try to add one more product to the wishlist"], "test_data": ["product: P051"], "expected_result": "Item is not added and user is informed that the wishlist is full."}
    ]
  },
  {
    "requirement": "The system shall send an order confirmation email after a successful payment. The email must include order number, items, and total amount.",
    "test_cases": [
      {"title": "Confirmation email content", "preconditions": ["User has completed payment for order #1234"], "test_steps": ["Complete a payment", "Check the inbox of the registered email"], "test_data": ["order: #1234"], "expected_result": "Email received containing order number #1234, ordered items, and correct total amount."},
      {"title": "No email on failed payment", "preconditions": ["Payment fails due to insufficient funds"], "test_steps": ["Attempt payment that fails", "Check email inbox"], "test_data": ["card: valid but insufficient funds"], "expected_result": "No order confirmation email is sent."}
    ]
  }
]

SYSTEM = "You are an expert software test engineer. You generate structured test cases from natural language requirements."

def is_valid(x):
    return isinstance(x, list) and len(x) > 0 and all(isinstance(t, dict) and "title" in t for t in x)

def extract_json(text, opener, closer):
    text = text.replace("```json", "").replace("```", "")
    try:
        s, e = text.index(opener), text.rindex(closer) + 1
        return json.loads(text[s:e])
    except Exception:
        return None

def build_prompt(req_text, examples):
    ex = ""
    for e in examples:
        ex += "Requirement:\n" + e["requirement"] + "\nTest cases (JSON):\n" + json.dumps(e["test_cases"], indent=1) + "\n\n"
    return (
        "Below are examples of requirements and their test cases.\n\n"
        + ex
        + "Requirement:\n" + req_text + "\n\n"
        + "Now generate test cases for the last requirement. Output ONLY a JSON array where each element has: "
        + '"title" (string), "preconditions" (list of strings), "test_steps" (list of strings), '
        + '"test_data" (list of strings), "expected_result" (string). No markdown fences, no commentary.'
    )

def main():
    reqs = json.load(open("data/raw/requirements_seed.json"))
    done = {}
    if os.path.exists(OUT):
        for l in open(OUT):
            r = json.loads(l)
            if is_valid(r.get("test_cases")):
                done[r["req_id"]] = r

    emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    bank_emb = emb.encode([b["requirement"] for b in BANK], convert_to_tensor=True)
    results = dict(done)

    for r in reqs:
        if r["id"] in done:
            print(f"[SKIP] {r['id']}: already done")
            continue
        q = emb.encode(r["text"], convert_to_tensor=True)
        top = util.cos_sim(q, bank_emb)[0].argsort(descending=True)[:2].tolist()
        examples = [BANK[i] for i in top]
        msgs = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": build_prompt(r["text"], examples)},
        ]
        tcs = extract_json(chat(msgs, temperature=0.2, max_tokens=4096), "[", "]")
        if not is_valid(tcs):
            print(f"[REPAIR] {r['id']}: retrying with stricter instruction...")
            msgs.append({"role": "assistant", "content": "..."})
            msgs.append({"role": "user", "content": "Output ONLY the JSON array now. No fences, no commentary."})
            tcs = extract_json(chat(msgs, temperature=0.0, max_tokens=4096), "[", "]")
        status = len(tcs) if is_valid(tcs) else "PARSE-FAIL"
        results[r["id"]] = {
            "req_id": r["id"], "requirement": r["text"],
            "model": MODEL, "temperature": 0.2,
            "run_id": RUN_ID, "timestamp": datetime.now().isoformat(),
            "retrieved_examples": [BANK[i]["requirement"][:60] for i in top],
            "test_cases": tcs if is_valid(tcs) else {"raw": "see-retry"},
        }
        print(f"[OK] {r['id']}: {status} test cases")
        time.sleep(2)

    with open(OUT, "w") as f:
        for r in reqs:
            if r["id"] in results:
                f.write(json.dumps(results[r["id"]], ensure_ascii=False) + "\n")
    print("Saved to", OUT)

if __name__ == "__main__":
    main()
