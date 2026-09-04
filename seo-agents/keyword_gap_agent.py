"""
Keyword-gap agent ("striking distance" finder).

Pulls Search Analytics data for a site, finds queries where the site ranks in
positions 8-20 (close to page 1, worth pushing) grouped by the page currently
ranking for them, and separately flags keyword cannibalization: queries where
more than one of the site's own pages is genuinely contesting the same
query. "Genuinely" means three things, in order: fold http:// and https://
copies of the same URL into one page first (see _canonical_page), require
at least MIN_CANNIBALIZATION_IMPRESSIONS combined impressions before a
split is even worth looking at, and then require that no single page
already holds DOMINANT_PAGE_SHARE or more of those impressions - a clear
winner with one stray impression elsewhere is not a contested query.

This agent only READS data - it does not write or publish anything. Its output
is a report; deciding what to do with striking-distance keywords (write new
content, fix internal links, etc.) is a later, human-reviewed step.
"""

from datetime import date, timedelta
from collections import defaultdict
from urllib.parse import urlsplit, urlunsplit

from gsc_client import GSCClient

STRIKING_DISTANCE_MIN = 8
STRIKING_DISTANCE_MAX = 20

# Below this many combined impressions across all its pages, a query is not
# meaningfully cannibalised - it is 1-2 stray impressions at position 60+
# that GSC happened to attribute to more than one URL. Flagging that as
# "worth fixing" sends people to rewrite pages for a problem that is not
# costing any real traffic. Chosen so a query needs to show up more than
# once or twice in 28 days before it counts - see the "clip soft" case
# (2 impressions, position 65) that prompted this.
MIN_CANNIBALIZATION_IMPRESSIONS = 5

# If one page already holds this share (or more) of a query's combined
# impressions, it has already won - a second page picking up one stray
# impression next to it is not "competing", it is noise sitting on top of
# a clear winner. Real cannibalization looks like a contested split (e.g.
# 60/40); it does not look like 92/8. See the "softclipper" case (12
# impressions on the homepage vs 1 on /download/) that prompted this.
DOMINANT_PAGE_SHARE = 0.85


def _canonical_page(page: str) -> str:
    """Fold the http:// and https:// copy of the same URL into one page.

    GSC sometimes keeps a stray http:// row from before a redirect fully
    propagated. Counting that as a second page "competing" for a query is a
    canonicalisation artifact, not cannibalization - e.g. softclipper.pro
    showed http://softclipper.pro/ and https://softclipper.pro/ as two
    "pages" for the query "softclipper", which is one page counted twice.
    """
    parts = urlsplit(page)
    return urlunsplit(("https", parts.netloc, parts.path, parts.query, parts.fragment))


def run(site_url: str, days: int = 28, row_limit: int = 5000):
    client = GSCClient()

    end_date = date.today() - timedelta(days=3)  # GSC data has ~2-3 day lag
    start_date = end_date - timedelta(days=days)

    rows = client.search_analytics_query(
        site_url=site_url,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        dimensions=["query", "page"],
        row_limit=row_limit,
    )

    striking_distance = []
    query_to_pages = defaultdict(set)
    query_impressions = defaultdict(int)
    query_page_impressions = defaultdict(lambda: defaultdict(int))

    for row in rows:
        query, page = row["keys"]
        position = row.get("position", 0)
        clicks = row.get("clicks", 0)
        impressions = row.get("impressions", 0)
        ctr = row.get("ctr", 0)

        canon_page = _canonical_page(page)
        query_to_pages[query].add(canon_page)
        query_impressions[query] += impressions
        query_page_impressions[query][canon_page] += impressions

        if STRIKING_DISTANCE_MIN <= position <= STRIKING_DISTANCE_MAX:
            striking_distance.append(
                {
                    "query": query,
                    "page": page,
                    "position": round(position, 1),
                    "clicks": clicks,
                    "impressions": impressions,
                    "ctr": round(ctr * 100, 2),
                }
            )

    # highest-opportunity first: most impressions, closest to page 1
    striking_distance.sort(key=lambda r: (-r["impressions"], r["position"]))

    cannibalization = []
    for query, pages in query_to_pages.items():
        total = query_impressions[query]
        if len(pages) <= 1 or total < MIN_CANNIBALIZATION_IMPRESSIONS:
            continue
        top_page_impressions = max(query_page_impressions[query].values())
        if top_page_impressions / total >= DOMINANT_PAGE_SHARE:
            continue
        cannibalization.append(
            {
                "query": query,
                "pages": sorted(pages),
                "impressions": total,
            }
        )
    # worst (most-seen) cannibalization first - that is the one actually worth fixing
    cannibalization.sort(key=lambda c: -c["impressions"])

    return {
        "site_url": site_url,
        "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "total_query_page_rows": len(rows),
        "striking_distance_keywords": striking_distance,
        "cannibalization_flags": cannibalization,
        # kept so the content agent can mine the same pull instead of
        # spending a second API call on identical data
        "raw_rows": rows,
    }


if __name__ == "__main__":
    import json
    import sys

    site = sys.argv[1] if len(sys.argv) > 1 else "sc-domain:softclipper.pro"
    result = run(site)
    print(json.dumps(result, indent=2))
