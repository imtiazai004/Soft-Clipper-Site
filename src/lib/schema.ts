/**
 * JSON-LD builders.
 *
 * Every one of these takes the same content the page already renders in HTML.
 * That is deliberate: structured data that disagrees with the visible page is a
 * spam signal, so the page and the schema are always generated from one source.
 */
import { SITE, PRICE, PRODUCT } from "../consts";

export type FaqItem = { q: string; a: string };
export type Crumb = { label: string; href: string };

export const faqSchema = (items: FaqItem[]) => ({
	"@context": "https://schema.org",
	"@type": "FAQPage",
	mainEntity: items.map((item) => ({
		"@type": "Question",
		name: item.q,
		acceptedAnswer: { "@type": "Answer", text: item.a },
	})),
});

export const breadcrumbSchema = (crumbs: Crumb[]) => ({
	"@context": "https://schema.org",
	"@type": "BreadcrumbList",
	itemListElement: crumbs.map((c, i) => ({
		"@type": "ListItem",
		position: i + 1,
		name: c.label,
		item: new URL(c.href, SITE.origin).href,
	})),
});

/** The product itself. Price and platform are read from consts so they cannot drift. */
export const softwareSchema = () => ({
	"@context": "https://schema.org",
	"@type": "SoftwareApplication",
	"@id": `${SITE.origin}/#software`,
	name: SITE.name,
	applicationCategory: "MultimediaApplication",
	applicationSubCategory: "Video editing",
	operatingSystem: PRODUCT.platforms,
	description: SITE.description,
	url: SITE.origin,
	publisher: { "@id": `${SITE.origin}/#organization` },
	offers: {
		"@type": "Offer",
		price: String(PRICE.amount),
		priceCurrency: PRICE.currency,
		availability: "https://schema.org/InStock",
		url: `${SITE.origin}/pricing/`,
		// A one-time licence, not a subscription — spelled out because it is the
		// single biggest reason someone chooses this over the competition.
		category: "One-time purchase",
	},
	featureList: [
		"AI detection of the most engaging moments in a long video",
		"Automatic 9:16 reframing that follows the speaker",
		"Burned-in animated captions",
		"Highlight reels stitched from several moments",
		"Batch styling across every clip at once",
	],
});

export const howToSchema = (opts: {
	name: string;
	description: string;
	steps: { name: string; text: string }[];
	totalTime?: string;
}) => ({
	"@context": "https://schema.org",
	"@type": "HowTo",
	name: opts.name,
	description: opts.description,
	totalTime: opts.totalTime,
	tool: [{ "@type": "HowToTool", name: SITE.name }],
	step: opts.steps.map((s, i) => ({
		"@type": "HowToStep",
		position: i + 1,
		name: s.name,
		text: s.text,
	})),
});

export const articleSchema = (opts: {
	title: string;
	description: string;
	path: string;
	published: string;
	updated?: string;
}) => ({
	"@context": "https://schema.org",
	"@type": "Article",
	headline: opts.title,
	description: opts.description,
	mainEntityOfPage: new URL(opts.path, SITE.origin).href,
	datePublished: opts.published,
	dateModified: opts.updated ?? opts.published,
	author: { "@id": `${SITE.origin}/#organization` },
	publisher: { "@id": `${SITE.origin}/#organization` },
});
