# Going live

The site is static: 34 HTML pages, no server, no JavaScript bundle. It is hosted
on **Cloudflare Pages**. The app itself and the licence API are not here — they
run on the Hetzner box, because those need a server and this does not.

| Hostname | Points at | Serves |
|---|---|---|
| `softclipper.pro` | Cloudflare Pages | This site |
| `www.softclipper.pro` | Cloudflare Pages | Redirect to the apex |
| `app.softclipper.pro` | Hetzner `5.75.178.2` | The web app, the licence API, the Stripe webhook |

The domain is registered at Hostinger and stays there. Only its **nameservers**
move to Cloudflare, which costs nothing and is not a transfer. A domain
registered in the last 60 days cannot be transferred anyway — ICANN forbids it —
but nothing here needs one.

## Why Cloudflare and not Vercel

Vercel's Hobby plan is for non-commercial use only, and their own definition of
commercial includes "any method of requesting or processing payment from
visitors of the site". A $49 checkout is exactly that, so this site on Vercel
needs the Pro plan at $20 a month — $240 a year, or five sales, for hosting that
Cloudflare gives away.

Cloudflare Pages' free tier permits commercial use and does not cap bandwidth.
The things Vercel is genuinely better at — serverless functions, SSR — this site
does not use: there is no API route here and no server rendering. The licence
API lives on Hetzner.

`vercel.json` was removed when this was decided. `public/_headers` carries the
security headers in the format Cloudflare Pages reads.

## Where the domain is written

One line, in `src/consts.ts`:

```ts
origin: "https://softclipper.pro"
```

`astro.config.mjs` reads it, and canonicals, the sitemap, Open Graph tags and
every JSON-LD block follow. The desktop app's `LICENCE_SERVER` is separate and
lives in `core/licence.py` in the other repository, because it points at `app.`
rather than here.

## 1 — Push to GitHub

Cloudflare Pages deploys from a git host; this repository has no remote yet.

```powershell
cd "d:\VIBE CODING\Soft Clipper Site"
gh repo create soft-clipper-site --private --source . --remote origin --push
```

Private is deliberate. Nothing here is secret, but a public repository invites
people to read unfinished pages before they are finished.

## 2 — Move the nameservers to Cloudflare

1. https://dash.cloudflare.com/ — free account
2. **Add a site** → `softclipper.pro` → **Free** plan
3. Cloudflare scans the existing DNS and shows what it found. **Check the list
   against Hostinger before continuing.** Anything it missed has to be added by
   hand or it stops working the moment the nameservers change.
4. It gives two nameservers, like `xxx.ns.cloudflare.com`
5. Hostinger hPanel → **Domains → DNS / Nameservers → Change nameservers** →
   paste both
6. Wait. Usually minutes, sometimes hours. Cloudflare says **Active** when done.

Email for this business is `info@aisofttechsolution.com` — a different domain
entirely — so no mailbox depends on `softclipper.pro`'s DNS today. If an address
on this domain is ever set up, its `MX` records have to exist in Cloudflare
before they are needed.

## 3 — Cloudflare Pages

1. https://dash.cloudflare.com/ → **Workers & Pages → Create → Pages →
   Connect to Git**
2. Pick the repository
3. Build settings:
   - Framework preset: **Astro**
   - Build command: `npm run build`
   - Build output directory: `dist`
4. Deploy. It comes up on a `*.pages.dev` URL — **check that before touching the
   custom domain.**
5. **Custom domains** → add `softclipper.pro` and `www.softclipper.pro`.
   Because the domain is already on Cloudflare DNS, the records are created for
   you; there is nothing to copy anywhere.

The free tier allows 500 builds a month — about sixteen a day. Every push to the
default branch is one build.

## 4 — The `app` record, and the one setting that will bite

In Cloudflare DNS, add:

| Type | Name | Value | Proxy |
|---|---|---|---|
| A | `app` | `5.75.178.2` | **DNS only — grey cloud** |

**This must be grey, not orange.** Two reasons, and the first one is not a
preference:

- Cloudflare's proxy caps a request body at **100 MB** on the free plan and
  returns `413` above it. The web app takes video uploads and Caddy is
  configured for 5 GB. Proxied, every upload over 100 MB fails.
- Caddy gets its own certificate from Let's Encrypt for `app.softclipper.pro`.
  With the orange cloud on, Cloudflare terminates TLS itself and that handshake
  never reaches Caddy.

The apex and `www` are Pages, so they are handled by Cloudflare either way.

## 5 — Check it

- `https://softclipper.pro` and `https://www.softclipper.pro` both load
- `https://app.softclipper.pro` reaches the web app over HTTPS
- `https://softclipper.pro/sitemap-index.xml` lists 32 pages on the real domain
- Submit that sitemap in Google Search Console

## A note on Strict-Transport-Security

`public/_headers` sets it to two years, for the domain and every subdomain.
Browsers remember it for that long and refuse plain HTTP afterwards. That is
what you want for a site that sells something — and it is not quickly
reversible, so it should only go live once the domain is definitely staying
where it is, and once `app.` is definitely serving HTTPS.
