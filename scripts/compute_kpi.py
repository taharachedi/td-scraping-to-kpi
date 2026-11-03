import json, time
from collections import Counter

# One deliberately simple, deliberately editable KPI definition -- change
# TARGET_SKILL, or write a different KPI function entirely. Per this course's
# standing principle: a KPI is a construct you chose, not a neutral fact.
TARGET_SKILL = "python"          # default from the manual
MY_TARGET_SKILL = "docker"       # my own choice (see REFLECTIONS.md, point 6)
CLOUD_PROVIDERS = ["aws", "azure", "gcp", "google cloud"]

def load_extracted(path="data/extracted.json"):
    with open(path) as f:
        return json.load(f)["postings"]

def share_mentioning(postings, target_skill):
    matching = [
        p for p in postings
        if any(target_skill.lower() in s.lower() for s in p.get("required_skills", []))
    ]
    return len(matching)

def compute_kpi(postings, target_skill=TARGET_SKILL):
    n = len(postings)
    n_match = share_mentioning(postings, target_skill)
    # Case-insensitive counting, so "Computer Vision" and "Computer vision"
    # are counted as one skill (see REFLECTIONS.md, point 4).
    all_skills = Counter()
    display = {}
    for p in postings:
        for s in p.get("required_skills", []):
            key = s.strip().lower()
            display.setdefault(key, s.strip())
            all_skills[key] += 1
    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "kpi_label": f"% of postings mentioning '{target_skill}'",
        "kpi_value": round(n_match / n, 3) if n else 0.0,
        "n_postings_analyzed": n,
        "n_matching": n_match,
        "top_skills": [{"skill": display[s], "count": c} for s, c in all_skills.most_common(10)],
        "avg_skills_per_posting": round(sum(len(p.get("required_skills", [])) for p in postings) / n, 2) if n else 0.0,
    }

def compute_cloud_kpi(postings):
    """Second, different KPI: share of postings naming at least one cloud provider."""
    n = len(postings)
    n_cloud = sum(
        1 for p in postings
        if any(any(c in s.lower() for c in CLOUD_PROVIDERS) for s in p.get("required_skills", []))
    )
    return {
        "label": "% of postings naming at least one cloud provider (AWS, Azure, GCP)",
        "value": round(n_cloud / n, 3) if n else 0.0,
        "n_matching": n_cloud,
    }

def main():
    postings = load_extracted()
    kpi = compute_kpi(postings)
    n = len(postings)
    n_mine = share_mentioning(postings, MY_TARGET_SKILL)
    kpi["my_kpi"] = {
        "label": f"% of postings mentioning '{MY_TARGET_SKILL}'",
        "value": round(n_mine / n, 3) if n else 0.0,
        "n_matching": n_mine,
    }
    kpi["second_kpi"] = compute_cloud_kpi(postings)
    print(json.dumps(kpi, indent=2))
    with open("docs/data/kpi.json", "w") as f:
        json.dump(kpi, f, indent=2)
    print("\nWrote docs/data/kpi.json")

if __name__ == "__main__":
    main()
