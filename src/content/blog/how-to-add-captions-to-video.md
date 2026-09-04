---
title: "How to add captions to a video (and why burned-in beats uploaded)"
description: "The difference between burned-in and uploaded captions, why most viewers never see the second kind, and a practical process for captioning short-form clips people actually read."
published: 2026-09-04
tags: ["guide", "captions"]
---

Most of the advice on captioning a video skips the one decision that determines whether anyone reads them at all: burned-in, or uploaded as a separate file. Get this wrong and the rest of the styling doesn't matter.

## Burned-in vs. uploaded: pick burned-in for short-form

An uploaded caption file (.srt or .vtt) is a track the platform can show or hide. On YouTube, viewers have to turn it on. On TikTok, Reels and Shorts, most players don't support the file at all — the platform either ignores it or auto-generates its own, usually worse, captions from your audio.

Burned-in captions are rendered directly into the video frame. They're always there, they look exactly the way you designed them, and they work identically on every platform because they're not a separate feature the player has to support — they're just pixels.

The tradeoff: burned-in captions can't be turned off, and if there's a typo you have to re-render, not just fix a text file. For short-form specifically, that tradeoff is worth it — [most short-form video is watched with the sound off](/blog/turn-long-videos-into-shorts/), which makes captions the primary way most viewers understand what's being said, not a backup for the hard of hearing.

## Getting the transcript right

Every automatic captioning tool starts from a speech-to-text transcript, and every mistake downstream starts as a mistake in that transcript. Two things to check before you trust it:

- **Names and jargon.** Speech-to-text guesses at anything it hasn't seen before — product names, people's names, technical terms. A wrong guess here reads as a mistake to viewers even though it's the software's fault, not yours.
- **Punctuation at clause boundaries.** Automatic punctuation tends to be roughly right but not exactly right, and a misplaced break changes where the caption line splits — which changes how fast a line reads.

Thirty seconds of proofreading before export catches almost all of this.

## Styling for readability, not decoration

- **Size:** large enough to read on a phone at arm's length without pausing. If you have to ask "is this too big," it probably isn't.
- **Contrast:** a solid or semi-transparent background block behind the text beats an outline alone — outlines fail against busy or light backgrounds.
- **Position:** keep captions clear of the bottom fifth of the frame, where TikTok, Reels and Shorts all draw their own UI (like, comment, follow buttons). A caption that's readable in your editor and covered by an interface element on the actual app is a caption nobody read.
- **Line length:** one or two short lines per caption, timed to roughly match natural speech pauses. A caption that changes every 0.3 seconds is unreadable; one that sits on screen for four seconds of continuous speech has fallen behind.

## Translation and multiple languages

If you're captioning for an audience that doesn't share your source language, translate the transcript before styling, not after — translated text runs longer or shorter than the original in almost every language pair, and re-timing captions after they're already burned in means starting over. Machine translation is good enough for captions in most language pairs now; it's worth a native-speaker skim before publishing if the content is commercial rather than casual.

---

[Soft Clipper](/features/captions/) transcribes, punctuates and burns in captions automatically as part of the clipping process, styled to stay clear of platform UI on every format — no separate captioning step or subtitle file to manage.
