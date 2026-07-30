/**
 * Settings fetched from the licence server when the site builds.
 *
 * Price, the discount, the download links, whether the affiliate programme is
 * open and whether a notice bar is showing are all things the owner should be
 * able to change without a developer. They are edited on the admin dashboard,
 * saved there, and read here — once, at build time — so they end up baked into
 * static HTML like every other word on the site.
 *
 * Build time and not in the browser, deliberately. Fetching the price client-side
 * would put the stale one in the HTML that Google indexes and in the JSON-LD
 * offer, and would show a visitor a number that changes under them after the
 * page has painted. A pricing page is the last place to want either.
 *
 * **This must never break a build.** If the licence server is down, slow, or
 * returns something unexpected, the site builds with the values committed in
 * `consts.ts` and says so in the log. A missed price change is a nuisance; a
 * failed deploy — or worse, a pricing page that renders with nothing on it —
 * takes the shop down.
 */

const ENDPOINT = import.meta.env.SITE_CONFIG_URL || "https://app.softclipper.pro/api/site-config";
const TIMEOUT_MS = 6000;

export interface RemoteSettings {
	price?: {
		amount?: number;
		listAmount?: number;
		currency?: string;
		checkoutUrl?: string;
	};
	downloads?: {
		enabled?: boolean;
		installerUrl?: string;
		installerSize?: string;
		offMessage?: string;
	};
	affiliates?: { enabled?: boolean; ratePct?: number; holdDays?: number };
	notice?: { enabled?: boolean; text?: string; tone?: string };
}

async function fetchSettings(): Promise<RemoteSettings> {
	// Opting out matters for offline work and for CI: a build on a laptop with
	// no network should not sit waiting for a timeout it is going to lose.
	if (import.meta.env.SKIP_REMOTE_CONFIG) {
		console.log("  ℹ  SKIP_REMOTE_CONFIG set — building with the committed defaults.");
		return {};
	}

	try {
		const res = await fetch(ENDPOINT, { signal: AbortSignal.timeout(TIMEOUT_MS) });
		if (!res.ok) throw new Error(`HTTP ${res.status}`);
		const body = (await res.json()) as RemoteSettings;

		// A response that arrived but makes no sense is treated as no response.
		// Half-applying it would be worse than ignoring it: a page advertising a
		// price of `undefined` still deploys, and still looks live.
		if (!body || typeof body !== "object" || typeof body.price?.amount !== "number") {
			throw new Error("the response did not contain a price");
		}
		console.log(`  ℹ  Settings loaded from ${ENDPOINT} — price $${body.price.amount}.`);
		return body;
	} catch (err) {
		console.warn(
			`\n  ⚠  Could not read settings from ${ENDPOINT} (${(err as Error).message}).\n` +
				"     Building with the values committed in src/consts.ts. Anything changed\n" +
				"     on the admin dashboard since the last successful build is NOT in this one.\n",
		);
		return {};
	}
}

/**
 * Top-level await: the fetch happens once when this module is first imported and
 * every page then reads the same resolved object. Astro renders pages after
 * modules have loaded, so nothing renders against a half-loaded config.
 */
export const REMOTE: RemoteSettings = await fetchSettings();
