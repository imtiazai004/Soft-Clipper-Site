---
title: "How to resize a video for TikTok, Instagram and YouTube"
description: "Which aspect ratio actually fits each platform, why a basic resize crops off the wrong things, and how to convert a video without losing the shot."
published: 2026-09-05
tags: ["guide", "short-form"]
---

Before you resize anything, the first question is which shape you actually need — get that wrong and no amount of "auto resize" fixes it afterwards.

## Which ratio goes where

| Platform | Best ratio | Notes |
|---|---|---|
| TikTok | 9:16 | Full-screen vertical; anything else gets letterboxed |
| Instagram Reels | 9:16 | Same as TikTok |
| Instagram feed post | 1:1 or 4:5 | 4:5 gets more vertical space in-feed than 1:1 |
| YouTube Shorts | 9:16 | Under 3 minutes, vertical |
| YouTube (regular) | 16:9 | The original widescreen standard |
| LinkedIn / X feed | 1:1 | Square holds up consistently across both |

Posting the same clip to TikTok, Reels and Shorts needs only one 9:16 export. Feed posts and regular YouTube need a separate export — there's no single ratio that covers everywhere.

## Resizing and reframing are two different problems

"Resize" gets used loosely, but there are really two operations:

- **Resizing** changes the canvas — e.g. 1920×1080 (16:9) becomes 1080×1920 (9:16).
- **Reframing** decides what stays in the shot once the canvas changes shape — which part of a horizontal frame survives the crop.

A plain online resize tool handles the first part fine. It rarely handles the second, because a naive resize just crops from the centre or stretches the footage — which is how a speaker's head gets cut off, or one of two people in frame disappears entirely.

## Doing it without losing the shot

1. **Decide the output ratio first**, from the table above, rather than resizing and figuring out where to post it afterwards.
2. **Use subject-aware or face-tracking cropping** if someone is talking. A fixed centre crop only holds up for a single, stationary subject.
3. **Check the edges after resizing** — anything important that landed outside the new frame needs a different crop, not a resize you accept as-is.
4. **Export at the platform's expected resolution** — 1080×1920 for 9:16, 1080×1080 for square — instead of an arbitrary size that gets recompressed on upload.

If a resized clip already looks off — jittery cropping, a subject drifting out of frame, the wrong part of the shot in view — that's a reframing problem, not a resizing one. See [why auto-reframing looks wrong](/blog/why-auto-reframing-looks-wrong/) for the specific fixes.

## At scale

Resizing one clip by hand is a five-minute job. Resizing and correctly reframing fifteen clips cut from an hour of source video is where doing it manually stops making sense.

---

[Soft Clipper](/) exports the same source clip to 9:16, 1:1 and 16:9 directly, with face-tracking crop — plus fit-and-blur, split-screen and centre fallback modes for shots where tracking one face doesn't apply — so the resize and the reframe happen in one pass instead of two.
