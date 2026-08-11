# SEO agents

Unattended Search Console monitoring for this site. Runs itself on GitHub
Actions every morning; nothing has to be installed or started by hand.

## What runs

| Agent | What it looks for |
|---|---|
| `keyword_gap_agent.py` | Queries ranking 8-20 — close enough to page one to be worth a push — and any query split across more than one of our own pages (cannibalisation) |
| `indexing_health_agent.py` | Every sitemap URL's index status. Separates "Google has never crawled this" (needs a Request Indexing click) from a real blocker (noindex, robots.txt disallow) — they look identical in the raw API and mean very different things |
| `aeo_agent.py` | Published FAQ answers, scored for whether an answer engine could lift them whole: 15-75 words, leading with the answer rather than a preamble |

`run_daily.py` runs all three and writes one Markdown report.
`config.py` is the only site-specific file — adding a site is an entry there.

## Where the report goes

- **Actions tab** → the run → job summary. Nothing to clone; this is the one to read.
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

**The refresh token currently expires every 7 days**, because the Google Cloud
OAuth app is still in "Testing" publishing status. Publishing and verifying the
app removes that limit and is worth doing before relying on this unattended.
Until then, an `invalid_grant` failure in the run log means the token needs
re-issuing and the secret updating.

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
anything to Google. Acting on a finding is a separate, deliberate step — which
is the point: automated publishing at scale is what Google's scaled-content
policy exists to catch.
