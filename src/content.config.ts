import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

// Blog posts are Markdown files. The schema is strict on purpose: a post
// without a description or a date would ship with a broken meta tag and no
// Article schema, and nobody notices that until traffic does not arrive.
const blog = defineCollection({
	loader: glob({ pattern: "**/*.md", base: "./src/content/blog" }),
	schema: z.object({
		title: z.string(),
		description: z.string(),
		published: z.coerce.date(),
		updated: z.coerce.date().optional(),
		tags: z.array(z.string()).default([]),
		draft: z.boolean().default(false),
	}),
});

export const collections = { blog };
