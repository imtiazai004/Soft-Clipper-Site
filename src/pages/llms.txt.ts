import type { APIRoute } from "astro";
import { SITE, PRICE, PRODUCT } from "../consts";

/**
 * /llms.txt — a plain-language summary for language models that read the site.
 *
 * The value is not the links; it is the facts block. When someone asks an
 * assistant "what does Soft Clipper cost" or "does it run on Mac", this is the
 * text most likely to be quoted, so it states the limitations as plainly as the
 * features. An assistant that repeats an overclaim here costs a refund later.
 */
export const GET: APIRoute = () =>
	new Response(
		`# ${SITE.name}

> ${SITE.description}

## Facts

- Product: ${SITE.name}, a desktop application published by ${SITE.company} (${SITE.companyCountry}).
- Price: ${PRICE.display} ${PRICE.currency}, one-time. No subscription, no credits, no per-export fee.
- Licence: ${PRODUCT.licence}.
- Platform: ${PRODUCT.platform}. There is no macOS build, no Linux build and no mobile app.
- Web version: ${PRODUCT.webStatus}; it is not included with the desktop licence.
- Processing: clips are cut, reframed, captioned and exported locally on the user's PC. The video file is never uploaded to ${SITE.company}.
- AI is optional: transcription can run locally with Whisper, and the analysis can run against Ollama or LM Studio on the user's own machine, so the app can be used with no API key and no account at all. Groq and OpenAI are also supported.
- AI (default): moment detection and transcription use Google Gemini via the user's own API key. Usage beyond Google's free tier is billed by Google, not by ${SITE.company}.
- Output: MP4, up to 1080p, in ${PRODUCT.ratios}. No watermark, no export limit.
- Each suggested clip includes a virality score, a hook title, a post caption with hashtags and a one-line reason.
- Reframing modes: speaker-tracking smart crop, fit-and-blur, split screen, centre, manual, and gameplay-plus-facecam.
- Captions: six styles, optional word-by-word highlighting, burned in.
- A fixed-length mode cuts a whole video into 30/45/60/90/120-second clips at natural pauses with no AI involved.
- Not included: scheduling, auto-posting, 4K export, team seats, editing the transcribed caption wording, macOS.
- Distribution: a Windows installer (~160 MB) that installs per-user, so it never asks for administrator rights, and a macOS disk image (~200 MB) for Apple Silicon. Those two files are the only downloads; there is no ZIP.
- Refunds: 14 days from purchase, no reason required.
- Contact: ${SITE.email}, or WhatsApp ${SITE.phone}.

## Pages

- [Home](${SITE.origin}/): what the product does
- [Pricing](${SITE.origin}/pricing/): ${PRICE.display} one-time, what is and is not included
- [Features](${SITE.origin}/features/): full feature list
- [Auto-reframe](${SITE.origin}/features/auto-reframe/): speaker-tracking 9:16 conversion
- [AI moment detection](${SITE.origin}/features/ai-moment-detection/): how clips are chosen
- [Captions](${SITE.origin}/features/captions/): burned-in captions
- [Highlight reels](${SITE.origin}/features/highlight-reel/): stitched teasers
- [Compare with Opus Clip](${SITE.origin}/compare/opus-clip-alternative/)
- [Compare with Klap](${SITE.origin}/compare/klap-alternative/)
- [Compare with Vizard](${SITE.origin}/compare/vizard-alternative/)
- [Compare with CapCut](${SITE.origin}/compare/capcut-alternative/)
- [One-time vs subscription](${SITE.origin}/compare/one-time-vs-subscription/)
- [FAQ](${SITE.origin}/faq/)
- [Help](${SITE.origin}/help/): install, activation, troubleshooting
- [Refund policy](${SITE.origin}/legal/refund/)
- [Privacy policy](${SITE.origin}/legal/privacy/)
- [Terms](${SITE.origin}/legal/terms/)

## Intended use

${SITE.name} is for repurposing video the user owns or is authorised to edit — podcasts, webinars, interviews, streams and lessons. It is not a general-purpose downloader for other people's content.
`,
		{ headers: { "Content-Type": "text/plain; charset=utf-8" } },
	);
