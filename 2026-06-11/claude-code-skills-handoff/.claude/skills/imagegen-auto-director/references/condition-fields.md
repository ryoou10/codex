# Condition Field Heuristics

Use these defaults only when the user leaves a field unspecified. Preserve explicit user instructions and evidence from reference images first.

## Subject

- For people or characters, define age range, gender presentation if relevant, face readability, hair, wardrobe, expression, pose, and one strong silhouette feature.
- For products or objects, define material, finish, scale, condition, edge quality, surface texture, and one immediately readable use cue.
- For animals or plants, define species, posture/growth form, texture, health/state, motion, and environment fit.
- If identity matters, prioritize likeness and recognizable features over added detail.

## Scene/Setting

- Character portraits default to an environment that supports the character story without stealing focus.
- Product shots default to a clean contextual surface, controlled props, and generous negative space.
- Fantasy or worldbuilding prompts default to a location with one cultural/material signal and one atmospheric signal.
- If the reference background is weak or cluttered, simplify it into fewer readable depth layers.

## Style

- Use one primary medium: photorealistic editorial photo, cinematic film still, anime cel illustration, painterly key art, 3D product render, watercolor illustration, oil painting, ink poster, or pixel art.
- Add only compatible modifiers such as retro film grain, minimalist layout, cyberpunk neon, premium editorial restraint, soft watercolor bleed, or tactile clay render.
- Translate exact artist or franchise references into visible traits such as line weight, palette, lens, shape language, material finish, or atmosphere.

## Composition/Camera

- Character key art defaults to portrait or 4:5 framing, eye-level or slight low angle, readable face, strong silhouette, and background depth.
- Product shots default to 1:1, 4:5, or 16:9 depending on usage, three-quarter angle, clean negative space, and controlled reflections.
- Environmental scenes default to wide framing, clear foreground/midground/background, a human-scale anchor, and atmospheric perspective.
- Use close-up only when texture, face, emotion, or product detail is the point.

## Lighting & Color

- Choose a motivated light source: window light, sunset backlight, neon signage, studio softbox, candlelight, moonlight, overcast diffusion, or volumetric beam.
- Define color temperature and contrast. Avoid vague words like "beautiful colors" without palette behavior.
- Use one dominant palette and one accent. Keep accents near the focal point.
- If the reference image has weak contrast, add directional light and separate subject from background.

## Quality

- Specify visible quality through concrete cues: crisp material texture, controlled depth of field, clean edges, readable eyes, refined reflections, atmospheric haze, film grain, brush texture, or detailed surface wear.
- For photorealism, include lens feel, natural imperfections, physically plausible light, and restrained retouching.
- For illustration, include line clarity, shape design, value grouping, texture style, and detail concentration around the focal area.
- For UI or project assets, include exact aspect ratio, no text unless specified, safe margins, and background/transparent requirements.

## Avoid List Defaults

Use a focused avoid list:

- unwanted text, watermark, logo, signature
- extra limbs, distorted hands, duplicated faces, unreadable eyes when people are present
- cluttered background when the focal subject must read quickly
- mismatched style, low-value detail, muddy colors, overexposed highlights, crushed shadows
- changed identity when using identity references
