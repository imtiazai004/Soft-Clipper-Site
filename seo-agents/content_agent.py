"""
Content agent - proposes posts, and drafts them only when asked.

Deliberately split in two, because the two halves carry very different risk.

`find_topics()` is the half that runs every day. It does NOT invent topics.
It only reports queries the site already gets impressions for and has no page
answering - evidence that someone searched for something this site could have
answered and did not. That constraint is the whole point: a generator that
invents topics from nothing is how sites end up on the wrong side of Google's
scaled-content-abuse policy, and it produces content nobody asked for.

`draft_post()` is the half that writes, and it only runs when a human passes
it a topic. It needs GEMINI_API_KEY; without one it is dormant and the daily
run simply skips it. Its output is a draft on the reports branch, never a
commit to the site. A person still has to read it and move it.

On the site's schema: frontmatter is validated here against the same fields
`src/content.config.ts` enforces, so a bad draft fails in this agent rather
than breaking the site build.
"""

import datetime
import json
import os
import re
import urllib.parse

import requests

# a query is worth writing about only if real people reached for it
MIN_IMPRESSIONS = 10
# and only if we are not already ranking respectably for it
MIN_POSITION = 20

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)


# ----------------------------------------------------------------------
# half one: what is worth writing, on evidence
# ----------------------------------------------------------------------
def _norm(text: str):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def find_topics(gsc_rows, existing_urls, min_impressions=MIN_IMPRESSIONS):
    """gsc_rows: rows from Search Analytics with dimensions ['query','page'].

    A topic qualifies when a query has real impressions, ranks poorly, and no
    existing URL looks like it is about that query. The URL check is a slug
    word-overlap test - crude, but it errs towards *not* proposing something
    already covered, which is the safer direction to be wrong in.
    """
    slug_words = {}
    for u in existing_urls:
        path = urllib.parse.urlparse(u).path
        slug_words[u] = _norm(path.replace("/", " ").replace("-", " "))

    by_query = {}
    for row in gsc_rows:
        query = row["keys"][0]
        agg = by_query.setdefault(
            query, {"impressions": 0, "clicks": 0, "best_position": 999, "pages": set()}
        )
        agg["impressions"] += row.get("impressions", 0)
        agg["clicks"] += row.get("clicks", 0)
        agg["best_position"] = min(agg["best_position"], row.get("position", 999))
        agg["pages"].add(row["keys"][1] if len(row["keys"]) > 1 else "")

    topics = []
    for query, agg in by_query.items():
        if agg["impressions"] < min_impressions:
            continue
        if agg["best_position"] < MIN_POSITION:
            continue  # already ranking; improve the page, don't write a new one

        qwords = _norm(query)
        covered = any(
            len(qwords & words) / max(1, len(qwords)) > 0.6
            for words in slug_words.values()
        )
        if covered:
            continue

        topics.append(
            {
                "query": query,
                "impressions": agg["impressions"],
                "clicks": agg["clicks"],
                "best_position": round(agg["best_position"], 1),
                "currently_shown_pages": sorted(p for p in agg["pages"] if p),
            }
        )

    topics.sort(key=lambda t: -t["impressions"])
    return topics


# ----------------------------------------------------------------------
# half two: drafting, only on request
# ----------------------------------------------------------------------
def _slugify(title: str):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)[:70]


REQUIRED_FRONTMATTER = ("title", "description", "published")


def validate_draft(markdown: str):
    """Same rules src/content.config.ts enforces, checked before anything is
    written, so a malformed draft can never reach the site build."""
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", markdown, re.S)
    if not m:
        return ["no frontmatter block"]

    fm, body = m.group(1), m.group(2)
    fields = dict(
        (k.strip(), v.strip())
        for k, v in (
            line.split(":", 1) for line in fm.splitlines() if ":" in line
        )
    )

    for key in REQUIRED_FRONTMATTER:
        if key not in fields or not fields[key]:
            problems.append(f"missing frontmatter: {key}")

    if "published" in fields:
        raw = fields["published"].strip("\"'")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
            problems.append(f"published is not YYYY-MM-DD: {raw}")

    desc = fields.get("description", "").strip("\"'")
    if desc and not (50 <= len(desc) <= 200):
        problems.append(f"description is {len(desc)} chars; aim for 50-200")

    if len(body.split()) < 300:
        problems.append(f"body is only {len(body.split())} words - too thin to publish")

    return problems


def draft_post(topic: str, evidence: dict, site_facts: str, api_key: str = None):
    """Ask Gemini for a draft. Returns (markdown, problems).

    The prompt carries the site's own llms.txt facts block so the model writes
    from what the site actually claims rather than from what it assumes a
    video tool does. Overclaiming here costs a refund later.
    """
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None, ["GEMINI_API_KEY not set - drafting is dormant"]

    today = datetime.date.today().isoformat()
    prompt = f"""You are writing one blog post for a software product's own website.

THE SEARCH THAT PROMPTED THIS
People searched for "{topic}" and reached this site {evidence.get('impressions', 0)} times
without finding a page that answers it. Write the page that answers it.

WHAT THE PRODUCT ACTUALLY IS - do not contradict any of this, and do not
claim a capability that is not listed:
{site_facts}

HOUSE STYLE
- Plain, direct, British spelling. No marketing superlatives, no "unleash",
  no "in today's fast-paced world".
- Say what the product cannot do when it is relevant. Honesty about limits is
  the site's voice.
- Open with a paragraph that answers the question outright, before any
  throat-clearing. It should stand on its own if quoted.
- Use ## subheadings. 600-1000 words.
- Do not invent statistics, prices, or dates.

OUTPUT
Return only Markdown, starting with this exact frontmatter shape:
---
title: "..."
description: "..."
published: {today}
tags: ["...", "..."]
---

Then the body."""

    resp = requests.post(
        GEMINI_URL,
        params={"key": api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=120,
    )
    if resp.status_code != 200:
        return None, [f"Gemini API error {resp.status_code}: {resp.text[:300]}"]

    try:
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        return None, [f"unexpected Gemini response shape: {e}"]

    text = re.sub(r"^```(?:markdown)?\n|\n```$", "", text.strip())
    return text, validate_draft(text)


def draft_filename(markdown: str):
    m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', markdown, re.M)
    return f"{_slugify(m.group(1))}.md" if m else "untitled.md"


if __name__ == "__main__":
    import sys

    print(json.dumps(find_topics([], sys.argv[1:]), indent=2))
