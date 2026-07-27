/**
 * Every fact the site repeats lives here once.
 *
 * The domain is a placeholder until the real one is bought — change `origin`
 * and canonicals, the sitemap, Open Graph tags and all JSON-LD follow. Same for
 * the price: it appears on the pricing page, in the schema markup, in the FAQ
 * answers and in the comparison tables, and a mismatch between those is the
 * kind of thing that gets a Stripe account questioned.
 */

export const SITE = {
	name: "Soft Clipper",
	// TODO: replace with the real domain once purchased (no trailing slash).
	origin: "https://softclipper.com",
	tagline: "Turn long videos into viral vertical clips",
	description:
		"Soft Clipper is a Windows desktop app that finds the best moments in a long video and cuts ready-to-post vertical clips for TikTok, Reels and Shorts — with AI captions and automatic 9:16 reframing. One-time payment, no subscription.",
	// The legal entity behind the product — Stripe, Meta ads and Google all look
	// for a real, consistent business identity across the site.
	company: "Soft Tech Solution Ltd",
	companyCountry: "United Kingdom",
	email: "info@aisofttechsolution.com",
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
} as const;

export const PRODUCT = {
	platform: "Windows 10 and 11 (64-bit)",
	licence: "1 licence = 1 PC, activated online, then works offline",
	fileSize: "~180 MB installer",
	requirements: "8 GB RAM recommended, no GPU required",
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
