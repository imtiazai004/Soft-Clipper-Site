# SEO agents

Unattended Search Console monitoring for this site. Runs itself on GitHub
Actions every morning; nothing has to be installed or started by hand.

## What runs

| Agent | What it looks for |
|---|---|
| `keyword_gap_agent.py` | Queries ranking 8-20 — close enough to page one to be worth a push — and any query split across more than one of our own pages (cannibalisation) |
| `indexing_health_agent.py` | Every sitemap URL's index status. Separates "Google has never crawled this" (needs a Request Indexing click) from a real blocker (noindex, robots.txt disallow) — they look identical in the raw API and mean very different things |
| `aeo_agent.py` | Published FAQ answers, scored for whether an answer engine could lift them whole: 15-75 words, leading with the answer rather than a preamble |
| `geo_agent.py` | Whether answer engines can reach and quote the site: AI crawler access in robots.txt (parsed with real group semantics), `llms.txt` health including whether its links still resolve, and whether pages open with a declared answer block. Does **not** claim to measure actual citations in ChatGPT or Perplexity — that needs paid API access, so no number is invented |
| `content_agent.py` | Queries that brought real impressions but have no page answering them. Evidence only — it proposes topics, it does not publish. Drafting is a separate, human-triggered call, because automated publishing at scale is exactly what Google's scaled-content policy exists to catch |
| `coldstart_agent.py` | What to write about **before** the site has any traffic. Mines Google Autocomplete (question and comparison prefixes, not just the head term) and competitors' blog sitemaps, then ranks the phrases no page of ours covers. Its score is **not search volume** — no free source publishes volume and this project has no paid keyword API, so the score states its own ingredients instead of inventing a number |

`run_daily.py` runs all six and writes the Markdown report plus
`reports/data.json` (today's findings) and `reports/history.json` (the few
numbers worth plotting, appended per day).

`build_dashboard.py` turns those two files into a single self-contained
`index.html` — no server, no database, no CDN, the data is embedded in the
page. That is what makes it publishable on GitHub Pages for free.

`config.py` is the only site-specific file — adding a site is an entry there.
`noindex_urls` there lists pages deliberately kept out of the index so they
stop appearing forever as a "never crawled" warning that is neither a problem
nor fixable. `coldstart.seeds` are the words a buyer would type — the cold-start
agent skips a site entirely rather than guess them, because a guessed seed
produces a confident list of the wrong topics.

`test_coldstart.py` runs offline (every network call is a fixture):

```bash
python test_coldstart.py
```

## Where the report goes

- **The dashboard** → `https://<user>.github.io/<repo>/` once GitHub Pages is
  pointed at the `seo-reports` branch (Settings → Pages → Source: Deploy from a
  branch → `seo-reports` / `/ (root)`). Score cards, one prioritised action
  list, and a trend line. Read it on a phone.
- **Actions tab** → the run → job summary. The same findings as prose.
- **`seo-reports` branch** → `reports/` — dated history, kept off `main` so a
  daily report never triggers a Cloudflare Pages rebuild.
- **Run artifacts** → the same files, downloadable.

## Secrets it needs

Set in Settings → Secrets and variables → Actions:

| Secret | What it is |
|---|---|
| `GSC_CLIENT_ID` | Google Cloud OAuth client ID (Desktop app type) |
| `GSC_CLIENT_SECRET` | That client's secret |
| `GSC_REFRESH_TOKEN` | Refresh token from the one-time browser authorization |

The refresh token is permanent. It used to expire every 7 days; that was the
OAuth app's **publishing status**, not its verification status — clicking
**Publish app** in Google Auth Platform removed the limit outright, with no
review to wait for. If you ever see `invalid_grant` in the run log, the token
was revoked and needs re-issuing.

## Running it locally

```bash
cd seo-agents
pip install -r requirements.txt
python run_daily.py
```

Locally it falls back to `../credentials/gsc_oauth.json` if the environment
variables are not set.

## What it does not do

It reads and reports. It does not publish content, change pages, or submit
anything to Google. Every button on the dashboard opens the screen where a
human does the thing — Search Console's URL inspection, or a prefilled GitHub
issue. Clicking one is the approval step. Acting on a finding is a separate, deliberate step — which
is the point: automated publishing at scale is what Google's scaled-content
policy exists to catch.
