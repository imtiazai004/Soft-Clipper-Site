/**
 * The four audiences the product is sold to. Kept as data rather than four
 * near-identical page files so a change to the shape of these pages happens
 * once — but every field below is written specifically for its audience,
 * because four pages that read the same are four pages Google merges into one.
 */
import type { FaqItem } from "../lib/schema";

export type UseCase = {
	slug: string;
	label: string;
	title: string;
	heading: string;
	description: string;
	intro: string;
	answer: string;
	pains: { title: string; text: string }[];
	workflow: { name: string; text: string }[];
	faqs: FaqItem[];
};

export const USE_CASES: UseCase[] = [
	{
		slug: "podcasters",
		label: "Podcasters",
		title: "Clip tool for podcasters",
		heading: "Every episode is twenty clips you have not posted",
		description:
			"Turn podcast episodes into vertical clips for TikTok, Reels and Shorts. Speaker-tracking reframing for two-person interviews, captions burned in, no monthly upload quota.",
		intro:
			"A weekly two-hour show is roughly a hundred hours of raw material a year. Almost none of it gets clipped, because clipping is the job nobody scheduled.",
		answer:
			"For podcasts the two things that matter are handling two speakers on screen and not paying per minute of source. Soft Clipper does split-screen and speaker-tracking framing, and puts no cap on how many hours you feed it.",
		pains: [
			{
				title: "Two people, one vertical frame",
				text: "Split mode stacks both speakers, one above the other. Smart mode follows whoever is talking and re-picks when the camera cuts. Either beats a centre crop that shows two half-faces.",
			},
			{
				title: "Long episodes cost the most on cloud tools",
				text: "Metered services charge by minute of source video, so a two-hour episode burns an allowance whether it yields two clips or twenty. Local rendering has no such meter.",
			},
			{
				title: "Guests and unreleased episodes",
				text: "Interviews often go out under embargo. Only the audio leaves your machine for transcription — the video never does.",
			},
		],
		workflow: [
			{ name: "Drop in the episode", text: "The recording is transcribed with timestamps, or existing captions are reused when the episode is already published." },
			{ name: "Ask for the themes", text: "Prompt search finds the segments about a specific topic — the guest's origin story, the disagreement, the practical advice." },
			{ name: "Cut ten at once", text: "Style the captions and framing once, apply to every clip, render the batch while you do something else." },
		],
		faqs: [
			{
				q: "Can it handle a two-hour episode?",
				a: "Yes. Long sources are transcribed once and the whole transcript is searched for moments, so length costs you time rather than money.",
			},
			{
				q: "What about video podcasts with two cameras?",
				a: "Smart reframing resets on scene changes, so when the edit cuts to the second camera the crop follows the new speaker instead of staying on an empty chair.",
			},
			{
				q: "Audio-only podcast — is there any point?",
				a: "Less. Soft Clipper is built for video sources. With audio only you would need to generate a visual layer elsewhere first.",
			},
		],
	},
	{
		slug: "youtubers",
		label: "YouTubers",
		title: "Clip tool for YouTube creators",
		heading: "Feed Shorts without filming anything new",
		description:
			"Cut existing YouTube videos into Shorts, Reels and TikToks. AI finds the moments, reframes to 9:16 with speaker tracking, burns in captions, and exports as many as you want.",
		intro:
			"The channel already contains the content. What it lacks is someone with three spare hours a week to cut it into short form.",
		answer:
			"For YouTubers the win is the back catalogue: videos that already have captions can be turned into clips in seconds, because the transcript step is free.",
		pains: [
			{
				title: "The archive is the asset",
				text: "A two-year-old video that performed well is still full of moments nobody has seen in vertical. Reuse costs nothing to produce.",
			},
			{
				title: "Shorts need volume",
				text: "The format rewards frequency more than polish. A tool with a monthly minute quota fights that directly; local rendering does not.",
			},
			{
				title: "Captions already exist",
				text: "Published videos usually have auto-captions. Soft Clipper reuses them instead of paying to transcribe the same words again.",
			},
		],
		workflow: [
			{ name: "Paste the video link", text: "Existing captions are pulled where available, which skips transcription entirely." },
			{ name: "Take the shortlist", text: "The AI proposes clips with a reason each; keep the ones that stand alone without the video around them." },
			{ name: "Export and schedule yourself", text: "Finished MP4s land in a folder, ready to upload to Shorts, Reels and TikTok." },
		],
		faqs: [
			{
				q: "Can I clip a video that is already on YouTube?",
				a: "Yes — paste the link and Soft Clipper fetches it. Only use videos you own or have the rights to; the app is for repurposing your own work.",
			},
			{
				q: "Does it write titles for the Shorts?",
				a: "It proposes a working title for each clip, which is usually the line the clip hangs on. Most people tighten it before posting.",
			},
			{
				q: "Will it upload to YouTube for me?",
				a: "No. Soft Clipper produces files; uploading and scheduling stay in your hands.",
			},
		],
	},
	{
		slug: "coaches",
		label: "Coaches & creators",
		title: "Clip tool for coaches and course creators",
		heading: "Turn webinars and lives into a month of posts",
		description:
			"Repurpose webinars, live streams and lessons into short vertical clips with captions. One-time licence, unlimited exports, and your material never leaves your computer.",
		intro:
			"A ninety-minute webinar contains a dozen complete answers. Each one is a post, and most of them are better than anything written from scratch that week.",
		answer:
			"Coaches usually have long recordings and confidential material. Local processing solves the second problem while the AI shortlist solves the first.",
		pains: [
			{
				title: "Client material should not go to a cloud",
				text: "Group calls and coaching sessions are private. The video stays on your disk; only audio is sent for transcription, and only when captions do not already exist.",
			},
			{
				title: "Teaching is full of self-contained answers",
				text: "Prompt search pulls the segment where you answered a specific objection, which is exactly the clip that converts.",
			},
			{
				title: "Consistency beats production value",
				text: "Batch styling makes twelve clips look like one series without twelve rounds of editing.",
			},
		],
		workflow: [
			{ name: "Import the recording", text: "Zoom, StreamYard and OBS files all work — it is an ordinary video file to Soft Clipper." },
			{ name: "Search for the objection", text: "“The part where I explain why the price is what it is.” Timestamps come back; you pick." },
			{ name: "Post daily from one recording", text: "One webinar comfortably produces two weeks of short-form." },
		],
		faqs: [
			{
				q: "Does my client's video get uploaded anywhere?",
				a: "No. The video file stays on your machine. Compressed audio is sent for transcription only when the source has no captions, and visual analysis — the one mode that uploads video — is opt-in.",
			},
			{
				q: "Can I add my branding?",
				a: "Yes — text overlays, stickers and caption styling, applied to a single clip or the whole batch.",
			},
			{
				q: "Is a Zoom recording good enough quality?",
				a: "Usually yes for short-form. Gallery-view recordings with several faces are the hard case; a speaker-view recording gives the tracking something clean to follow.",
			},
		],
	},
	{
		slug: "agencies",
		label: "Agencies",
		title: "Clip tool for social media agencies",
		heading: "One licence per editor, no per-seat billing",
		description:
			"Cut client long-form into vertical clips at volume. A one-time licence per workstation, no monthly minute quota, and client footage that never leaves the office.",
		intro:
			"Agencies feel metered pricing first: five clients times four hours of source a month is where cloud tools stop being cheap and start being a line item.",
		answer:
			"For an agency the arithmetic is per editor rather than per minute. One licence per workstation, unlimited output, and client confidentiality that does not depend on a third party's retention policy.",
		pains: [
			{
				title: "Volume is the whole job",
				text: "Minute quotas turn every extra client into an upgrade. Local rendering scales with the machines you already own.",
			},
			{
				title: "Client footage is confidential",
				text: "Unreleased campaigns and internal recordings stay on your hardware, which is a shorter conversation than explaining a vendor's data policy.",
			},
			{
				title: "Consistency across a roster",
				text: "Save a look per client, apply it to every clip in a batch, and the output stays on-brand without a checklist.",
			},
		],
		workflow: [
			{ name: "One licence per workstation", text: "Buy a licence for each editor. There is no per-seat subscription to renegotiate every year." },
			{ name: "Batch per client", text: "Set the caption style, framing and look once per client, then apply across the batch." },
			{ name: "Deliver files, not links", text: "Finished MP4s go straight into the client's folder — no viewer account, no expiring share link." },
		],
		faqs: [
			{
				q: "How do we buy for a team?",
				a: "One licence per computer. For more than five, email us and we will invoice once instead of putting five card payments through.",
			},
			{
				q: "Can two editors share one licence?",
				a: "No — a licence activates on one machine. You can release it from an old machine and move it to a new one, but it is not a floating seat.",
			},
			{
				q: "Is there a white-label version?",
				a: "Not currently. The output files carry no branding, but the app itself is Soft Clipper.",
			},
		],
	},
];

export const findUseCase = (slug: string) => USE_CASES.find((u) => u.slug === slug);
