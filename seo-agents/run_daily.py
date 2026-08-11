"""
The daily run: every agent, one Markdown report.

Runs unattended in GitHub Actions. Writes:
  - reports/<date>.md and reports/latest.md  (committed to the seo-reports branch)
  - the same Markdown to $GITHUB_STEP_SUMMARY, so the report is readable
    straight from the Actions run page without cloning anything

Exit code is 0 even when the agents find problems - findings are the normal
output, not a failure. It only exits non-zero if an agent could not run at
all, because that is the case that needs someone to look at it.
"""

import datetime
import os
import sys
import traceback

import config
import keyword_gap_agent
import indexing_health_agent
import aeo_agent


def _fmt_keyword_section(kw):
    lines = []
    sd = kw["striking_distance_keywords"]
    lines.append(f"### Striking-distance keywords (positions 8-20)\n")
    lines.append(
        f"_Window {kw['date_range']['start']} to {kw['date_range']['end']}, "
        f"{kw['total_query_page_rows']} query/page rows in total._\n"
    )
    if not sd:
        lines.append("Nothing in range this run.\n")
    else:
        lines.append("| Position | Impressions | Clicks | Query | Page |")
        lines.append("|---:|---:|---:|---|---|")
        for row in sd[:25]:
            lines.append(
                f"| {row['position']} | {row['impressions']} | {row['clicks']} | "
                f"{row['query']} | {row['page']} |"
            )
        if len(sd) > 25:
            lines.append(f"\n_...and {len(sd) - 25} more._\n")

    cannibal = kw["cannibalization_flags"]
    lines.append(f"\n### Keyword cannibalisation\n")
    if not cannibal:
        lines.append("No queries are being split across more than one page.\n")
    else:
        for c in cannibal[:15]:
            pages = "".join(f"\n  - {p}" for p in c["pages"])
            lines.append(f"- **{c['query']}** is targeted by {len(c['pages'])} pages:{pages}")
        lines.append("")
    return "\n".join(lines)


def _fmt_indexing_section(idx):
    lines = [f"### Indexing health\n"]
    lines.append(f"{idx['total_urls_checked']} URLs checked from the sitemap.\n")

    never = idx.get("never_crawled", [])
    lines.append(f"**Never crawled by Google yet: {len(never)}**")
    if never:
        lines.append("_These need a \"Request indexing\" click in Search Console._\n")
        for r in never:
            lines.append(f"- {r['url']}")
    else:
        lines.append("_None - every sitemap URL is known to Google._")
    lines.append("")

    other = [r for r in idx["not_indexed"] if r not in never]
    if other:
        lines.append(f"**Crawled but not indexed: {len(other)}** (worth investigating)\n")
        for r in other:
            lines.append(f"- {r['url']} — {r.get('coverage_state')}")
        lines.append("")

    blockers = idx["technical_blockers"]
    lines.append(f"**Technical blockers (noindex / robots.txt disallow): {len(blockers)}**")
    if blockers:
        for r in blockers:
            lines.append(
                f"- {r['url']} — robots: {r.get('robots_txt_state')}, "
                f"indexing: {r.get('indexing_state')}"
            )
    else:
        lines.append("_None._")
    lines.append("")

    if idx["check_errors"]:
        lines.append(f"**Errors while checking: {len(idx['check_errors'])}**\n")
        for r in idx["check_errors"]:
            lines.append(f"- {r['url']}: {r['error']}")
        lines.append("")
    return "\n".join(lines)


def _fmt_aeo_section(results):
    lines = ["### Answer-engine readiness (FAQ snippets)\n"]
    total_faqs = sum(r["faq_count"] for r in results)
    total_ready = sum(r["snippet_ready_count"] for r in results)
    lines.append(
        f"{total_ready} of {total_faqs} published FAQ answers are snippet-ready "
        f"across {len(results)} pages checked.\n"
    )
    problems = []
    for r in results:
        for faq in r["faqs"]:
            if not faq["snippet_ready"]:
                problems.append((r["url"], faq))
    if not problems:
        lines.append("Every answer checked is in good shape.\n")
    else:
        lines.append("Answers worth rewriting:\n")
        for url, faq in problems[:20]:
            issues = "; ".join(faq["issues"])
            lines.append(f"- **{faq['question']}** ({url}) — {issues}")
        lines.append("")
    return "\n".join(lines)


def run_site(site):
    """Runs every agent for one site. Each agent is isolated: one blowing up
    does not take the rest of the report down with it."""
    parts = [f"## {site['name']}\n"]
    failures = []

    try:
        kw = keyword_gap_agent.run(site["gsc_property"])
        parts.append(_fmt_keyword_section(kw))
    except Exception:
        failures.append(("keyword-gap", traceback.format_exc()))
        parts.append("### Striking-distance keywords\n\n_Agent failed - see log._\n")

    try:
        idx = indexing_health_agent.run(site["gsc_property"], site["sitemap"])
        parts.append(_fmt_indexing_section(idx))
        # reuse the crawled URL list so the AEO pass checks real pages
        page_urls = [r["url"] for r in idx["all_results"] if "error" not in r]
    except Exception:
        failures.append(("indexing-health", traceback.format_exc()))
        parts.append("### Indexing health\n\n_Agent failed - see log._\n")
        page_urls = [site["origin"]]

    try:
        aeo_results = []
        for url in page_urls:
            try:
                result = aeo_agent.audit_page(url)
                if result["faq_count"]:
                    aeo_results.append(result)
            except Exception:
                continue
        parts.append(_fmt_aeo_section(aeo_results))
    except Exception:
        failures.append(("aeo", traceback.format_exc()))
        parts.append("### Answer-engine readiness\n\n_Agent failed - see log._\n")

    return "\n".join(parts), failures


def main():
    today = datetime.date.today().isoformat()
    sections = [f"# SEO report — {today}\n"]
    all_failures = []

    sites = config.enabled_sites()
    if not sites:
        print("No sites enabled in config.py", file=sys.stderr)
        return 1

    for site in sites:
        body, failures = run_site(site)
        sections.append(body)
        all_failures.extend((site["name"], name, tb) for name, tb in failures)

    report = "\n".join(sections)

    os.makedirs("reports", exist_ok=True)
    for path in (f"reports/{today}.md", "reports/latest.md"):
        with open(path, "w", encoding="utf-8") as f:
            f.write(report)

    # make it readable straight from the Actions run page
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(report)

    print(report)

    if all_failures:
        print("\n\n=== AGENT FAILURES ===", file=sys.stderr)
        for site_name, agent_name, tb in all_failures:
            print(f"\n--- {site_name} / {agent_name} ---\n{tb}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
