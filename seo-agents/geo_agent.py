"""
GEO agent - visibility to answer and generative engines.

GEO is the least mature of the four pillars and the easiest place to write a
dashboard that measures nothing. So this agent only reports things that are
actually checkable from outside:

  1. AI crawler access. Parses robots.txt with real group semantics (a named
     user-agent group replaces the "*" group; it does not merge with it) and
     reports each known AI agent's effective access. The list below is the
     thing that goes stale - new crawlers appear every few months and a site
     that was open a year ago can be quietly invisible to the newest one.

  2. llms.txt health. Whether it exists, whether it still carries a facts
     block, and - the part that actually rots - whether every URL it links
     still resolves. Rename a page and llms.txt keeps confidently pointing
     assistants at a 404.

  3. Citability. Whether a page opens with a self-contained answer an engine
     can lift, and whether it carries publisher attribution. A page that
     answers in the first paragraph gets quoted; one that warms up for three
     paragraphs does not.

What this agent deliberately does NOT claim to do: tell you whether ChatGPT or
Perplexity actually cited you. That needs to be measured by querying those
engines, which needs paid API access this project does not have. Anything
here that looked like a citation count would be invented, so there isn't one.
"""

import re
import urllib.parse

import requests

# Grouped by what the crawler is FOR, because the distinction matters and is
# usually missed: sites allow the training crawlers, whose absence costs them
# nothing today, and forget the retrieval ones, which are what decide whether
# an assistant can cite the page in an answer right now.
AI_AGENTS = {
    "retrieval": {
        # these fetch pages to answer a question being asked this second,
        # or index specifically so the assistant can cite you
        "OAI-SearchBot": "OpenAI - indexes for ChatGPT citations",
        "ChatGPT-User": "OpenAI - fetches a page when a ChatGPT user asks it to",
        "Claude-SearchBot": "Anthropic - indexes for Claude citations",
        "Claude-User": "Anthropic - fetches a page for a Claude user",
        "PerplexityBot": "Perplexity - indexes for answer citations",
        "Perplexity-User": "Perplexity - fetches a page for a live answer",
        "Googlebot": "Google - also feeds AI Overviews and AI Mode",
    },
    "training": {
        "GPTBot": "OpenAI - training crawl",
        "ClaudeBot": "Anthropic - training crawl",
        "Google-Extended": "Google - training opt-out token",
        "Applebot-Extended": "Apple - training opt-out token",
        "Meta-ExternalAgent": "Meta - training crawl",
        "Amazonbot": "Amazon - Alexa and Amazon AI",
        "CCBot": "Common Crawl - open dataset used by many models",
        "Bytespider": "ByteDance - training crawl",
    },
}

# Nobody names Googlebot in robots.txt and nobody should have to - the
# catch-all covers it. It stays in the list above so that it is still caught
# if it is ever *blocked*, which would be a far bigger problem than GEO.
ALWAYS_IMPLICIT = {"Googlebot"}

UA = {"User-Agent": "Mozilla/5.0 (compatible; seo-agents/1.0)"}


# ----------------------------------------------------------------------
# robots.txt
# ----------------------------------------------------------------------
def _parse_robots(text: str):
    """Return {user_agent_lower: [(rule, path), ...]}.

    robots.txt groups consecutive User-agent lines together, and the rules
    that follow apply to all of them. A blank line or a rule line ends the
    run of agent names.
    """
    groups = {}
    current = []
    expecting_agents = False

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            expecting_agents = False
            continue
        if ":" not in line:
            continue
        field, value = line.split(":", 1)
        field = field.strip().lower()
        value = value.strip()

        if field == "user-agent":
            if not expecting_agents:
                current = []
                expecting_agents = True
            current.append(value.lower())
            groups.setdefault(value.lower(), [])
        elif field in ("allow", "disallow"):
            expecting_agents = False
            for agent in current:
                groups.setdefault(agent, []).append((field, value))
    return groups


def _effective_rules(groups, agent: str):
    """The rules that apply to `agent`: its own group if it has one, else the
    '*' group. Named groups replace the wildcard, they do not add to it."""
    a = agent.lower()
    if a in groups:
        return groups[a], "named"
    if "*" in groups:
        return groups["*"], "wildcard"
    return [], "absent"


def _is_allowed(rules, path: str = "/"):
    """Longest-match wins; Allow wins ties. Good enough for a root check,
    which is the only question that matters here."""
    best_rule, best_len = None, -1
    for rule, value in rules:
        if value == "":
            # "Disallow:" with an empty value means allow everything
            if rule == "disallow" and best_len < 0:
                best_rule, best_len = "allow", 0
            continue
        if path.startswith(value.rstrip("*")):
            length = len(value)
            if length > best_len or (length == best_len and rule == "allow"):
                best_rule, best_len = rule, length
    if best_rule is None:
        return True  # nothing matched, so nothing forbids it
    return best_rule == "allow"


def audit_ai_crawlers(origin: str, session=None):
    session = session or requests.Session()
    url = urllib.parse.urljoin(origin, "/robots.txt")
    try:
        resp = session.get(url, timeout=30, headers=UA)
        resp.raise_for_status()
    except Exception as e:
        return {"robots_url": url, "error": str(e)}

    groups = _parse_robots(resp.text)
    results = {}
    blocked, unnamed_retrieval = [], []

    for purpose, agents in AI_AGENTS.items():
        for agent, what in agents.items():
            rules, source = _effective_rules(groups, agent)
            allowed = _is_allowed(rules, "/")
            results[agent] = {
                "purpose": purpose,
                "what": what,
                "allowed": allowed,
                "matched_via": source,
            }
            if not allowed:
                blocked.append(agent)
            elif (
                purpose == "retrieval"
                and source != "named"
                and agent not in ALWAYS_IMPLICIT
            ):
                unnamed_retrieval.append(agent)

    return {
        "robots_url": url,
        "agents": results,
        "blocked": blocked,
        "retrieval_agents_not_named": unnamed_retrieval,
        "has_wildcard_group": "*" in groups,
    }


# ----------------------------------------------------------------------
# llms.txt
# ----------------------------------------------------------------------
def audit_llms_txt(origin: str, session=None, check_links: bool = True):
    session = session or requests.Session()
    url = urllib.parse.urljoin(origin, "/llms.txt")
    try:
        resp = session.get(url, timeout=30, headers=UA)
    except Exception as e:
        return {"llms_url": url, "exists": False, "error": str(e)}

    if resp.status_code != 200:
        return {"llms_url": url, "exists": False, "status": resp.status_code}

    text = resp.text
    links = re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", text)

    dead = []
    if check_links:
        for label, link in links:
            try:
                r = session.head(link, timeout=20, headers=UA, allow_redirects=True)
                if r.status_code >= 400:
                    r = session.get(link, timeout=20, headers=UA)
                if r.status_code >= 400:
                    dead.append({"label": label, "url": link, "status": r.status_code})
            except Exception as e:
                dead.append({"label": label, "url": link, "status": str(e)})

    return {
        "llms_url": url,
        "exists": True,
        "bytes": len(text),
        "has_facts_block": bool(re.search(r"^##\s*Facts", text, re.M | re.I)),
        "link_count": len(links),
        "dead_links": dead,
    }


# ----------------------------------------------------------------------
# citability
# ----------------------------------------------------------------------
LEAD_MIN_WORDS = 20
LEAD_MAX_WORDS = 90

# Pages that are deliberately kept out of search. An engine is not going to
# cite them and should not, so scoring them only manufactures warnings.
SKIP_PATH_HINTS = ("/checkout/", "/thank-you/", "/404")


def _strip_tags(html: str) -> str:
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", html)


def _find_para(html: str, cls: str):
    m = re.search(
        r'<p[^>]*class="[^"]*\b%s\b[^"]*"[^>]*>(.*?)</p>' % cls, html, re.S | re.I
    )
    if not m:
        return None
    return re.sub(r"\s+", " ", _strip_tags(m.group(1))).strip()


def audit_citability(url: str, session=None, html: str = None):
    """Can an answer engine lift a self-contained answer off this page?

    Three outcomes rather than pass/fail, because "this page has no declared
    answer" is an opportunity, not a defect - a contact page does not need
    one, a comparison page badly does:

      citable     - has an <p class="answer"> block of liftable length
      opportunity - a content page whose opening is a marketing intro rather
                    than a declared answer
      skipped     - noindex by design
    """
    session = session or requests.Session()
    if html is None:
        try:
            resp = session.get(url, timeout=30, headers=UA)
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            return {"url": url, "status": "error", "error": str(e)}

    if any(h in url for h in SKIP_PATH_HINTS) or re.search(
        r'<meta[^>]+name="robots"[^>]*content="[^"]*noindex', html, re.I
    ):
        return {"url": url, "status": "skipped", "reason": "noindex by design"}

    answer = _find_para(html, "answer")
    lead = _find_para(html, "lead")
    has_publisher = bool(re.search(r'"@type"\s*:\s*"Organization"', html)) or bool(
        re.search(r'"publisher"', html)
    )

    issues = []
    if not has_publisher:
        issues.append("no Organization/publisher attribution in structured data")

    if answer is None:
        return {
            "url": url,
            "status": "opportunity",
            "lead_words": len(lead.split()) if lead else 0,
            "issues": issues,
            "note": "opens with an intro, not a declared answer block",
        }

    words = len(answer.split())
    if words < LEAD_MIN_WORDS:
        issues.append(f"answer block very short ({words} words)")
    elif words > LEAD_MAX_WORDS:
        issues.append(f"answer block long ({words} words) - unlikely to be lifted whole")

    return {
        "url": url,
        "status": "citable" if not issues else "needs_work",
        "answer_words": words,
        "issues": issues,
    }


# ----------------------------------------------------------------------
def run(origin: str, page_urls=None, session=None):
    session = session or requests.Session()
    crawlers = audit_ai_crawlers(origin, session)
    llms = audit_llms_txt(origin, session)

    pages = [audit_citability(u, session) for u in (page_urls or [])[:60]]
    pages = [p for p in pages if p.get("status") != "error"]

    def by(status):
        return [p for p in pages if p.get("status") == status]

    return {
        "origin": origin,
        "ai_crawlers": crawlers,
        "llms_txt": llms,
        "citability": {
            "pages_checked": len(pages),
            "citable": len(by("citable")),
            "needs_work": by("needs_work"),
            "opportunities": by("opportunity"),
            "skipped": len(by("skipped")),
        },
    }


if __name__ == "__main__":
    import json
    import sys

    origin = sys.argv[1] if len(sys.argv) > 1 else "https://softclipper.pro"
    print(json.dumps(run(origin, sys.argv[2:]), indent=2))
