"""
Builds the dashboard: reports/data.json + reports/history.json -> index.html

One self-contained HTML file. No build step, no server, no CDN, no database -
the data is embedded straight into the page as JSON. That is the whole point:
it can be published on GitHub Pages for free and opened on a phone, and there
is nothing to keep running and nothing to pay for.

What it deliberately is NOT: a control panel that changes the site. Every
"action" here opens the place where a human does the thing (Search Console,
a prefilled GitHub issue). Nothing is submitted to Google and nothing is
published automatically - that boundary is the same one the agents keep, and
it is what keeps this on the right side of Google's scaled-content policy.
"""

import datetime
import html
import json
import os
import urllib.parse

REPO = os.environ.get("GITHUB_REPOSITORY", "imtiazai004/Soft-Clipper-Site")

SEV_ORDER = {"critical": 0, "warning": 1, "idea": 2}


# ----------------------------------------------------------------------
# deep links - each action opens the exact screen where a human does it
# ----------------------------------------------------------------------
def gsc_inspect_url(gsc_property: str, page_url: str) -> str:
    """Search Console URL Inspection, opened straight on one URL. From there
    'Request indexing' is a single click."""
    return (
        "https://search.google.com/search-console/inspect?resource_id="
        + urllib.parse.quote(gsc_property, safe="")
        + "&id="
        + urllib.parse.quote(page_url, safe="")
    )


def issue_url(title: str, body: str, labels: str = "seo") -> str:
    """A prefilled 'new issue' form. Clicking it is the approve step: an issue
    exists only because a human decided the finding was worth acting on."""
    q = urllib.parse.urlencode({"title": title, "body": body, "labels": labels})
    return f"https://github.com/{REPO}/issues/new?{q}"


# ----------------------------------------------------------------------
# findings -> one prioritised action list
# ----------------------------------------------------------------------
def build_actions(site: dict):
    """Turns the agents' findings into a single queue sorted by how much it
    matters. Everything the report says in prose ends up here as one row with
    one button, because a list you can work top-to-bottom is the thing a
    report is not."""
    name = site["name"]
    prop = site.get("gsc_property", "")
    actions = []

    def add(sev, pillar, title, detail, label=None, url=None):
        actions.append(
            {
                "sev": sev,
                "pillar": pillar,
                "title": title,
                "detail": detail,
                "label": label,
                "url": url,
            }
        )

    idx = site.get("indexing") or {}
    for b in idx.get("technical_blockers", []):
        add(
            "critical",
            "SEO",
            f"Blocked from indexing: {short(b['url'])}",
            f"robots: {b.get('robots')} · indexing: {b.get('indexing')}. "
            "Google is being told not to index this page. If that is deliberate, "
            "ignore it; if not, it is costing the page every impression it would "
            "otherwise get.",
            "Inspect in Search Console",
            gsc_inspect_url(prop, b["url"]),
        )

    for url in idx.get("never_crawled", []):
        add(
            "warning",
            "SEO",
            f"Never crawled: {short(url)}",
            "Google has not fetched this URL even once, so it cannot rank for "
            "anything. One 'Request indexing' click starts the crawl.",
            "Request indexing",
            gsc_inspect_url(prop, url),
        )

    for r in idx.get("crawled_not_indexed", []):
        add(
            "warning",
            "SEO",
            f"Crawled but not indexed: {short(r['url'])}",
            f"Google's reason: {r.get('reason')}. Crawled and then rejected is a "
            "content or duplication signal, not a technical one.",
            "Inspect in Search Console",
            gsc_inspect_url(prop, r["url"]),
        )

    kw = site.get("keywords") or {}
    for c in kw.get("cannibalization", []):
        pages = "\n".join(f"- {p}" for p in c["pages"])
        add(
            "warning",
            "SEO",
            f"Two pages competing for “{c['query']}”",
            f"{len(c['pages'])} of our own pages are shown for this query, so the "
            "ranking signals are split between them instead of stacking on one:\n"
            + pages,
            "Open an issue to pick one page",
            issue_url(
                f"[SEO] Cannibalisation: {c['query']}",
                f"`{name}` shows {len(c['pages'])} pages for the query "
                f"**{c['query']}**:\n\n{pages}\n\nDecide which single page should "
                "own this query, and point the others at it (internal link, or "
                "canonical if they are near-duplicates).",
            ),
        )

    geo = site.get("geo") or {}
    # Only a blocked RETRIEVAL crawler is a finding. Training crawlers
    # (GPTBot, CCBot, Bytespider...) are blocked on purpose here - surfacing
    # those as "critical" is noise, and it is exactly the over-flagging this
    # project keeps having to undo.
    for a in _blocked_retrieval(geo):
        add(
            "critical",
            "GEO",
            f"robots.txt blocks {a['agent']}",
            f"{a.get('what') or 'A retrieval crawler.'} This is what lets an "
            "assistant read and quote the site. Blocked means absent from that "
            "engine's answers, not merely ranked lower.",
            "Open an issue",
            issue_url(
                f"[GEO] robots.txt blocks {a['agent']}",
                f"`{a['agent']}` is disallowed in {name}'s robots.txt. If that is "
                "not deliberate, allow it - retrieval crawlers are how answer "
                "engines cite the site.",
            ),
        )

    llms = geo.get("llms_txt") or {}
    if llms and not llms.get("exists"):
        add(
            "idea",
            "GEO",
            "No /llms.txt",
            "Assistants have no short plain-language summary of the site to quote, "
            "so they paraphrase whatever page they happened to land on.",
            "Open an issue",
            issue_url(
                "[GEO] Add /llms.txt",
                f"{name} has no /llms.txt. Add a short file naming what the product "
                "is, who it is for, the price, and links to the pages worth quoting.",
            ),
        )
    for d in llms.get("dead_links", []) or []:
        add(
            "warning",
            "GEO",
            f"Dead link in llms.txt: {short(d['url'])}",
            f"Returns {d.get('status')}. llms.txt is pointing assistants at nothing.",
            "Open an issue",
            issue_url(
                "[GEO] Dead link in llms.txt",
                f"`{d['url']}` in {name}/llms.txt returns {d.get('status')}. "
                "Update or remove the link.",
            ),
        )

    for a in geo.get("retrieval_not_named", []):
        add(
            "idea",
            "GEO",
            f"{a} is allowed only by the catch-all rule",
            "It can reach the site today. Naming it in robots.txt makes the intent "
            "explicit and survives a future blanket Disallow.",
            None,
            None,
        )

    cit = geo.get("citability") or {}
    for p in cit.get("needs_work", []):
        add(
            "warning",
            "GEO",
            f"Answer block needs work: {short(p['url'])}",
            "; ".join(p["issues"]),
            "Open an issue",
            issue_url(
                f"[GEO] Answer block: {p['url']}",
                f"{p['url']}\n\n" + "\n".join(f"- {i}" for i in p["issues"]),
            ),
        )

    opps = cit.get("opportunities", [])
    if opps:
        add(
            "idea",
            "GEO",
            f"{len(opps)} pages open with an intro, not a declared answer",
            "Not a fault. But a page that answers its question in the first "
            "paragraph is the one an engine lifts. Worth doing on the pages that "
            "answer a real question:\n"
            + "\n".join(f"- {u}" for u in opps[:12])
            + (f"\n…and {len(opps) - 12} more" if len(opps) > 12 else ""),
            "Open an issue",
            issue_url(
                "[GEO] Add answer blocks to high-value pages",
                "\n".join(f"- [ ] {u}" for u in opps),
            ),
        )

    aeo = site.get("aeo") or {}
    for p in aeo.get("problems", []):
        add(
            "warning",
            "AEO",
            f"FAQ answer not snippet-ready: {p['question']}",
            f"{p['url']} — " + "; ".join(p["issues"]),
            "Open an issue",
            issue_url(
                f"[AEO] Rewrite answer: {p['question'][:60]}",
                f"{p['url']}\n\n**{p['question']}**\n\n"
                + "\n".join(f"- {i}" for i in p["issues"]),
            ),
        )

    content = site.get("content") or {}
    for t in content.get("topics", []):
        add(
            "idea",
            "Content",
            f"Nothing answers “{t['query']}”",
            f"{t['impressions']} impressions, best position {t['best_position']}. "
            "People are searching this and landing on nothing that answers it.",
            "Open an issue to draft it",
            issue_url(
                f"[Content] {t['query']}",
                f"Query **{t['query']}** brought {t['impressions']} impressions to "
                f"{name} at best position {t['best_position']}, with no page "
                "covering it.\n\nDrafting is a deliberate step - this issue is the "
                "decision to write it, not the draft.",
            ),
        )

    cold = site.get("coldstart") or {}
    for t in (cold.get("gaps") or [])[:12]:
        add(
            "idea",
            "Content",
            f"Write: “{t['phrase']}”",
            f"Google completed {t['autocomplete_hits']} different prefixes into this "
            f"phrase (best position {t['best_position']}), and "
            + (
                f"{t['competitors_covering']} competitor(s) have a page on it"
                if t["competitors_covering"]
                else "no competitor has a page on it yet"
            )
            + ". No page of ours covers it.\n\nSeen from: "
            + ", ".join(t.get("seen_from") or []),
            "Open an issue to draft it",
            issue_url(
                f"[Content] {t['phrase']}",
                f"**{t['phrase']}**\n\n"
                f"- Suggested by {t['autocomplete_hits']} autocomplete prefixes, "
                f"best position {t['best_position']}\n"
                f"- Competitors with a page on it: {t['competitors_covering']}\n"
                f"- Prefixes it came from: {', '.join(t.get('seen_from') or [])}\n\n"
                "This is autocomplete + competitor evidence, **not search volume** "
                "— no free source publishes volume and none was invented. Judge it "
                "before writing.",
            ),
        )

    for a in site.get("failed_agents", []):
        add(
            "critical",
            "System",
            f"Agent failed to run: {a}",
            "The report for this pillar is missing, not clean. Check the Actions "
            "run log - a failed agent usually means an expired token or an API quota.",
            "Open the Actions log",
            f"https://github.com/{REPO}/actions",
        )

    actions.sort(key=lambda a: SEV_ORDER.get(a["sev"], 9))
    return actions


def _crawler_entries(geo: dict):
    """Tolerates both shapes: the old plain list of names and the current list
    of dicts carrying purpose."""
    out = []
    for b in (geo or {}).get("blocked_crawlers") or []:
        out.append({"agent": b, "purpose": None, "what": None} if isinstance(b, str) else b)
    return out


def _blocked_retrieval(geo: dict):
    # purpose None = an older report that did not record it; treat as retrieval
    # so a real block is never silently swallowed
    return [b for b in _crawler_entries(geo) if b.get("purpose") in (None, "retrieval")]


def _blocked_training(geo: dict):
    return [b for b in _crawler_entries(geo) if b.get("purpose") == "training"]


def _content_sub(site: dict, kw: dict) -> str:
    """Two different things, kept apart on purpose: topics proven by our own
    Search Console data, and ideas sourced from outside it. Merging them would
    hide which ones are actually evidenced by our traffic."""
    proven = len((site.get("content") or {}).get("topics") or [])
    cold = site.get("coldstart") or {}
    ideas = len(cold.get("gaps") or [])
    bits = [
        _plural(proven, "topic") + " from our own search data",
        _plural(kw.get("total_query_page_rows") or 0, "query row"),
    ]
    if cold.get("skipped"):
        bits.append("no cold-start seeds set")
    else:
        bits.append(_plural(ideas, "cold-start idea"))
    return " · ".join(bits)


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def short(url: str, limit: int = 52) -> str:
    u = url.replace("https://", "").replace("http://", "")
    return u if len(u) <= limit else u[: limit - 1] + "…"


# ----------------------------------------------------------------------
# the four pillar scores
# ----------------------------------------------------------------------
def pillar_scores(site: dict):
    """Percentages, each with the raw numbers underneath so the number can be
    checked rather than trusted. None means 'not measured' - which is shown as
    a dash, never as 0%, because those mean opposite things."""
    idx = site.get("indexing") or {}
    aeo = site.get("aeo") or {}
    cit = (site.get("geo") or {}).get("citability") or {}
    geo = site.get("geo") or {}
    kw = site.get("keywords") or {}

    total = idx.get("total_urls_checked") or 0
    problems = (
        len(idx.get("never_crawled") or [])
        + len(idx.get("crawled_not_indexed") or [])
        + len(idx.get("technical_blockers") or [])
    )
    seo = round(100 * (total - problems) / total) if total else None

    faqs = aeo.get("total_faqs") or 0
    aeo_pct = round(100 * (aeo.get("snippet_ready") or 0) / faqs) if faqs else None

    checked = cit.get("pages_checked") or 0
    open_to_ai = not _blocked_retrieval(geo)
    geo_pct = round(100 * (cit.get("citable") or 0) / checked) if checked else None

    return [
        {
            "key": "SEO",
            "tone": "score",
            "pct": seo,
            "sub": f"{total - problems}/{total} sitemap URLs healthy"
            if total
            else "no sitemap URLs read",
        },
        {
            "key": "AEO",
            "tone": "score",
            "pct": aeo_pct,
            "sub": f"{aeo.get('snippet_ready') or 0}/{faqs} FAQ answers snippet-ready"
            if faqs
            else "no FAQ markup found",
        },
        {
            "key": "GEO",
            # coverage: pages without a declared answer block are an opportunity,
            # not a defect, so this is not scored red
            "tone": "coverage",
            "pct": geo_pct,
            "sub": (
                f"{cit.get('citable') or 0}/{checked} pages carry an answer block · "
                + (
                    "retrieval crawlers open"
                    if open_to_ai
                    else f"{len(_blocked_retrieval(geo))} retrieval crawler(s) BLOCKED"
                )
                + (
                    f" · {len(_blocked_training(geo))} training crawler(s) blocked on purpose"
                    if _blocked_training(geo)
                    else ""
                )
            )
            if checked
            else "not measured",
        },
        {
            "key": "Content",
            "tone": "coverage",
            "pct": None,
            "sub": _content_sub(site, kw),
        },
    ]


# ----------------------------------------------------------------------
def build(data_path="reports/data.json", history_path="reports/history.json",
          out_path="index.html"):
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)

    history = []
    if os.path.exists(history_path):
        try:
            with open(history_path, encoding="utf-8") as f:
                history = json.load(f)
        except (ValueError, OSError):
            history = []

    payload = {
        "generated": data.get("generated"),
        "generated_at": data.get("generated_at"),
        "repo": REPO,
        "history": history,
        "sites": [
            {
                "name": s["name"],
                "origin": s.get("origin"),
                "scores": pillar_scores(s),
                "actions": build_actions(s),
                "stats": {
                    "query_rows": (s.get("keywords") or {}).get("total_query_page_rows"),
                    "striking": (s.get("keywords") or {}).get("striking_distance") or [],
                    "date_range": (s.get("keywords") or {}).get("date_range"),
                },
            }
            for s in data.get("sites", [])
        ],
    }

    page = TEMPLATE.replace("__PAYLOAD__", json.dumps(payload))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    return out_path


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>SEO / AEO / GEO dashboard</title>
<style>
:root{
  --bg:#0e1117; --panel:#161b22; --line:#242c38; --ink:#e6edf3; --dim:#8b949e;
  --ok:#3fb950; --warn:#d29922; --bad:#f85149; --idea:#58a6ff;
}
@media (prefers-color-scheme: light){
  :root{ --bg:#f6f8fa; --panel:#fff; --line:#d8dee4; --ink:#1f2328; --dim:#636c76; }
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1000px;margin:0 auto;padding:20px 16px 64px}
header{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:baseline;
  border-bottom:1px solid var(--line);padding-bottom:14px;margin-bottom:20px}
h1{font-size:19px;margin:0;letter-spacing:-.2px}
.meta{color:var(--dim);font-size:13px;margin-left:auto}
.meta a{color:var(--idea);text-decoration:none}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:18px}
.tab{padding:6px 13px;border:1px solid var(--line);border-radius:99px;
  background:transparent;color:var(--dim);cursor:pointer;font-size:13px}
.tab[aria-selected=true]{background:var(--panel);color:var(--ink);border-color:var(--dim)}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin-bottom:24px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card h3{margin:0 0 6px;font-size:12px;letter-spacing:.10em;text-transform:uppercase;color:var(--dim)}
.pct{font-size:30px;font-weight:600;line-height:1.1;letter-spacing:-1px}
.pct.na{color:var(--dim);font-size:22px}
.card p{margin:4px 0 0;font-size:12.5px;color:var(--dim)}
.bar{height:4px;border-radius:99px;background:var(--line);margin-top:9px;overflow:hidden}
.bar i{display:block;height:100%;border-radius:99px}
h2{font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);
  margin:28px 0 12px;font-weight:600}
.filters{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}
.chip{padding:4px 11px;border:1px solid var(--line);border-radius:99px;background:transparent;
  color:var(--dim);cursor:pointer;font-size:12px}
.chip[aria-pressed=true]{border-color:var(--idea);color:var(--ink)}
.act{background:var(--panel);border:1px solid var(--line);border-left-width:3px;
  border-radius:8px;padding:12px 14px;margin-bottom:9px}
.act.critical{border-left-color:var(--bad)} .act.warning{border-left-color:var(--warn)}
.act.idea{border-left-color:var(--idea)}
.act .top{display:flex;gap:9px;align-items:baseline;flex-wrap:wrap}
.pill{font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;padding:2px 7px;
  border-radius:99px;border:1px solid var(--line);color:var(--dim);white-space:nowrap}
.act strong{font-size:14.5px;font-weight:600}
.act .detail{color:var(--dim);font-size:13px;margin-top:6px;white-space:pre-wrap;word-break:break-word}
.act a.do{display:inline-block;margin-top:10px;padding:6px 13px;border-radius:7px;
  background:var(--idea);color:#04121f;font-size:12.5px;font-weight:600;text-decoration:none}
.empty{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:26px;text-align:center;color:var(--dim)}
table{width:100%;border-collapse:collapse;font-size:13px;background:var(--panel);
  border:1px solid var(--line);border-radius:10px;overflow:hidden}
th,td{padding:8px 12px;text-align:left;border-bottom:1px solid var(--line)}
th{color:var(--dim);font-size:11px;letter-spacing:.08em;text-transform:uppercase;font-weight:600}
tr:last-child td{border-bottom:none}
td.n,th.n{text-align:right}
svg.chart{width:100%;height:130px;background:var(--panel);border:1px solid var(--line);border-radius:10px}
footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);
  color:var(--dim);font-size:12.5px}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>SEO · AEO · GEO · Content</h1>
    <div class="meta" id="meta"></div>
  </header>
  <div class="tabs" id="tabs" role="tablist"></div>
  <div class="cards" id="cards"></div>

  <h2>What to do next</h2>
  <div class="filters" id="filters"></div>
  <div id="actions"></div>

  <h2>Trend</h2>
  <div id="trend"></div>

  <h2>Close to page one</h2>
  <div id="striking"></div>

  <footer id="foot"></footer>
</div>
<script>
const D = __PAYLOAD__;
let site = 0, filter = "all";
const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const el = id => document.getElementById(id);

el("meta").innerHTML =
  "Last run " + esc(D.generated_at || D.generated || "—") +
  ' · <a href="https://github.com/' + esc(D.repo) + '/actions">run it now</a>' +
  ' · <a href="https://github.com/' + esc(D.repo) + '/issues">open issues</a>';

el("tabs").innerHTML = D.sites.map((s,i) =>
  '<button class="tab" role="tab" data-i="'+i+'">'+esc(s.name)+'</button>').join("");
el("tabs").onclick = e => { const b = e.target.closest(".tab");
  if (b) { site = +b.dataset.i; render(); } };

function colour(p, tone){
  if (tone === "coverage") return "var(--idea)";
  return p >= 90 ? "var(--ok)" : p >= 70 ? "var(--warn)" : "var(--bad)";
}

function render(){
  const s = D.sites[site];
  [...el("tabs").children].forEach((b,i) => b.setAttribute("aria-selected", i === site));

  el("cards").innerHTML = s.scores.map(c => {
    const has = c.pct !== null && c.pct !== undefined;
    return '<div class="card"><h3>'+esc(c.key)+'</h3>' +
      '<div class="pct'+(has?"":" na")+'"'+(has?' style="color:'+colour(c.pct,c.tone)+'"':"")+'>' +
      (has ? c.pct + "%" : "—") + '</div>' +
      '<p>'+esc(c.sub)+'</p>' +
      (has ? '<div class="bar"><i style="width:'+c.pct+'%;background:'+colour(c.pct,c.tone)+'"></i></div>' : "") +
      '</div>';
  }).join("");

  const counts = {critical:0, warning:0, idea:0};
  s.actions.forEach(a => counts[a.sev]++);
  const labels = {all:"All "+s.actions.length, critical:"Critical "+counts.critical,
                  warning:"Worth fixing "+counts.warning, idea:"Ideas "+counts.idea};
  el("filters").innerHTML = Object.keys(labels).map(k =>
    '<button class="chip" data-f="'+k+'" aria-pressed="'+(k===filter)+'">'+esc(labels[k])+'</button>'
  ).join("");
  el("filters").onclick = e => { const b = e.target.closest(".chip");
    if (b) { filter = b.dataset.f; render(); } };

  const shown = s.actions.filter(a => filter === "all" || a.sev === filter);
  el("actions").innerHTML = shown.length ? shown.map(a =>
    '<div class="act '+a.sev+'"><div class="top">' +
      '<span class="pill">'+esc(a.pillar)+'</span><strong>'+esc(a.title)+'</strong></div>' +
      '<div class="detail">'+esc(a.detail)+'</div>' +
      (a.url ? '<a class="do" target="_blank" rel="noopener" href="'+esc(a.url)+'">'+esc(a.label)+'</a>' : "") +
    '</div>').join("")
    : '<div class="empty">Nothing in this bucket. On a quiet day that is the correct answer, not a broken run.</div>';

  const h = (D.history || []).filter(p => p.site === s.name);
  el("trend").innerHTML = h.length < 2
    ? '<div class="empty">A trend needs at least two runs. There ' +
      (h.length === 1 ? "is 1 so far" : "are none yet") + ' — it fills in daily.</div>'
    : chart(h);

  const sd = s.stats.striking || [];
  const dr = s.stats.date_range;
  el("striking").innerHTML = sd.length
    ? '<table><tr><th class="n">Pos</th><th class="n">Impr</th><th class="n">Clicks</th>' +
      '<th>Query</th><th>Page</th></tr>' + sd.slice(0,25).map(r =>
      '<tr><td class="n">'+esc(r.position)+'</td><td class="n">'+esc(r.impressions)+'</td>' +
      '<td class="n">'+esc(r.clicks)+'</td><td>'+esc(r.query)+'</td>' +
      '<td>'+esc(r.page)+'</td></tr>').join("") + '</table>'
    : '<div class="empty">No query is sitting in positions 8–20 yet' +
      (dr ? ' (window '+esc(dr.start)+' → '+esc(dr.end)+')' : '') + '.</div>';

  el("foot").innerHTML =
    "Generated by the agents in <code>seo-agents/</code>. Read-only: nothing here " +
    "changes the site or submits anything to Google — every button opens the screen " +
    "where a human decides. Not measured: whether ChatGPT or Perplexity actually cite " +
    "the site; that needs paid API access, so no number is invented for it.";
}

/* A plain inline SVG line chart. No library, no CDN - the page has to work
   offline and forever, and a chart library is the one thing that would break
   that. */
function chart(h){
  const series = [
    {key:"impressions", label:"Impressions", c:"var(--idea)"},
    {key:"never_crawled", label:"Not crawled", c:"var(--bad)"},
  ];
  const W = 900, H = 130, pad = 26;
  const xs = h.map((_,i) => pad + i * (W - 2*pad) / Math.max(1, h.length - 1));
  const all = series.flatMap(s => h.map(p => p[s.key] || 0));
  const max = Math.max(1, ...all);
  const y = v => H - pad - (v || 0) / max * (H - 2*pad);
  const paths = series.map(s =>
    '<polyline fill="none" stroke="'+s.c+'" stroke-width="2" points="' +
    h.map((p,i) => xs[i] + "," + y(p[s.key])).join(" ") + '"/>').join("");
  const dots = series.map(s => h.map((p,i) =>
    '<circle cx="'+xs[i]+'" cy="'+y(p[s.key])+'" r="2.5" fill="'+s.c+'"><title>' +
    esc(p.date + " · " + s.label + ": " + (p[s.key] || 0)) + '</title></circle>').join("")).join("");
  const key = series.map((s,i) =>
    '<text x="'+(pad + i*130)+'" y="14" fill="'+s.c+'" font-size="11">■ '+s.label+'</text>').join("");
  return '<svg class="chart" viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="none">' +
    key + paths + dots +
    '<text x="'+pad+'" y="'+(H-8)+'" fill="var(--dim)" font-size="10">'+esc(h[0].date)+'</text>' +
    '<text x="'+(W-pad)+'" y="'+(H-8)+'" fill="var(--dim)" font-size="10" text-anchor="end">' +
    esc(h[h.length-1].date)+'</text></svg>';
}

render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    import sys

    out = build(*(sys.argv[1:] or []))
    print(f"wrote {out}")
