"""
Cold-start topic agent - finds what to write about BEFORE the site has traffic.

Why this exists: `content_agent.py` only proposes a topic once a real query has
already brought impressions. That is the right rule for a site with search
history and completely useless for a new one - no traffic means no evidence
means no topics, forever. This agent breaks that circle by looking outside our
own Search Console.

Three free sources, no API key, no paid subscription:

  1. **Google Autocomplete.** The public suggest endpoint returns the phrases
     Google itself completes a prefix into. Those completions are drawn from
     what people actually type, so they are demand evidence - just not
     *quantified* demand.

  2. **Question and comparison prefixes.** "how to X", "X vs", "best X",
     "X alternative" - run through the same endpoint. This is where a new site
     can realistically rank, because the head term is already owned.

  3. **Competitor blog sitemaps.** A competitor who published a post on a topic
     spent real money deciding it was worth covering. Two competitors covering
     the same thing is a stronger signal than any keyword tool's estimate.

WHAT THIS IS NOT: it is not search volume. Nobody gives volume away for free,
and this project does not have a paid keyword API - so rather than invent a
number, the score below says exactly what it is made of. A topic ranked high
here means "Google suggests this consistently and competitors have committed
pages to it", not "1,900 searches a month".

Nothing here publishes anything. It produces a ranked list a human picks from.
"""

import json
import math
import re
import time
import urllib.parse

import requests

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"

UA = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; softclipper-seo-agent/1.0; "
        "+https://softclipper.pro)"
    )
}

# Prefixes and suffixes that pull long-tail, low-competition phrasing out of
# autocomplete. A new domain will not outrank an established one on the bare
# head term; these are where it can.
QUESTION_PREFIXES = ("how to", "how do i", "what is", "why is", "can i", "best")
SUFFIXES = ("vs", "alternative", "free", "for", "without", "online", "software")

# Full a-z expansion is 26 requests per seed and adds mostly noise past the
# first few letters. These carry most of the useful completions.
LETTERS = "abcdefghijklmnopqrstuvwxyz"

# Be a polite client of a public endpoint.
REQUEST_DELAY_SECONDS = 0.25
MAX_REQUESTS = 150

# Words that carry no topical meaning when matching a phrase to a URL slug.
STOPWORDS = {
    "a", "an", "the", "to", "of", "for", "in", "on", "with", "and", "or",
    "my", "your", "is", "are", "do", "does", "how", "what", "why", "can",
    "i", "it", "you", "best", "free", "online",
}


# ----------------------------------------------------------------------
# Google Autocomplete
# ----------------------------------------------------------------------
def _parse_suggest(body: str):
    """The endpoint answers with a JSON array: [query, [suggestions], ...].

    It is not a documented API, so anything unexpected is treated as "no
    suggestions" rather than as a crash - a malformed response should cost us
    one query, not the whole run.
    """
    try:
        data = json.loads(body)
    except ValueError:
        return []
    if not isinstance(data, list) or len(data) < 2:
        return []
    suggestions = data[1]
    if not isinstance(suggestions, list):
        return []
    out = []
    for s in suggestions:
        if isinstance(s, str) and s.strip():
            out.append(s.strip().lower())
    return out


def autocomplete(query: str, session=None, hl="en", gl="us"):
    session = session or requests.Session()
    params = {"client": "firefox", "q": query, "hl": hl, "gl": gl}
    url = f"{SUGGEST_URL}?{urllib.parse.urlencode(params)}"
    resp = session.get(url, timeout=20, headers=UA)
    if resp.status_code != 200:
        return []
    return _parse_suggest(resp.text)


def build_queries(seeds):
    """Turns a handful of seeds into the prefix set worth asking about.

    Deliberately ordered: the bare seed first, then question and comparison
    shapes, then letter expansion. If MAX_REQUESTS truncates the list, what
    gets dropped is the least useful part.
    """
    queries = []
    seen = set()

    def add(q):
        q = q.strip().lower()
        if q and q not in seen:
            seen.add(q)
            queries.append(q)

    for seed in seeds:
        add(seed)
    for seed in seeds:
        for p in QUESTION_PREFIXES:
            add(f"{p} {seed}")
        for s in SUFFIXES:
            add(f"{seed} {s}")
    for seed in seeds:
        for letter in LETTERS:
            add(f"{seed} {letter}")
    return queries


def harvest(seeds, session=None, max_requests=MAX_REQUESTS, delay=REQUEST_DELAY_SECONDS):
    """Returns {phrase: {"hits": n, "best_position": p, "from": [queries]}}.

    `hits` is how many different prefixes surfaced the phrase - breadth.
    `best_position` is its best rank within a suggestion list; Google orders
    those roughly by popularity, so position 0 means more than position 9.
    """
    session = session or requests.Session()
    found = {}
    used = 0
    errors = []

    for query in build_queries(seeds)[:max_requests]:
        try:
            suggestions = autocomplete(query, session)
        except Exception as e:
            errors.append({"query": query, "error": str(e)})
            continue
        finally:
            used += 1
            if delay:
                time.sleep(delay)

        for position, phrase in enumerate(suggestions):
            entry = found.setdefault(
                phrase, {"phrase": phrase, "hits": 0, "best_position": position, "from": []}
            )
            entry["hits"] += 1
            entry["best_position"] = min(entry["best_position"], position)
            if len(entry["from"]) < 5:
                entry["from"].append(query)

    return {"phrases": found, "requests_made": used, "errors": errors}


# ----------------------------------------------------------------------
# Competitor coverage
# ----------------------------------------------------------------------
SITEMAP_PATHS = ("/sitemap.xml", "/sitemap-index.xml", "/sitemap_index.xml")

# A URL is treated as editorial (something they chose to write) rather than
# product surface. Product pages tell us nothing about topic demand.
EDITORIAL_HINTS = ("/blog/", "/guide", "/learn/", "/resources/", "/post/", "/articles/")


def _urls_from_xml(xml: str):
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)


def competitor_urls(origin: str, session=None, max_sitemaps=4):
    """Reads a competitor's sitemap (following one level of sitemap index)."""
    session = session or requests.Session()
    for path in SITEMAP_PATHS:
        url = urllib.parse.urljoin(origin, path)
        try:
            resp = session.get(url, timeout=25, headers=UA)
        except Exception:
            continue
        if resp.status_code != 200 or "<loc>" not in resp.text:
            continue

        locs = _urls_from_xml(resp.text)
        if "<sitemapindex" in resp.text:
            pages = []
            for child in locs[:max_sitemaps]:
                try:
                    r = session.get(child, timeout=25, headers=UA)
                    if r.status_code == 200:
                        pages.extend(_urls_from_xml(r.text))
                except Exception:
                    continue
            return pages
        return locs
    return []


# Path segments that describe where a page lives, not what it is about.
# Without these, every blog URL "matches" every phrase containing the word blog.
PATH_NOISE = {
    "blog", "post", "posts", "article", "articles", "guide", "guides",
    "learn", "resources", "resource", "news", "page", "index", "html",
    "www", "com", "amp",
}


def slug_words(url: str):
    path = urllib.parse.urlparse(url).path.lower()
    words = re.split(r"[^a-z0-9]+", path)
    return {
        w
        for w in words
        if w and w not in STOPWORDS and w not in PATH_NOISE and len(w) > 2
    }


def competitor_index(origins, session=None):
    """{competitor origin: [set of slug words per editorial URL]}"""
    session = session or requests.Session()
    index = {}
    for origin in origins:
        urls = competitor_urls(origin, session)
        editorial = [u for u in urls if any(h in u.lower() for h in EDITORIAL_HINTS)]
        index[origin] = [slug_words(u) for u in editorial]
    return index


def _phrase_words(phrase: str):
    words = re.split(r"[^a-z0-9]+", phrase.lower())
    return {w for w in words if w and w not in STOPWORDS and len(w) > 2}


# Overlap required as a fraction of the phrase's own length. A flat "2 words
# in common" sounded reasonable and was not: against a competitor with 1,100
# blog URLs, almost every two-word phrase finds *something*, so the competitor
# signal came back as 4-out-of-4 for nearly every row and stopped
# distinguishing anything. Requiring most of the phrase's words fixes that.
COVERAGE_RATIO = 0.6


def covered_by(phrase: str, url_word_sets, ratio=COVERAGE_RATIO, min_overlap=2):
    """A page counts as covering a phrase when one URL slug carries most of the
    phrase's meaningful words - not merely two of them."""
    pw = _phrase_words(phrase)
    if len(pw) < min_overlap:
        return False
    need = max(min_overlap, math.ceil(ratio * len(pw)))
    return any(len(pw & words) >= need for words in url_word_sets)


# ----------------------------------------------------------------------
# Clustering
# ----------------------------------------------------------------------
# "add captions to video", "add captions to video free", "add captions to
# video online", "best app to add captions to video" are one blog post, not
# four. Left unclustered the list reads as forty opportunities when it is
# really about ten - which is the same over-counting this project keeps having
# to undo, wearing a different hat.
CLUSTER_RATIO = 0.6


def _same_topic(a_words, b_words, ratio=CLUSTER_RATIO):
    if not a_words or not b_words:
        return False
    overlap = len(a_words & b_words)
    return overlap >= 2 and overlap >= ratio * min(len(a_words), len(b_words))


def cluster(topics):
    """Greedy: highest-scoring phrase becomes the head of a cluster, weaker
    phrasings of the same thing hang off it as `variants`. The head keeps the
    cluster's best score so ranking is unaffected by how many ways people
    phrase it."""
    clusters = []
    for t in sorted(topics, key=lambda x: (-x["score"], x["phrase"])):
        words = _phrase_words(t["phrase"])
        for c in clusters:
            if _same_topic(words, c["_words"]):
                c["variants"].append(t["phrase"])
                c["autocomplete_hits"] = max(c["autocomplete_hits"], t["autocomplete_hits"])
                break
        else:
            head = dict(t)
            head["variants"] = []
            head["_words"] = words
            clusters.append(head)
    for c in clusters:
        c.pop("_words", None)
    return clusters


# ----------------------------------------------------------------------
# Scoring
# ----------------------------------------------------------------------
def score(entry, competitor_hits):
    """Composite of three things we can actually observe.

    Not volume. The components are returned alongside the number so the score
    can be argued with rather than trusted.
    """
    breadth = entry["hits"] * 2
    rank = 10 - min(entry["best_position"], 10)
    competitors = competitor_hits * 3
    return breadth + rank + competitors


def rank_topics(harvested, comp_index, our_url_word_sets, limit=40,
                negative_words=()):
    """Autocomplete drifts. Seeding "turn long videos into shorts" also returns
    "how to make videos longer" - the opposite intent, from the same words.
    `negative_words` is the escape hatch for that; it is a config list rather
    than cleverness, because guessing intent from words is how you end up
    silently dropping good topics."""
    negatives = {w.lower() for w in negative_words}
    topics = []
    for phrase, entry in harvested["phrases"].items():
        if len(_phrase_words(phrase)) < 2:
            continue  # single-word head terms: not winnable, not useful
        if negatives & set(re.split(r"[^a-z0-9]+", phrase.lower())):
            continue
        comp_hits = sum(
            1 for sets in comp_index.values() if covered_by(phrase, sets)
        )
        we_cover = covered_by(phrase, our_url_word_sets)
        topics.append(
            {
                "phrase": phrase,
                "score": score(entry, comp_hits),
                "autocomplete_hits": entry["hits"],
                "best_position": entry["best_position"],
                "competitors_covering": comp_hits,
                "we_cover_it": we_cover,
                "seen_from": entry["from"],
            }
        )
    topics.sort(key=lambda t: (-t["score"], t["phrase"]))
    gaps = cluster([t for t in topics if not t["we_cover_it"]])
    return gaps[:limit], topics


# ----------------------------------------------------------------------
def run(seeds, competitors, our_urls, session=None, max_requests=MAX_REQUESTS,
        delay=REQUEST_DELAY_SECONDS, negative_words=()):
    session = session or requests.Session()
    harvested = harvest(seeds, session, max_requests=max_requests, delay=delay)
    comp_index = competitor_index(competitors, session)
    our_sets = [slug_words(u) for u in our_urls]
    gaps, everything = rank_topics(
        harvested, comp_index, our_sets, negative_words=negative_words
    )
    return {
        "seeds": seeds,
        "requests_made": harvested["requests_made"],
        "phrases_found": len(harvested["phrases"]),
        "competitors_read": {o: len(v) for o, v in comp_index.items()},
        "errors": harvested["errors"],
        "gaps": gaps,
        "phrases_clustered_into": len(gaps),
        "already_covered": len([t for t in everything if t["we_cover_it"]]),
    }


if __name__ == "__main__":
    import sys
    import config

    site = config.enabled_sites()[0]
    cs = site.get("coldstart") or {}
    out = run(cs.get("seeds", []), cs.get("competitors", []), [])
    json.dump(out, sys.stdout, indent=2)
