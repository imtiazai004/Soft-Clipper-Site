# Going live

The site is static: 34 HTML pages, no server, no JavaScript bundle. It is hosted
on Vercel. The app itself and the licence API are not here — they run on the
Hetzner box, because those need a server and this does not.

| Hostname | Points at | Serves |
|---|---|---|
| `softclipper.pro` | Vercel | This site |
| `www.softclipper.pro` | Vercel | Redirect to the apex |
| `app.softclipper.pro` | Hetzner `5.75.178.2` | The web app, the licence API, the Stripe webhook |

The domain is registered at Hostinger. Nothing needs to move: DNS stays there
and points at both hosts.

## Where the domain is written

One line, in `src/consts.ts`:

```ts
origin: "https://softclipper.pro"
```

`astro.config.mjs` reads it, and canonicals, the sitemap, Open Graph tags and
every JSON-LD block follow. The desktop app's `LICENCE_SERVER` is separate and
lives in `core/licence.py` in the other repository, because it points at
`app.` rather than here.

## Push to GitHub

Vercel deploys from a git host; this repository has no remote yet.

```powershell
gh repo create soft-clipper-site --private --source . --remote origin --push
```

Private is deliberate. Nothing here is secret, but a public repository invites
people to read the comparison pages' source and the unpublished blog drafts
before they are finished.

## Vercel

1. https://vercel.com/new — import the repository
2. Framework preset: **Astro**. Build command `npm run build`, output `dist`.
   Vercel detects all three; check them rather than assuming.
3. Deploy. It will come up on a `*.vercel.app` URL first — check that before
   touching DNS.
4. Project → **Settings → Domains** → add `softclipper.pro` and
   `www.softclipper.pro`.

Vercel then shows the exact DNS records to create. **Use the values it shows
you.** Vercel now issues per-project record values rather than one global pair,
so a value copied out of a guide may be the old shared one — it still works, but
there is no reason to use it when the dashboard is telling you the right answer.

The shape is an `A` record on the apex and a `CNAME` on `www`. `www` cannot be a
CNAME *and* the apex at the same time: a CNAME at a zone apex is not allowed,
because the apex also has to carry `NS` and `MX` records and the DNS
specification forbids a CNAME sitting alongside anything else.

## Hostinger DNS

hPanel → **Domains → DNS / Nameservers → Manage DNS records**. Add what Vercel
gave you, plus the app:

| Type | Name | Value |
|---|---|---|
| A | `@` | *(from Vercel)* |
| CNAME | `www` | *(from Vercel)* |
| A | `app` | `5.75.178.2` |

Leave the `MX` records alone. Deleting those is how a business loses its email,
and `info@aisofttechsolution.com` is the address on every page of this site and
on every licence email.

## After DNS

- `https://softclipper.pro` and `https://www.softclipper.pro` both load
- HTTPS is automatic on both hosts — Vercel provisions its own, Caddy gets one
  from Let's Encrypt for `app.` the first time it is asked for
- `https://softclipper.pro/sitemap-index.xml` lists 32 pages, all with the real
  domain
- Submit that sitemap in Google Search Console

## A note on Strict-Transport-Security

`vercel.json` sets it to two years. Browsers remember it for that long and
refuse plain HTTP for the domain and every subdomain. That is what you want for
a site that sells something — and it is not quickly reversible, so it should
only go live once the domain is definitely staying where it is.

## If Cloudflare is used instead

`public/_headers` carries the same rules in Cloudflare Pages' format. It is
inert on Vercel, and kept so the choice stays open.
