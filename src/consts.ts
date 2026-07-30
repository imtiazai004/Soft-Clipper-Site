import { REMOTE } from "./lib/remote";

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
	/**
	 * A UK limited company has to publish its registered number, where it is
	 * registered and its registered office. Not optional decoration: it is a
	 * Companies Act requirement, a buyer checking whether this is a real
	 * business looks for exactly this, and a payment processor verifying an
	 * account expects the site to carry it.
	 *
	 * "England and Wales" rather than "United Kingdom" — the place of
	 * registration is the jurisdiction, and the UK has three of them.
	 */
	companyNumber: "15025294",
	companyRegisteredIn: "England and Wales",
	companyAddress: ["4 Blenheim Court", "Peppercorn Close", "Peterborough", "PE1 2DU"],
	/** One line, for prose and for the footer. */
	get companyAddressLine() {
		return this.companyAddress.join(", ");
	},
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

/**
 * The values below marked "editable" are the **fallback**, not the source of
 * truth. The live ones are set on the admin dashboard and fetched when the site
 * builds — see `lib/remote.ts`. What is written here is what the site ships with
 * if the licence server cannot be reached during a build, so it is kept in step
 * with reality rather than left to rot.
 */
const DEFAULTS = {
	price: {
		amount: 39,
		listAmount: 49,
		currency: "USD",
		checkoutUrl: "https://buy.stripe.com/test_eVqbJ3fDK8po52h0DJefC00",
	},
	downloads: {
		enabled: true,
		installerUrl: "https://dl.softclipper.pro/Soft-Clipper-Setup.exe",
		installerSize: "120 MB",
		zipUrl: "https://dl.softclipper.pro/Soft-Clipper.zip",
		zipSize: "164 MB",
		offMessage: "Downloads are paused while we ship an update. Back shortly.",
	},
	affiliates: { enabled: true, ratePct: 30, holdDays: 30 },
	notice: { enabled: false, text: "", tone: "info" },
};

const price = { ...DEFAULTS.price, ...REMOTE.price };
const downloads = { ...DEFAULTS.downloads, ...REMOTE.downloads };
const affiliates = { ...DEFAULTS.affiliates, ...REMOTE.affiliates };

export const PRICE = {
	/**
	 * What a customer is actually charged — editable on the dashboard.
	 *
	 * Everything on the site derives from this: headings, FAQ answers, comparison
	 * tables, the break-even maths and the JSON-LD offer. It must agree with what
	 * the Stripe Payment Link charges, and nothing here can enforce that, because
	 * the amount belongs to the link. A site that advertises one number while the
	 * checkout charges another is the clearest possible reason for a chargeback,
	 * and Stripe sides with the buyer. The dashboard says so on every save.
	 */
	amount: price.amount,
	currency: price.currency,
	display: `$${price.amount}`,
	/**
	 * The price the site genuinely carried before the discount, shown struck
	 * through beside the current one. 0 turns the comparison off everywhere.
	 *
	 * It has to be a real former price, not a decorative one — UK price-marking
	 * rules treat a "was" figure as a claim about the past. $49 is one we can
	 * stand behind: it was the published price on softclipper.pro. If the price
	 * settles for good, set the "was" price to 0 on the dashboard rather than
	 * leaving a comparison that has stopped being true.
	 */
	listAmount: price.listAmount,
	listDisplay: `$${price.listAmount}`,
	savingDisplay: `$${price.listAmount - price.amount}`,
	percentOff: price.listAmount
		? Math.round((1 - price.amount / price.listAmount) * 100)
		: 0,
	/** What a subscription competitor costs per month, for the comparison maths. */
	competitorMonthly: 29,
	/**
	 * The Stripe Payment Link. A hosted checkout page, which is what a static
	 * site needs: creating a Checkout Session requires a server, and there is no
	 * server here. Fulfilment does not depend on the browser coming back — the
	 * licence is minted by the `checkout.session.completed` webhook on the
	 * licence service, so a customer who closes the tab still gets their key.
	 *
	 * Empty means nobody can buy, and the buy button says so rather than
	 * pretending: see PayButton.astro.
	 */
	checkoutUrl: price.checkoutUrl,
};

export const PRODUCT = {
	platform: "Windows 10 and 11 (64-bit)",
	licence: "1 licence = 1 PC, activated online, then works offline",
	fileSize: `~${downloads.installerSize} installer`,

	/**
	 * Downloads can be switched off from the dashboard — mid-release, or when a
	 * build turns out to be broken. The download page then explains itself
	 * instead of handing out a file we do not want in circulation.
	 */
	downloadsEnabled: downloads.enabled,
	downloadsOffMessage: downloads.offMessage,

	// Both are served from R2 on our own domain. The installer is what the
	// licence email links to; the ZIP stays for anyone who would rather not run
	// a setup wizard, and is the same build either way.
	//
	// The filenames must not change between releases: an email sent last month
	// has to keep working, so a new build replaces the object at the same key.
	installerUrl: downloads.installerUrl,
	installerSize: downloads.installerSize,
	zipUrl: downloads.zipUrl,
	zipSize: downloads.zipSize,
	requirements: "8 GB RAM recommended, no GPU required",
	ratios: "9:16 vertical, 1:1 square and 16:9",
	/** Kept vague on purpose until the web version has a date. */
	webStatus: "in development",
};

/** The affiliate programme, and whether it is open to new sign-ups. */
export const AFFILIATES = {
	open: affiliates.enabled,
	ratePct: affiliates.ratePct,
	holdDays: affiliates.holdDays,
	/** How long a referral is remembered. Matches ReferralTag.astro. */
	windowDays: 60,
};

/** A bar across every page. Off unless someone has turned it on. */
export const NOTICE = { ...DEFAULTS.notice, ...REMOTE.notice };

/** Primary navigation — also drives the footer sitemap and breadcrumb labels. */
export const NAV = [
	{ href: "/features/", label: "Features" },
	{ href: "/use-cases/", label: "Use cases" },
	{ href: "/compare/", label: "Compare" },
	{ href: "/pricing/", label: "Pricing" },
	{ href: "/blog/", label: "Blog" },
	{ href: "/help/", label: "Help" },
] as const;
