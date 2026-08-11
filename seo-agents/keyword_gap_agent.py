"""
Keyword-gap agent ("striking distance" finder).

Pulls Search Analytics data for a site, finds queries where the site ranks in
positions 8-20 (close to page 1, worth pushing) grouped by the page currently
ranking for them, and separately flags keyword cannibalization: queries where
more than one of the site's own pages is getting impressions.

This agent only READS data - it does not write or publish anything. Its output
is a report; deciding what to do with striking-distance keywords (write new
content, fix internal links, etc.) is a later, human-reviewed step.
"""

from datetime import date, timedelta
from collections import defaultdict

from gsc_client import GSCClient

STRIKING_DISTANCE_MIN = 8
STRIKING_DISTANCE_MAX = 20


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

    for row in rows:
        query, page = row["keys"]
        position = row.get("position", 0)
        clicks = row.get("clicks", 0)
        impressions = row.get("impressions", 0)
        ctr = row.get("ctr", 0)

        query_to_pages[query].add(page)

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
        if len(pages) > 1:
            cannibalization.append({"query": query, "pages": sorted(pages)})
    cannibalization.sort(key=lambda c: c["query"])

    return {
        "site_url": site_url,
        "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "total_query_page_rows": len(rows),
        "striking_distance_keywords": striking_distance,
        "cannibalization_flags": cannibalization,
    }


if __name__ == "__main__":
    import json
    import sys

    site = sys.argv[1] if len(sys.argv) > 1 else "sc-domain:softclipper.pro"
    result = run(site)
    print(json.dumps(result, indent=2))
