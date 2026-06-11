---
name: visual-prompt-designer
description: Use before image generation when refining prompts, especially character and worldbuilding images, or translating vague design feedback into concrete visual direction. Pair with the imagegen skill when the user wants an actual bitmap generated. Diagnose issues like "too flat", "too cluttered", "not premium", "needs hierarchy", "let it breathe", "tighten it up", "more cinematic", "stronger negative space", "better rhythm", or "needs an anchor", then return a concise diagnosis and an improved prompt.
metadata:
  short-description: Translate vague visual feedback into image prompts
---

# Visual Prompt Designer

Use this skill to turn vague image-generation requests or visual critique into clear prompt direction. The default output is a short design diagnosis followed by a paste-ready improved prompt and a focused avoid list.

Primary domain: character and worldbuilding imagery. The skill can also help with editorial, poster, product, or social visuals, but keep the reasoning anchored in image composition rather than UI implementation.

This skill is the design-translation layer. It does not replace image generation tooling. When the user asks to create or edit a raster image, use the `imagegen` skill after this prompt pass and follow imagegen's generation, editing, save-path, transparency, and validation rules.

## Combined Imagegen Flow

Use this combined flow whenever the user wants both prompt refinement and an actual generated bitmap:

1. Translate the request with this skill first: diagnose the design gap, choose a clear direction, and write an improved prompt.
2. Convert the improved prompt into an imagegen handoff spec using imagegen's taxonomy and shared schema.
3. Generate or edit through `imagegen` using its built-in mode by default.
4. Inspect the output against the original diagnosis:
   - Did the visual anchor read immediately?
   - Is the hierarchy clear at thumbnail size?
   - Does the character/worldbuilding signal survive without explanation?
   - Are the requested constraints, reference roles, text, aspect ratio, and avoid items respected?
5. If iteration is needed, change one design variable at a time, such as framing, lighting, palette, density, or gesture. Do not rewrite the whole concept unless the result misses the user's intent.
6. Report the final imagegen mode, saved path when project-bound, and the final prompt or handoff spec used.

If the user says "generate", "make the image", "画像生成して", "出して", or similar, do the full combined flow. If the user only asks to "詰める", "rewrite", "diagnose", or "prompt only", stop at the prompt/handoff output.

## Workflow

1. Identify the input mode:
   - Vague request: expand it into a stronger visual concept.
   - Existing prompt: diagnose what is underspecified or visually weak.
   - Feedback phrase: translate design language into prompt instructions.
   - Image critique: inspect the image first when one is available, then diagnose.
2. Ask at most 3 questions only when the missing information would materially change the image, such as subject identity, target mood, or required format. Otherwise choose a coherent direction and proceed.
3. Diagnose the design problem in concrete visual terms:
   - focal hierarchy: what should be seen first, second, and last
   - anchor: the face, gesture, silhouette, light source, prop, or contrast point that stops the eye
   - breathing room: the amount of space around the subject and important details
   - rhythm: repeated shapes, color accents, lighting beats, pose lines, or environmental motifs
   - density: whether the image needs more restraint, more detail, or clearer grouping
4. Write the improved prompt with a single coherent art direction. Avoid stacking many style labels that fight each other.
5. Include concrete negatives only. Avoid generic filler like "bad quality" unless the target tool specifically benefits from it.
6. If the user wants an actual generated image, hand off the improved prompt to `imagegen`:
   - classify the use case with imagegen's taxonomy, usually `illustration-story`, `stylized-concept`, `historical-scene`, or `photorealistic-natural`
   - preserve the user's required subject, aspect ratio, reference-image roles, exact text, and avoid list
   - generate only after the prompt is specific enough to execute
   - inspect the result against the diagnosis before reporting completion

When the request involves an exact artist, living creator, copyrighted character, or protected franchise look, translate the reference into observable traits instead of asking for direct imitation.

## Output Format

Use this format unless the user asks for a different structure:

```markdown
Diagnosis
- ...

Design Direction
- ...

Improved Prompt
...

Negative / Avoid
...

Imagegen Handoff
...

Result Check
...
```

Keep `Diagnosis` and `Design Direction` concise. The `Improved Prompt` should be directly usable in an image-generation tool. Include `Imagegen Handoff` only when the next action is to generate or edit an image. Include `Result Check` only after an image has been generated or inspected.

## Prompt Construction

Include the relevant parts in this order:

1. Subject and role: who or what the image is about, including emotional state.
2. World signal: era, culture, environment, materials, social context, or story implication.
3. Composition: framing, camera distance, angle, subject placement, foreground/midground/background.
4. Hierarchy and anchor: what dominates the image and what supports it.
5. Light and color: light source, color temperature, contrast, palette, and accents.
6. Texture and detail: fabric, skin, metal, weathering, atmosphere, props, environment.
7. Lens or medium: cinematic portrait, painterly key art, anime cel illustration, film still, etc.
8. Practical constraints: aspect ratio, no text, clean silhouette, readable face, or transparent background when relevant.

## Imagegen Handoff

When handing off to `imagegen`, compress the improved prompt into imagegen's shared prompt schema:

```text
Use case: <imagegen taxonomy slug>
Asset type: <preview, character key art, website hero, sprite, etc.>
Primary request: <one-sentence intent>
Subject: <main subject and role>
Scene/backdrop: <environment and world signal>
Style/medium: <photo, illustration, cinematic key art, etc.>
Composition/framing: <camera distance, angle, placement, depth layers>
Lighting/mood: <source, color temperature, contrast, mood>
Color palette: <dominant colors and accents>
Materials/textures: <surfaces and detail logic>
Text (verbatim): "<exact text, or none>"
Constraints: <must keep, aspect ratio, reference-image roles, transparency needs>
Avoid: <focused negatives>
```

If the user only asked for prompt improvement, stop after the written output. If the user asked to generate, call the built-in `image_gen` tool by default through the imagegen workflow.

## Character/Worldbuilding Imagegen Defaults

Use these defaults when the user gives a vague character or world prompt and does not specify otherwise:

- Use case: `stylized-concept` for concept art, `illustration-story` for narrative scenes, `photorealistic-natural` for realistic portraits, and `historical-scene` when period accuracy matters.
- Asset type: `preview` unless the user names a project destination or use case.
- Aspect ratio: infer from use. Use portrait for character key art, wide for environmental or hero scenes, square for exploration thumbnails.
- Text: `none` unless the user provides exact text.
- References: label every provided image as edit target, identity reference, style reference, composition reference, or mood reference before generation.
- Transparency: defer to imagegen's chroma-key-first path unless the user explicitly confirms true native transparency fallback.

## Design Translation Rules

- "Fix the hierarchy" -> define one primary focal point, one secondary read, and quieter supporting detail.
- "Let it breathe" -> add negative space, simplify background activity, and separate the subject from surrounding elements.
- "Tighten it up" -> crop closer, reduce loose empty margins, strengthen the silhouette, and remove low-value details.
- "Too flat" -> add foreground/midground/background depth, stronger light direction, atmospheric perspective, and value contrast.
- "Too cluttered" -> group details into fewer masses, reduce competing highlights, and reserve detail for the focal area.
- "More cinematic" -> specify lens, camera height, motivated lighting, depth layers, color grade, and a decisive moment.
- "More premium" -> use restraint, high-quality materials, controlled highlights, refined palette, and spacious composition.

For deeper phrase banks and examples, read `references/design-vocabulary.md`.
