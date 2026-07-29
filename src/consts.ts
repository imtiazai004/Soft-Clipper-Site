/**
 * Every fact the site repeats lives here once.
 *
 * `origin` is the one place the domain is written. Canonicals, the sitemap,
 * Open Graph tags and all JSON-LD follow from it. Same for the price: it appears
 * on the pricing page, in the schema markup, in the FAQ answers and in the
 * comparison tables, and a mismatch between those is the kind of thing that gets
 * a Stripe account questioned.
 */

export const SITE = {
	name: "Soft Clipper",
	// The marketing site. The app itself and the licence API live on a different
	// host — see LICENCE_SERVER in the desktop app's core/licence.py — because
	// this is static hosting and those need a server.
	origin: "https://softclipper.pro",
	tagline: "Turn long videos into viral vertical clips",
	description:
		"Soft Clipper is a Windows desktop app that finds the best moments in a long video and cuts ready-to-post vertical clips for TikTok, Reels and Shorts — with AI captions and automatic 9:16 reframing. One-time payment, no subscription.",
	// The legal entity behind the product — Stripe, Meta ads and Google all look
	// for a real, consistent business identity across the site.
	company: "Atlantic Ltd Store Limited",
	companyCountry: "United Kingdom",
	// On the same domain the customer buys from, deliberately. A licence key for
	// something bought on softclipper.pro arriving from an unrelated domain is
	// what a phishing email looks like, and a buyer who has just paid $49 is
	// exactly the person primed to think so.
	email: "info@softclipper.pro",
	// WhatsApp is the fastest channel for most buyers, so it sits on every page.
	// `phoneE164` is the dialable form; `waLink` is what wa.me expects (digits only).
	phone: "+44 7462 086661",
	phoneE164: "+447462086661",
	waLink: "https://wa.me/447462086661",
	locale: "en_GB",
	twitter: "@softclipper",
} as const;

export const PRICE = {
	amount: 49,
	currency: "USD",
	display: "$49",
	/** What a subscription competitor costs per month, for the comparison maths. */
	competitorMonthly: 29,
	/**
	 * The Stripe Payment Link. A hosted checkout page, which is what a static
	 * site needs: creating a Checkout Session requires a server, and there is no
	 * server here. Fulfilment does not depend on the browser coming back — the
	 * licence is minted by the `checkout.session.completed` webhook on the
	 * licence service, so a customer who closes the tab still gets their key.
	 *
	 * Empty until the link is created in the Stripe dashboard. While it is empty
	 * the buy button does not pretend to work: see PayButton.astro.
	 *
	 * ⚠ THIS IS THE TEST-MODE LINK. It takes no money. Stripe keeps test and
	 * live links separate, so going live means creating the product and link
	 * again with the dashboard toggled to live, and replacing this string with
	 * the buy.stripe.com/… one (no `test_`). PayButton shows a banner on the
	 * page and the build prints a warning until that happens, so it cannot be
	 * quietly forgotten.
	 */
	checkoutUrl: "https://buy.stripe.com/test_eVqbJ3fDK8po52h0DJefC00",
} as const;

export const PRODUCT = {
	platform: "Windows 10 and 11 (64-bit)",
	licence: "1 licence = 1 PC, activated online, then works offline",
	fileSize: "~120 MB installer",

	// Both are served from R2 on our own domain. The installer is what the
	// licence email links to; the ZIP stays for anyone who would rather not run
	// a setup wizard, and is the same build either way.
	//
	// The filenames must not change between releases: an email sent last month
	// has to keep working, so a new build replaces the object at the same key.
	installerUrl: "https://dl.softclipper.pro/Soft-Clipper-Setup.exe",
	installerSize: "120 MB",
	zipUrl: "https://dl.softclipper.pro/Soft-Clipper.zip",
	zipSize: "164 MB",
	requirements: "8 GB RAM recommended, no GPU required",
	ratios: "9:16 vertical, 1:1 square and 16:9",
	/** Kept vague on purpose until the web version has a date. */
	webStatus: "in development",
} as const;

/** Primary navigation — also drives the footer sitemap and breadcrumb labels. */
export const NAV = [
	{ href: "/features/", label: "Features" },
	{ href: "/use-cases/", label: "Use cases" },
	{ href: "/compare/", label: "Compare" },
	{ href: "/pricing/", label: "Pricing" },
	{ href: "/blog/", label: "Blog" },
	{ href: "/help/", label: "Help" },
] as const;
