# Design Vocabulary for Image Prompts

Use this reference when a request contains vague visual feedback or designer shorthand that needs to become concrete image-generation language.

## Core Translations

| Feedback | Prompt Translation |
| --- | --- |
| tighter | closer crop, fewer loose margins, more deliberate framing, stronger silhouette |
| looser | wider framing, more surrounding atmosphere, more negative space, softer edge pressure |
| bump the leading | increase line spacing for image text; use only when text is part of the image |
| set the text tighter | reduce letter spacing or line breaks; use only when text is part of the image |
| let it breathe | clear space around the subject, fewer background distractions, calmer value structure |
| fix the hierarchy | one dominant focal point, one secondary element, subdued supporting detail |
| anchor it | add a face, hand gesture, strong prop, light source, contrast block, or silhouette that stops the eye |
| rhythm | repeat shapes, color accents, light spots, pose angles, fabric folds, architecture, or environmental motifs |
| negative space | intentionally quiet empty area that frames the subject and gives room for copy or atmosphere |
| too flat | stronger depth layers, directional light, atmospheric haze, foreground overlap, value contrast |
| too busy | fewer competing highlights, simpler background, grouped details, detail concentrated near the face or action |
| lacks polish | refined materials, cleaner edges, intentional palette, controlled highlights, less random detail |

## Character and Worldbuilding Checks

A strong character/world prompt usually answers:

- Role: what the character is in the world, not just what they look like.
- Emotion: what they are feeling or hiding.
- Gesture: what the hands, posture, and eye line are doing.
- Costume logic: materials and details that imply culture, class, climate, or occupation.
- World trace: background details that imply history without stealing focus.
- Light logic: where the light comes from and why it exists in the scene.
- Focal anchor: the strongest face, silhouette, hand, weapon, tool, glow, or shape.
- Restraint: what should stay quiet so the focal point reads clearly.

## Useful Prompt Moves

- Add hierarchy: "The face is the primary focal point, the hands and glowing object are the secondary read, the background remains soft and low-contrast."
- Add breathing room: "Leave clean negative space on the upper left, with the character placed slightly right of center."
- Add rhythm: "Repeat crescent shapes in the cloak folds, moonlit windows, and curved blade to create visual rhythm."
- Add depth: "Layer a blurred foreground arch, sharp midground figure, and misty background towers."
- Add premium restraint: "Use a restrained palette of ivory, black lacquer, muted gold, and one crimson accent."
- Add cinematic specificity: "Low camera angle, 50mm lens feel, shallow depth of field, motivated lantern light, rain haze catching the backlight."

## Diagnosis Patterns

Use these short diagnoses before rewriting:

- "The subject is named, but the image lacks a focal hierarchy and a clear visual anchor."
- "The mood is present, but the worldbuilding is generic; the prompt needs material, culture, and environmental signals."
- "The image direction is dense, but the prompt does not reserve quiet areas, so every detail competes for attention."
- "The prompt asks for a style, but not a shot: camera distance, angle, light source, and depth layers are missing."
- "The character has surface details, but not intent; gesture, eye line, and emotional tension should carry the scene."

## Imagegen Pairing Patterns

Use these when the user wants the prompt pass and actual generation in one flow:

- Character key art: use case `stylized-concept` or `illustration-story`; emphasize role, expression, gesture, silhouette, costume logic, and world trace.
- Period or lore scene: use case `historical-scene` when accuracy matters; specify materials, architecture, clothing logic, and anachronisms to avoid.
- Photoreal character portrait: use case `photorealistic-natural`; specify lens feel, natural skin texture, motivated light, and restrained retouching.
- Website or campaign visual with a character: use case `ads-marketing` only when the image must sell or support a layout; reserve negative space for copy.
- Transparent character asset: use imagegen's transparency guidance; request a flat chroma-key background first unless the user confirms true native transparency fallback.

## Post-Generation QA

After imagegen returns a result, check it with the same design vocabulary used before generation:

- Anchor: the viewer should know where to look first within one second.
- Hierarchy: face, gesture, prop, or environment should not compete equally unless the concept intentionally uses chaos.
- Breathing room: important silhouettes and copy-safe areas should not feel accidentally crowded.
- Rhythm: repeated shapes, color accents, or light beats should support the composition instead of becoming noise.
- Density: detail should cluster near the focal point and quiet down elsewhere.
- World signal: costume, materials, architecture, and props should imply a coherent setting.
- Prompt fidelity: required subject, reference role, text, aspect ratio, and avoid list should be respected.

If the output fails, revise one axis at a time:

- Weak focal point -> strengthen face lighting, silhouette contrast, or hand/prop anchor.
- Cluttered read -> reduce background highlights and group details into larger masses.
- Generic world -> add material culture, environment history, climate, or occupation-specific props.
- Flat composition -> add foreground overlap, midground subject, background depth, and directional light.
- Wrong tone -> adjust palette, contrast, lens distance, and character expression before changing the whole subject.

## Compact Example

Weak input:

```text
A cool dark fantasy swordswoman, cinematic, very detailed.
```

Improved direction:

```text
A scarred oathbound swordswoman standing in the doorway of a ruined chapel, her face calm but exhausted, one hand resting on a rain-darkened silver blade. Three-quarter portrait, slightly low camera angle, the face as the primary focal point and the blade hilt as the secondary anchor. Torn black wool cloak, dull steel armor with hand-etched devotional marks, wet stone floor, collapsed stained glass in the background. Cold moonlight from behind outlines her silhouette, while a small amber votive candle lights one side of her face. Restrained palette of blue-black, bone white, tarnished silver, and a single red thread tied around the sword grip. Painterly cinematic key art, shallow depth of field, crisp facial features, quiet negative space above the shoulder, no text.
```
