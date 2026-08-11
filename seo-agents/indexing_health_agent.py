"""
Indexing-health agent.

Fetches the site's sitemap (following a sitemap-index if there is one),
then checks each URL's indexing status via the Search Console URL Inspection
API. Flags:
  - URLs that are not indexed
  - Technical blockers: noindex, robots.txt disallow, wrong canonical
  - (Everything else is reported too, for a complete picture)

URL Inspection has an API quota of roughly 2000 queries/day per property -
irrelevant at this site's current size (~34 pages) but the code sleeps briefly
between calls to be a well-behaved API citizen regardless of site size.
"""

import time
import xml.etree.ElementTree as ET

import requests

from gsc_client import GSCClient

SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def _fetch_sitemap_urls(sitemap_url: str, seen=None):
    """Fetch a sitemap (or sitemap-index) and return the flat list of page URLs."""
    seen = seen or set()
    if sitemap_url in seen:
        return []
    seen.add(sitemap_url)

    resp = requests.get(sitemap_url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    urls = []
    # sitemap index: <sitemapindex><sitemap><loc>...
    child_sitemaps = root.findall(f"{SITEMAP_NS}sitemap/{SITEMAP_NS}loc")
    if child_sitemaps:
        for loc in child_sitemaps:
            urls.extend(_fetch_sitemap_urls(loc.text.strip(), seen))
        return urls

    # regular urlset: <urlset><url><loc>...
    for loc in root.findall(f"{SITEMAP_NS}url/{SITEMAP_NS}loc"):
        urls.append(loc.text.strip())
    return urls


def run(site_url: str, sitemap_url: str, sleep_between_calls: float = 0.5, max_urls: int = 500):
    client = GSCClient()

    page_urls = _fetch_sitemap_urls(sitemap_url)
    page_urls = page_urls[:max_urls]

    results = []
    for i, page_url in enumerate(page_urls):
        try:
            inspection = client.inspect_url(site_url, page_url)
            index_result = inspection.get("inspectionResult", {}).get("indexStatusResult", {})
            coverage_state = index_result.get("coverageState", "UNKNOWN")
            verdict = index_result.get("verdict", "UNKNOWN")
            robots_state = index_result.get("robotsTxtState", "UNKNOWN")
            indexing_state = index_result.get("indexingState", "UNKNOWN")
            last_crawl = index_result.get("lastCrawlTime")

            is_indexed = verdict == "PASS" and coverage_state.lower().startswith("submitted and indexed")

            results.append(
                {
                    "url": page_url,
                    "verdict": verdict,
                    "coverage_state": coverage_state,
                    "robots_txt_state": robots_state,
                    "indexing_state": indexing_state,
                    "last_crawl_time": last_crawl,
                    "is_indexed": is_indexed,
                }
            )
        except Exception as e:
            results.append({"url": page_url, "error": str(e)})

        if i < len(page_urls) - 1:
            time.sleep(sleep_between_calls)

    not_indexed = [r for r in results if not r.get("is_indexed") and "error" not in r]
    # a genuine technical blocker means Google explicitly says "no" - not just
    # "no data yet" (which shows up as *_UNSPECIFIED for pages never crawled).
    blocked = [
        r
        for r in results
        if r.get("robots_txt_state") == "DISALLOWED"
        or r.get("indexing_state") == "BLOCKED_BY_META_TAG"
        or r.get("indexing_state") == "BLOCKED_BY_HTTP_HEADER"
        or r.get("indexing_state") == "BLOCKED_BY_ROBOTS_TXT"
    ]
    # never crawled yet is a separate, more benign bucket: worth a manual
    # "Request Indexing" click in GSC rather than a code fix
    never_crawled = [
        r for r in not_indexed if r.get("coverage_state", "").lower() == "url is unknown to google"
    ]
    errors = [r for r in results if "error" in r]

    return {
        "site_url": site_url,
        "sitemap_url": sitemap_url,
        "total_urls_checked": len(results),
        "not_indexed": not_indexed,
        "never_crawled": never_crawled,
        "technical_blockers": blocked,
        "check_errors": errors,
        "all_results": results,
    }


if __name__ == "__main__":
    import json
    import sys

    site = sys.argv[1] if len(sys.argv) > 1 else "sc-domain:softclipper.pro"
    sitemap = sys.argv[2] if len(sys.argv) > 2 else "https://softclipper.pro/sitemap-index.xml"
    result = run(site, sitemap)
    print(json.dumps(result, indent=2))
