/**
 * Checks the main navigation against the pages that were actually built.
 *
 *     npm test
 *
 * It exists because a wrong link in the nav does not break anything on the way
 * out. The build succeeds, the page renders, the menu opens and looks right —
 * and one entry quietly leads to a 404, on every page of the site, for everyone.
 * Nothing else in the pipeline would notice: Astro does not resolve `href`
 * strings, and the only person who finds out is a visitor who wanted that page.
 *
 * It reads `dist/` rather than the source, because what matters is what shipped.
 * A check against `consts.ts` would pass for a link whose page failed to build,
 * and would have to reimplement Astro's routing — including the dynamic
 * `[slug]` routes — to say anything at all.
 */
import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

const dist = (p) => fileURLToPath(new URL("../dist" + p, import.meta.url));

if (!existsSync(dist("/index.html"))) {
	console.error(
		"\n  dist/ is missing — build the site first.\n" +
			"  `npm test` does that for you; this file cannot check what was never built.\n",
	);
	process.exit(1);
}

const home = readFileSync(dist("/index.html"), "utf8");
const nav = home.match(/<nav aria-label="Main"[^>]*>([\s\S]*?)<\/nav>/);

let fails = 0;
const check = (name, ok, detail = "") => {
	if (!ok) fails++;
	console.log(`${ok ? "ok  " : "FAIL"}  ${name}${ok || !detail ? "" : `\n        ${detail}`}`);
};

check("the main nav is in the HTML", Boolean(nav));
if (!nav) process.exit(1);

const hrefs = [...new Set([...nav[1].matchAll(/href="([^"]+)"/g)].map((m) => m[1]))];

// Every destination has to be a page that exists. Internal links only — the nav
// has never held an external one, and if it ever does this should be told about
// it rather than quietly reporting it as broken.
const internal = hrefs.filter((h) => h.startsWith("/"));
check("every nav link is internal", internal.length === hrefs.length,
	`external: ${hrefs.filter((h) => !h.startsWith("/")).join(", ")}`);

const broken = internal.filter((h) => !existsSync(dist(h.replace(/\/$/, "") + "/index.html")));
check(`all ${internal.length} nav links reach a page that was built`, broken.length === 0,
	`missing: ${broken.join(", ")}`);

// The affiliate programme only recruits anybody if it is visible while they are
// here for something else. Nobody goes looking for one they have not heard of.
check("the affiliate programme is in the nav", internal.includes("/affiliates/"));

// The menus are plain HTML, present before any script runs. A menu built by
// JavaScript is a menu a crawler never sees, and these are the pages the site
// most wants indexed.
const panels = (nav[1].match(/class="panel"/g) || []).length;
const carets = (nav[1].match(/class="caret"/g) || []).length;
check("the dropdown panels are server-rendered", panels > 0, `found ${panels}`);
check("every panel has a button to open it without hover", panels === carets,
	`${panels} panels, ${carets} buttons — a panel with no button cannot be opened by keyboard or on a touchscreen`);

// The heading of a menu is a real page too. Somebody who knows where they are
// going should not have to open a panel to get there.
const groupTargets = [...nav[1].matchAll(/aria-controls="menu-([^"]+)"/g)].map((m) => m[1]);
check("each menu heading links somewhere of its own", groupTargets.length === carets);

console.log(fails ? `\n${fails} FAILED` : "\nall passed");
process.exit(fails ? 1 : 0);
