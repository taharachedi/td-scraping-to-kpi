# NOTE: as allowed by the instructor, the extraction for this repo was performed
# with Claude (cloud LLM) instead of a local Ollama model, using the same prompt
# below on the first 12 postings of data/jobs_sample.csv. The resulting
# data/extracted.json stays local (gitignored). This script is kept as the
# reproducible local-LLM version of the same stage.
import csv, json, sys, time
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen3:8b"
N_POSTINGS = int(sys.argv[1]) if len(sys.argv) > 1 else 15
MAX_CHARS = 1500

PROMPT_TEMPLATE = """Extract ONLY the concrete named tools/technologies/hard skills mentioned
in this job posting text (it may be in French or English). Do not include generic soft
skills, the job title, or company name.
Return ONLY valid JSON with one key:
- required_skills: array of strings (e.g. ["Python", "Docker", "AWS"]) -- empty array if none found.

TEXT:
{text}
"""

def call_ollama(prompt, retries=3, backoff=5):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(
                OLLAMA_URL,
                proxies={"http": None, "https": None},
                # think: False -- avoids qwen3's slow internal "thinking" pass.
                json={"model": MODEL, "prompt": prompt, "format": "json", "stream": False, "think": False},
                timeout=(10, 120),
            )
            resp.raise_for_status()
            return json.loads(resp.json()["response"])
        except Exception as e:
            last_error = e
            print(f"    Ollama call attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(backoff)
    raise RuntimeError(f"Ollama unreachable after {retries} attempts") from last_error

def main():
    with open("data/jobs_sample.csv", newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r.get("description", "").strip()]
    rows = rows[:N_POSTINGS]
    print(f"Extracting skills from {len(rows)} postings...")

    postings = []
    start = time.time()
    for i, row in enumerate(rows, 1):
        text = row["description"][:MAX_CHARS]
        t0 = time.time()
        extracted = call_ollama(PROMPT_TEMPLATE.format(text=text))
        skills = extracted.get("required_skills", [])
        print(f"  [{i}/{len(rows)}] {row['title'][:50]!r} ({time.time() - t0:.1f}s): {skills}")
        postings.append({
            "title": row["title"], "company": row.get("company"),
            "required_skills": skills,
        })

    with open("data/extracted.json", "w") as f:
        json.dump({
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "postings": postings,
        }, f, indent=2, ensure_ascii=False)
    total = time.time() - start
    print(f"\nWrote data/extracted.json ({len(postings)} postings, {total:.0f}s total)")

if __name__ == "__main__":
    main()
