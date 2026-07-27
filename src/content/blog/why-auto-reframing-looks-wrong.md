---
title: "Why auto-reframed clips look wrong (and how to fix it)"
description: "Cropped-off heads, jittery framing and speakers who wander out of shot. The three reasons automatic 9:16 reframing fails, and what to do about each one."
published: 2026-07-24
tags: ["guide", "reframing"]
---

You run a clip through an automatic tool, and something about the result is off. The words are right, the timing is right, and yet it looks like nobody edited it. Almost always it is the framing, and almost always it is one of three specific failures.

## Failure 1: the centre crop

The cheapest way to make a 16:9 video vertical is to keep the middle 9/16ths and throw the rest away. It works only if the subject sits dead centre and never moves — which is to say, it works in almost no real footage.

Two-person interviews are the worst case: a centre crop of a two-shot gives you the gap between two people, with half a face on each edge.

**Fix:** use tracking, or split the frame and stack the two speakers vertically. A tool that only offers a centre crop is not doing the job.

## Failure 2: tracking that snaps

Tracking solves the first problem and introduces a new one. If the crop jumps to a new position the instant a different face becomes largest, the result twitches — and viewers read the twitch as broken software, even if they cannot say why.

**Fix:** smooth motion. The crop should drift toward the subject over a fraction of a second, the way a camera operator would move. Good tracking is invisible; visible tracking is a bug.

## Failure 3: tracking that never resets

The opposite mistake. The tool locks onto a subject at the start and keeps following that position even after the edit cuts to a different camera — so you spend eight seconds looking at an empty chair while someone off-screen talks.

**Fix:** detect scene changes and start again. Any cut significant enough for a human to notice should reset the tracking.

## The case where none of this helps

Screen recordings, slides, gameplay, anything where the information fills the frame. Cropping loses the content, and tracking has no face to follow.

For these, do not crop at all. Scale the whole frame to the width of the vertical canvas and fill the space above and below with a blurred, darkened copy of the same footage. It is not elegant, but it keeps every pixel of what mattered, and viewers are entirely used to it.

## A checklist before you export

- Does anyone's head leave the frame at any point?
- Does the crop move when nobody has moved?
- After each cut, is the camera on the person speaking?
- On a phone-sized screen, can you read the captions and see the face at the same time?
- Is anything important sitting in the bottom fifth, where the platform draws its own interface?

Fixing framing after upload is not possible, and re-uploading resets whatever momentum the post had. It is worth the thirty seconds.

---

[Soft Clipper](/features/auto-reframe/) does the tracking, the smoothing and the scene-change reset locally, and lets you drag the crop by hand on any clip where the automatic choice was wrong.
