import type { APIRoute } from "astro";
import { SITE } from "../consts";

// Generated rather than kept as a static file so the sitemap URL follows the
// configured domain instead of silently pointing at a placeholder after launch.
export const GET: APIRoute = () =>
	new Response(
		`User-agent: *
Allow: /

# Answer and generative engines are welcome — being quoted by them is the point.
# Two kinds, and the second kind is the one that decides whether an assistant
# can cite this site in an answer it is writing right now. Naming both is
# belt-and-braces: the catch-all above already allows them, but if that rule
# ever tightens, these should not quietly go with it.

# Training crawls
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

# Retrieval and citation
User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

Sitemap: ${SITE.origin}/sitemap-index.xml
`,
		{ headers: { "Content-Type": "text/plain; charset=utf-8" } },
	);
