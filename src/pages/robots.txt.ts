import type { APIRoute } from "astro";
import { SITE } from "../consts";

// Generated rather than kept as a static file so the sitemap URL follows the
// configured domain instead of silently pointing at a placeholder after launch.
export const GET: APIRoute = () =>
	new Response(
		`User-agent: *
Allow: /

# Answer and generative engines are welcome — being quoted by them is the point.
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: ${SITE.origin}/sitemap-index.xml
`,
		{ headers: { "Content-Type": "text/plain; charset=utf-8" } },
	);
