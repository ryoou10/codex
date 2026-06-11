---
name: imagegen-auto-director
description: Convert local or attached reference images plus optional user conditions into polished image-generation specs, then generate or edit bitmap images through the imagegen skill. Use when the user wants automated image generation from image files, reference images, rough visual ideas, or a six-part condition set covering subject, scene, style, composition, lighting/color, and quality, especially when unspecified fields should be creatively filled instead of repeatedly questioned.
---

# Imagegen Auto Director

Use this skill as the creative-director layer before image generation. Its single purpose is to inspect provided visual inputs, merge them with the user's optional conditions, fill missing creative choices coherently, and hand a production-ready prompt to `imagegen`.

Do not stop at prompt writing when the user asks to generate, create, make, produce, automate image generation, or otherwise expects a bitmap result. Use the built-in `image_gen` path through the `imagegen` skill unless the user explicitly asks for another route.

## Workflow

1. Locate every image input:
   - If the user provides local file paths, inspect each image with `view_image` before using it.
   - If the user says the images are in iPhone Files > iCloud Drive > image files, check the Mac sync path: `/Users/ryogokita/Library/Mobile Documents/com~apple~CloudDocs/画像`. Use `scripts/list_icloud_images.py` to list image candidates with size and pixel dimensions.
   - If iCloud paths are visible to the shell but not to `view_image`, copy the selected image non-destructively to `/private/tmp/` and inspect the copy. If that still fails, verify with `sips -g pixelWidth -g pixelHeight` and ask the user for an attachment only if visual inspection is impossible.
   - If the user mentions a folder, use `rg --files` or `find` to list common raster files, then inspect only the relevant candidates.
   - If images are attached in the conversation, treat them as already visible and label their roles.
2. Assign a role to each image:
   - `edit target`: the image to modify while preserving its identity or layout
   - `identity reference`: subject, face, character, object, product, or brand identity to preserve
   - `style reference`: visual medium, rendering language, texture, color, or finish
   - `composition reference`: camera angle, framing, pose, spatial layout, or crop
   - `mood reference`: atmosphere, lighting, emotional tone, weather, or energy
3. Extract concrete visual evidence from the images:
   - subject identity, silhouette, pose, expression, clothing, materials, and key objects
   - setting, depth layers, environmental clues, time of day, weather, and supporting props
   - style cues, line quality, realism level, lens/medium, texture density, and era
   - camera distance, angle, crop, aspect ratio, negative space, and focal hierarchy
   - light source, contrast, color temperature, palette, accents, shadows, and atmosphere
4. Merge the evidence with the user's six condition fields. Preserve explicit user instructions over inferred image evidence.
5. Creatively fill any unspecified field with one coherent direction. Choose defaults that support the user's goal instead of listing alternatives.
6. Build an `imagegen` handoff spec and then call `imagegen`:
   - For new images from references, use generate mode.
   - For modifying a source image while preserving parts of it, use edit mode.
   - For multiple distinct outputs, create one focused spec per output.
7. Inspect the generated result against the spec. If it misses the subject, constraints, or focal hierarchy, iterate once with one targeted correction.
8. Report the final mode, saved path when project-bound, reference roles, and final prompt.

## Condition Fields

Treat the user's fields as inputs, not a questionnaire. Ask only when a missing answer changes a hard constraint such as identity, exact text, safety, usage rights, destination, or required format.

Use this fill order:

1. `Subject`: define the main person, character, object, animal, plant, or product. Include age range, gender presentation, clothing, hairstyle, expression, pose, material, texture, condition, and the visual anchor when relevant.
2. `Scene/Setting`: define location, world, era, indoor/outdoor context, time of day, weather, atmosphere, surrounding objects, crowding, effects, and story implication.
3. `Style`: choose one primary visual medium or genre, then add only compatible modifiers. Avoid stacking conflicting labels.
4. `Composition/Camera`: define camera angle, shot size, framing, aspect ratio, subject placement, foreground/midground/background, negative space, and focal hierarchy.
5. `Lighting & Color`: define the motivated light source, contrast, color temperature, palette, accent colors, shadows, glow, haze, and grade.
6. `Quality`: define detail density, texture behavior, depth of field, lens feel, finish, polish level, and important technical constraints.

If the user leaves fields blank, use the heuristics in `references/condition-fields.md`. Read it when the request is vague, high-stakes visually, or needs a reusable style system.

## Creative Fill Rules

- Make one decisive art direction. Do not present multiple options unless the user asks for variants.
- Preserve the user's explicit subject, image identity, exact text, aspect ratio, and avoid list.
- Add details only when they strengthen the stated goal or make the image more executable.
- Keep the prompt internally consistent: medium, era, lighting, color, and camera choices should reinforce each other.
- Avoid direct imitation of living artists or protected franchise styles. Translate references into observable traits.
- Avoid generic filler such as "masterpiece" unless the target tool specifically benefits from it. Prefer concrete qualities: crisp fabric weave, controlled rim light, shallow depth of field, clean silhouette, readable face, textured ceramic glaze, etc.
- Use no text in the image unless the user gives exact text to render.

## Imagegen Handoff Format

Use this format before generation or editing:

```text
Use case: <imagegen taxonomy slug>
Mode: <generate | edit>
Asset type: <preview, hero image, character key art, product shot, sprite, poster, etc.>
Reference roles: <path-or-label: role; path-or-label: role>
Primary request: <one-sentence intent>
Subject: <main subject and preserved identity details>
Scene/backdrop: <location, time, weather, environment, surrounding elements>
Style/medium: <single coherent visual style>
Composition/framing: <angle, shot size, aspect ratio, placement, depth layers>
Lighting/mood: <light source, contrast, atmosphere, emotional tone>
Color palette: <dominant palette and accents>
Materials/textures: <surface detail, tactile qualities, finish>
Quality/detail: <resolution/detail intent, focus, lens/depth behavior>
Text (verbatim): "<exact text, or none>"
Constraints: <must preserve, destination, transparency, safety, format>
Avoid: <specific negative constraints>
```

## Optional Script

Use `scripts/compose_imagegen_spec.py` when the user provides structured JSON conditions or when repeated outputs need the same schema. The script normalizes fields and produces the handoff skeleton, but it does not replace visual inspection or creative completion.

Example:

```bash
python scripts/compose_imagegen_spec.py conditions.json
```

Use `scripts/list_icloud_images.py` when the user points to iPhone Files > iCloud Drive > image files and does not name a specific file:

```bash
python scripts/list_icloud_images.py --limit 12
```

Expected JSON keys:

```json
{
  "use_case": "stylized-concept",
  "mode": "generate",
  "asset_type": "preview",
  "reference_roles": [],
  "primary_request": "",
  "subject": "",
  "scene": "",
  "style": "",
  "composition": "",
  "lighting_color": "",
  "quality": "",
  "text": "none",
  "constraints": "",
  "avoid": []
}
```

## Output Discipline

When returning only a prompt, provide `Reference roles`, `Final Prompt`, and `Avoid`.

When generating an image, follow the `imagegen` skill's reporting rules. Include the final prompt or handoff spec, final path for project-bound assets, and any iteration performed.
