"""
AEO-readiness agent (Answer Engine Optimization).

This site already has FAQPage/HowTo/Article JSON-LD schema on nearly every
content page (verified by reading the repo directly) - so this agent's job is
NOT "add schema", it's:

  1. Pull the actual FAQ schema (mainEntity Q&A pairs) from each live page's
     JSON-LD and score each answer for snippet-friendliness: is it short
     enough (~40-75 words) to be lifted whole into a Featured Snippet / AI
     Overview, and does it lead with the direct answer instead of a preamble?

  2. Cross-reference against real search demand (via Semrush keyword data,
     passed in rather than fetched here so this module has no external
     dependency beyond `requests`) to flag question-shaped queries the site
     gets impressions for but does NOT have a matching FAQ answer for -
     i.e. a genuine AEO content gap, not just a schema-presence check.

This agent only READS - it produces a report. Writing new/improved FAQ
answers is a separate, human-reviewed step (the content-writing agent).
"""

import json
import re

import requests

# crude but effective: Google tends to lift snippet-length answers, sources
# vary on the exact number but 40-75 words is the commonly cited sweet spot
IDEAL_ANSWER_WORDS_MIN = 15
IDEAL_ANSWER_WORDS_MAX = 75

# phrases that mean an answer is stalling instead of leading with the answer
PREAMBLE_STARTERS = (
    "well,", "so,", "basically,", "in general,", "it depends", "great question",
)


def _extract_faq_schema(html: str):
    """Find all <script type="application/ld+json"> blocks and return any
    FAQPage schema's question/answer pairs."""
    blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    faqs = []
    for block in blocks:
        try:
            data = json.loads(block.strip())
        except (json.JSONDecodeError, ValueError):
            continue
        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if isinstance(item, dict) and item.get("@type") == "FAQPage":
                for entity in item.get("mainEntity", []):
                    q = entity.get("name", "")
                    a = entity.get("acceptedAnswer", {}).get("text", "")
                    if q and a:
                        faqs.append({"question": q, "answer": a})
    return faqs


def _score_answer(answer: str):
    word_count = len(answer.split())
    issues = []

    if word_count < IDEAL_ANSWER_WORDS_MIN:
        issues.append(f"too short ({word_count} words) - may read as thin/unhelpful")
    elif word_count > IDEAL_ANSWER_WORDS_MAX:
        issues.append(f"too long ({word_count} words) - unlikely to be lifted whole into a snippet")

    lowered = answer.strip().lower()
    if any(lowered.startswith(p) for p in PREAMBLE_STARTERS):
        issues.append("starts with a preamble instead of the direct answer")

    return {
        "word_count": word_count,
        "snippet_ready": len(issues) == 0,
        "issues": issues,
    }


def audit_page(url: str, session: requests.Session = None):
    """Fetch one live page and audit its FAQ schema for AEO-readiness."""
    session = session or requests.Session()
    resp = session.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    faqs = _extract_faq_schema(resp.text)
    audited = []
    for faq in faqs:
        score = _score_answer(faq["answer"])
        audited.append({**faq, **score})

    return {
        "url": url,
        "faq_count": len(audited),
        "snippet_ready_count": sum(1 for f in audited if f["snippet_ready"]),
        "faqs": audited,
    }


def find_question_gaps(page_urls, question_queries, session: requests.Session = None):
    """Compare question-shaped search queries (e.g. from GSC or Semrush,
    passed in as a list of query strings) against the FAQ questions actually
    published across the given pages, and flag ones with no close match.

    This is intentionally a simple substring/keyword-overlap check, not
    semantic matching - good enough to flag "definitely not covered" cases
    for a human (or a later LLM-backed pass) to look at.
    """
    session = session or requests.Session()
    all_faq_questions = []
    for url in page_urls:
        try:
            result = audit_page(url, session)
            all_faq_questions.extend(f["question"].lower() for f in result["faqs"])
        except Exception:
            continue

    gaps = []
    for query in question_queries:
        q_lower = query.lower()
        q_words = set(re.findall(r"\w+", q_lower))
        covered = False
        for faq_q in all_faq_questions:
            faq_words = set(re.findall(r"\w+", faq_q))
            overlap = len(q_words & faq_words) / max(1, len(q_words))
            if overlap > 0.5:
                covered = True
                break
        if not covered:
            gaps.append(query)

    return gaps


if __name__ == "__main__":
    import sys

    urls = sys.argv[1:] or ["https://softclipper.pro/"]
    session = requests.Session()
    for u in urls:
        result = audit_page(u, session)
        print(json.dumps(result, indent=2))
