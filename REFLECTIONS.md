# Reflections — TD3 Scraping to KPI

Note on method: as allowed by the instructor, the LLM extraction stage was done
with Claude instead of a local Ollama model, using the same prompt as
`scripts/extract_skills.py`, on the first 12 postings of `data/jobs_sample.csv`.

## 1. Why a silent robots.txt failure is worse than a loud one (CM3)
A crash stops the pipeline and forces someone to look. A silent "disallow
everything" looks like a normal answer, so either the scraper stops collecting
for no visible reason (a data gap nobody notices), or someone "fixes" it by
removing the check, and from then on nobody really knows whether the data was
collected within the site's rules. Provenance is about being able to say where
data came from and under which conditions. A check that can fail without saying
so means we can no longer prove those conditions, which is worse than having no
data at all.

## 2. France Travail data vs this jobspy-derived sample
France Travail data is published under an open licence: reuse and
redistribution are explicitly allowed, so publishing it is low risk. The
jobspy sample is scraped from Indeed/LinkedIn, whose Terms of Service forbid
redistribution: republishing the posting texts could breach those terms and
the companies' copyright. Public vs private matters because a public repo IS a
redistribution (anyone can download it, forks and caches keep copies). A
private repo lowers the exposure but does not remove it, which is why the rule
here is stronger: the raw CSV never goes into Git at all (`.gitignore`), only
aggregate numbers do.

## 3. Why free-text-to-skills is a good LLM task, application tracking is not (CM5)
Skill extraction is an interpretation task on messy, bilingual, unstructured
text with no single "right" parser: synonyms, phrasing and layout vary from one
posting to the next, which is exactly where an LLM adds value. Errors are also
tolerable and checkable against the source text. A record of my own actions
(which application I sent, when) is a fact I already know with certainty. An
LLM there adds no information, only the risk of inventing or changing a fact.
LLMs belong where interpretation is needed, not where a plain record is the
ground truth.

## 4. Predicted formatting inconsistency, and what I actually found
Prediction: the same skill written with different capitalisation or naming
across postings. Found in my own extraction:
- "Computer Vision" (posting 1) vs "Computer vision" (posting 2)
- "Azure" (Hilti) vs "Microsoft Azure" (desktop support)
- "C/C++" (Astemo) vs "C++" (Synopsys)
- "CI/CD" vs "GitLab CI/CD"
I fixed the first type in `compute_kpi.py` by counting skills in lower case, so
"Computer Vision" counts once with 2 postings. The naming variants (Azure,
C++, CI/CD) are not fixed by lower-casing: they would need a small synonym
table. I also found a data-quality problem upstream: postings 1 and 2 are the
same CarCutter job posted twice under two company names, which inflates
PyTorch, Generative AI and Computer Vision.

## 5. Critique pass and human-in-the-loop (CM5)
I checked the extracted skills against the original posting texts. One real
error: for the Astemo posting the extraction missed "ADAS simulation" and
"vehicle dynamics", which are explicitly listed as advantages. A second trap
was avoided: the CEA posting's lab description mentions LabVIEW, MCNP and
PENELOPE, which belong to a different laboratory and are not requirements of
the post. A model could easily list them by mistake. This is human-in-the-loop
because a person compares the model's raw output with the source and decides
what is right before it feeds a KPI. It has to happen on `extracted.json`
because `kpi.json` only holds aggregates: once skills are counted, you can no
longer see which posting a wrong skill came from, so the error cannot be traced
or fixed.

## 6. My TARGET_SKILL, and which KPI I would trust (CM2)
Before seeing the numbers I chose Docker, because containerisation is now
expected in almost every software, data and DevOps role, and is less covered
in the ENSIM curriculum than Python. Results: Python 67% (8/12), Docker 17%
(2/12). I would not use either alone to tell a curriculum committee "teach X
next": 12 postings are too few, one job is duplicated, and the sample mixes
very different roles (computer vision, DevOps, desktop support, pre-sales).
Python's 67% is the more robust signal because it appears across very
different roles. Docker's 17% mostly says this sample contains only two DevOps
postings.

## 7. What could be reconstructed from kpi.json alone (CM3/CM6)
From `kpi.json` a classmate sees one percentage, counts, and the ten most
frequent skill names. They cannot recover which postings were scraped or which
companies they came from: there is no title, company, URL or text. This was a
deliberate design choice: `compute_kpi()` only outputs aggregate fields, and
`data/jobs_sample.csv` and `data/extracted.json` are gitignored from the start.
Some residual risk remains with a very small sample: a rare skill with a count
of 1 could hint at a specific company. A minimum-count threshold (e.g. only
publish skills seen in 3 or more postings) would reduce that.

## 8. Who the dashboard is for (CM1)
The manual's version ("Scraping to KPI lab") was written for me, checking my
own work. The audience implied by Stage 4 is ENSIM's curriculum committee, so I
changed the title to "Which skills do engineering job postings ask for?" and
the description to say who it is for, how the numbers were produced (LLM
extraction) and the main limit (small sample, a signal, not a market study).

## 9. My second KPI, and which one I trust more
Second KPI: share of postings naming at least one cloud provider (AWS, Azure or
GCP): 33% (4/12). It groups several tools into one capability, so it is less
sensitive to naming variants than a single skill like Docker (17%). For a real
decision I would trust the "Python" or the "cloud" KPI more than the "Docker"
one, but only after removing duplicates and analysing a larger sample.
