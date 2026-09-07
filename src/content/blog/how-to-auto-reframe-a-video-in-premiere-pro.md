---
title: "How to auto-reframe a video in Premiere Pro"
description: "Applying Auto Reframe to a sequence or clip in Premiere Pro, what it actually tracks, and the situations where it needs a manual fix afterwards."
published: 2026-09-07
tags: ["guide", "reframing", "premiere-pro"]
---

<p class="answer">Premiere Pro auto-reframes video with a built-in effect called Auto Reframe: apply it to a sequence or clip, choose a target aspect ratio, and it tracks the main subject and moves the crop to follow them. It works from a source video already sitting in a 16:9 (or similar) timeline — it does not generate new footage, only recrops and repositions what's there.</p>

## Applying it to a sequence

The most common route is sequence-level, because it reframes everything on the timeline at once rather than clip by clip:

1. Duplicate the sequence first — Auto Reframe changes the sequence's frame size, and you generally want to keep the original 16:9 cut untouched.
2. Right-click the duplicated sequence in the Project panel and choose **Auto Reframe Sequence**, or find it in the Effects panel and drag it onto the sequence.
3. Pick a target aspect ratio — 9:16 for TikTok and Reels, 1:1 or 4:5 for feed posts — and Premiere analyses the footage and generates tracking keyframes automatically.

Adobe's own documentation describes it as reframing "entire sequences" for exactly this batch case, which is the scenario most people actually have — [Add Auto Reframe effect to sequences](https://helpx.adobe.com/premiere/desktop/add-video-effects/commonly-used-effects/add-auto-reframe-effect-to-a-sequence.html).

## Applying it to a single clip

If only one shot in a longer edit needs reframing, applying Auto Reframe as a clip-level effect from the Effects panel keeps everything else at the original ratio. This is the better choice when most of a sequence is graphics, screen capture or a static shot that a full sequence reframe would mangle — see [Add Auto Reframe effect to clips](https://helpx.adobe.com/premiere/desktop/add-video-effects/commonly-used-effects/add-auto-reframe-effect-to-a-clip.html).

## What it actually tracks

Auto Reframe generates Motion effect keyframes based on detected motion and faces in the frame, then animates the crop position across the clip. That has two practical consequences worth knowing before you rely on it:

- **It is keyframe-based, so it is editable afterwards.** If the crop drifts to the wrong place for a few seconds, you can open the Motion effect on that clip and adjust or delete individual keyframes rather than starting over.
- **It tracks one point of interest at a time.** With two people in frame who take turns speaking, it will usually settle on whichever face is largest or most central rather than switching cleanly between them — the same failure mode covered in [why auto-reframed clips look wrong](/blog/why-auto-reframing-looks-wrong/), which goes through the fix (split-frame stacking) in more detail.

## Where it needs a manual pass

Three situations reliably need hand-adjustment after running Auto Reframe:

**Two-person interviews.** Expect to redo the framing as a split-frame stack rather than trust a single tracked crop across a back-and-forth conversation.

**Screen recordings and slides.** There's no face to track and nothing to centre a crop on, so Auto Reframe either does nothing useful or crops off part of the screen. Scale-and-blur (fit the whole frame in and pad the sides) works better here, and has to be set up by hand.

**Fast cuts between camera angles.** Auto Reframe re-analyses each clip independently, so if your sequence has many short cuts, check every one rather than assuming a single reframe pass covers the whole timeline correctly.

None of this makes Auto Reframe unreliable — for a single speaker sitting reasonably still, it gets the crop right without intervention most of the time. It just is not a "set once, ignore forever" tool for anything with more moving parts than that.

## If you're doing this repeatedly

Auto Reframe is a per-project effect: duplicate a sequence, reframe it, export, and do the same steps again for the next video. For a one-off video that's fine. For a weekly batch of clips cut from the same long recording, [the process is the same one covered for turning a long video into Shorts](/blog/turn-long-videos-into-shorts/) — picking moments, framing them, captioning them — and doing it by hand in Premiere for every clip is the part that gets slow.

[Soft Clipper](/features/auto-reframe/) automates that batch case specifically: it tracks the speaker, smooths the crop and resets on scene changes across an entire set of clips at once, running locally on your PC rather than as a per-sequence effect you reapply each time.
