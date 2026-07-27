import type { APIRoute } from "astro";

// The logo referenced by the Organization schema. Served from a route so there
// is exactly one definition of the mark, matching the favicon and the nav.
export const GET: APIRoute = () =>
	new Response(
		`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="512" y2="512" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#8b5cf6"/>
      <stop offset="50%" stop-color="#6366f1"/>
      <stop offset="100%" stop-color="#22d3ee"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="120" fill="url(#g)"/>
  <g fill="none" stroke="#fff" stroke-width="34" stroke-linecap="round" stroke-linejoin="round">
    <rect x="112" y="136" width="176" height="240" rx="40"/>
    <path d="M352 192v128"/>
    <path d="M416 160v192"/>
  </g>
</svg>
`,
		{ headers: { "Content-Type": "image/svg+xml" } },
	);
