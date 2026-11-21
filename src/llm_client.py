import os, time, requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")

def chat(messages, temperature=0.2, max_tokens=2000, retries=8):
    last_err = "unknown"
    for attempt in range(retries):
        try:
            r = requests.post(
                BASE_URL + "/chat/completions",
                headers={"Authorization": "Bearer " + API_KEY},
                json={"model": MODEL, "messages": messages,
                      "temperature": temperature, "max_tokens": max_tokens},
                timeout=60,
            )
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"].get("content") or ""
                if content.strip():
                    return content
                last_err = "empty content"
            else:
                last_err = f"HTTP {r.status_code}: {r.text[:150]}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:150]}"
        wait = min(10 * (2 ** attempt), 90)
        print(f"[retry {attempt+1}/{retries}] {last_err} -> wait {wait}s", flush=True)
        time.sleep(wait)
    raise RuntimeError(f"LLM call failed after {retries} tries: {last_err}")
