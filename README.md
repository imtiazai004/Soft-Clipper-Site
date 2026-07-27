# Soft Clipper — marketing site

The public website for the Soft Clipper desktop app: landing page, feature and
comparison pages, help centre, blog and legal pages. Static Astro build, no
client-side JavaScript, no external requests at runtime.

## Run it

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # static output in dist/
npm run preview  # serve the built output
```

## Where things live

| Path | What |
|---|---|
| `src/consts.ts` | **Domain, price, company details.** Change them here and the whole site follows. |
| `src/layouts/Base.astro` | `<head>`, canonical URL, Open Graph, Organization + WebSite schema |
| `src/layouts/Page.astro` | Standard content page: breadcrumbs, H1, intro, CTA band |
| `src/lib/schema.ts` | JSON-LD builders (FAQ, HowTo, Article, Breadcrumb, SoftwareApplication) |
| `src/data/use-cases.ts` | The four audience pages, rendered by `src/pages/use-cases/[slug].astro` |
| `src/content/blog/` | Blog posts as Markdown |
| `src/pages/robots.txt.ts`, `llms.txt.ts` | Generated so they always carry the real domain |

## Before launch

1. **Set the real domain** in `src/consts.ts` (`SITE.origin`). Canonicals, the
   sitemap, `robots.txt`, `llms.txt` and every schema block read from it.
2. **Confirm the company details** in `src/consts.ts` — `company`,
   `companyCountry`, `email`. They appear in the footer, the schema and the
   legal pages, and Stripe checks that they match your account.
3. **Add `public/og.png`** — 1200×630. Every page references `/og.png` for
   social sharing; without it links unfurl blank.
4. **Have the legal pages reviewed.** `src/pages/legal/*` are drafts written to
   match how the software actually behaves, not solicitor-approved text.
5. **Wire the checkout.** `/pricing/` has the buy button marked
   `data-checkout`; point it at Stripe Checkout once the product exists there.
6. **Verify competitor pricing** on the `/compare/` pages. Each says when it was
   last checked — keep that honest or delete the figures.

## SEO / AEO / GEO notes

- One `<h1>` per page, unique title and meta description everywhere, canonical
  on every URL, breadcrumbs with matching `BreadcrumbList` schema.
- FAQ answers are written to be quotable on their own — that is what answer
  engines lift. The `.answer` block near the top of comparison pages exists for
  the same reason.
- `/llms.txt` states the product's limits (Windows only, no scheduling, no 4K)
  as plainly as its features, so assistants that quote it do not oversell.
- Structured data is always generated from the same data the page renders. Do
  not add schema for anything not visible on the page.
