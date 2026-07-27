// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import { SITE } from "./src/consts";

// `site` is what makes canonical URLs, the sitemap and JSON-LD point at the real
// domain. It comes from src/consts.js so the domain lives in exactly one place —
// when the real domain is bought, that single line is the only edit.
export default defineConfig({
	site: SITE.origin,
	integrations: [sitemap()],
	build: {
		// Cleaner URLs: /pricing/ instead of /pricing.html. Search engines treat the
		// two as different pages, so picking one and sticking to it matters.
		format: "directory",
	},
	compressHTML: true,
});
