---
name: x-viral-image-director
description: Create X-ready shareable bitmap images from an iCloud Drive image folder and optional attached style reference, then generate through imagegen. Use when the user asks to reference all images in iCloud Drive's image folder, match an attached image's mood or art style, fill unspecified image-generation fields, and make an image optimized for X/Twitter likes, reposts, quotes, thumbnail stopping power, or social virality.
---

# X Viral Image Director

Use this skill to turn a folder of reference images and an optional attached mood/style image into one polished image intended for the X timeline. Its single purpose is X-ready image generation: stop the scroll, invite saving, and leave enough ambiguity for quotes without adding text bait.

Use `imagegen-auto-director` for general image prompt automation. Use this skill only when the requested destination or success criterion is X/Twitter engagement, reposts, quotes, likes, or timeline impact.

## Workflow

1. Gather references:
   - Treat an attached image as the primary `style reference` and `mood reference` unless the user says it is the subject.
   - Treat `/Users/ryogokita/Library/Mobile Documents/com~apple~CloudDocs/画像` as the default iCloud Drive image folder when the user says `iCloud Driveの「画像」フォルダ`.
   - Use all images in that folder as palette, composition, texture, and mood evidence unless the user asks for a random subset.
   - If `view_image` cannot inspect local or attachment paths, verify files with `file`, `sips`, and `scripts/analyze_reference_set.py`; continue from measurable evidence when direct visual inspection is unavailable.
2. Analyze the image set:
   - Run `scripts/analyze_reference_set.py --icloud --attachment <path>` when an attachment exists.
   - Extract dimensions, aspect ratios, dominant palettes, average color, contrast/entropy, and repeated mood signals.
   - Summarize folder-wide trends in 1-3 concrete lines before prompting.
3. Choose one X strategy from `references/x-image-heuristics.md`:
   - `gaze-hook`: face or eyes stop the scroll.
   - `world-gap`: an unexplained world detail invites quote posts.
   - `quiet-emotion`: restraint and negative space invite saves.
   - `color-snap`: one sharp accent breaks a muted palette.
   - `motion-freeze`: a captured instant feels shareable.
4. Build an `imagegen` prompt:
   - Preserve the attached image's observable style traits, not exact pixels or identity.
   - Synthesize all folder images by palette, aspect ratio, texture, atmosphere, and composition tendencies.
   - Use vertical `4:5` by default for X mobile feed unless the user specifies another format.
   - Keep text out of the image unless exact text is provided.
   - Avoid manipulative claims such as guaranteeing likes or reposts; optimize visual affordances instead.
5. Generate through the built-in `image_gen` path from the `imagegen` skill.
6. Verify and report:
   - Confirm generated path under `$CODEX_HOME/generated_images/...` unless the user requested a project destination.
   - Report reference roles, the selected X strategy, and the final prompt summary.

## Handoff Prompt Shape

Use this structure before calling `imagegen`:

```text
Use case: stylized-concept or illustration-story
Mode: generate
Asset type: X post image, vertical 4:5
Reference roles: <attachment: style/mood reference>; <iCloud folder: palette/composition/texture reference>
X strategy: <gaze-hook | world-gap | quiet-emotion | color-snap | motion-freeze>
Primary request: Create one original X-ready image from the attached mood and iCloud folder references.
Subject: <one clear focal subject with thumbnail-readable silhouette>
Scene/backdrop: <atmospheric setting with quote-worthy story gap>
Style/medium: <observable traits from attachment, translated into non-copying style language>
Composition/framing: vertical 4:5, mobile timeline readability, focal face/object, controlled negative space
Lighting/mood: <motivated light, emotional tone, contrast>
Color palette: <attachment palette plus folder-wide accents>
Materials/textures: <tactile details from folder trends>
Quality/detail: <crisp focal area, soft background, film/anime/painterly finish as appropriate>
Text (verbatim): "none"
Constraints: original image, no exact copying, no logos, no watermarks, no UI, no recognizable existing characters
Avoid: cluttered focal area, weak silhouette, generic beauty, unreadable face, engagement-bait text
```

## Defaults From Prior Runs

- When the attachment is `PNG画像 14.png`, translate it as: soft muted ivory, pale green-gray atmosphere, warm beige highlights, charcoal accents, gentle high-detail anime rendering, delicate film-like texture, calm emotional tone, and elegant negative space.
- Folder-wide iCloud trends often include tall portrait framing, pale ivory, foggy gray-green, teal mist, deep navy shadows, smoky mauve, muted rose, bronze-gold earth tones, and occasional cyan or magenta spark accents.
- For X, prefer one memorable figure or object over a busy collage. The viewer should understand the focal point instantly and wonder about the story afterward.

## Output Discipline

Do not promise actual engagement. Say the image is optimized for X timeline impact, not guaranteed to earn likes, reposts, or quotes.

When generation succeeds, provide the saved image path and a concise explanation of the reference synthesis. When generation is rate-limited, keep the final prompt and retry after waiting before reporting failure.
