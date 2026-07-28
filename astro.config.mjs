// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import { SITE } from "./src/consts";

// Kept here rather than inferred, because the sitemap is generated from routes
// and cannot see what a page rendered. Any page with `noindex` belongs here.
const NOINDEX_PATHS = [
	// The Mac build is not verified yet — see the note at the top of that page.
	"/help/install-mac/",
	// Only reachable by paying. In search results it would rank for the brand and
	// then congratulate a visitor on a purchase they have not made.
	"/thank-you/",
];

// `site` is what makes canonical URLs, the sitemap and JSON-LD point at the real
// domain. It comes from src/consts.js so the domain lives in exactly one place —
// when the real domain is bought, that single line is the only edit.
export default defineConfig({
	site: SITE.origin,
	integrations: [
		sitemap({
			// Pages carrying `noindex` must not be in the sitemap either —
			// submitting a URL and then telling the crawler to ignore it is a
			// contradiction Search Console reports as an error.
			filter: (page) => !NOINDEX_PATHS.some((path) => page.includes(path)),
		}),
	],
	build: {
		// Cleaner URLs: /pricing/ instead of /pricing.html. Search engines treat the
		// two as different pages, so picking one and sticking to it matters.
		format: "directory",
	},
	compressHTML: true,
});
