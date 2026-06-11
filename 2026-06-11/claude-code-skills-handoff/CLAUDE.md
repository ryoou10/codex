# Claude Code Instructions For This Skills Bundle

Use the local skill folders in `.claude/skills` when the user's request clearly matches a skill.

## Skill Use Rules

1. Read the relevant `.claude/skills/<skill-name>/SKILL.md` before applying a skill.
2. Follow the skill's workflow, but adapt Codex-specific tool names to the tools available in Claude Code.
3. Keep user-facing replies in Japanese if the user is writing in Japanese.
4. Keep generated artifacts, code, config files, templates, schemas, commit messages, and PR text in the appropriate normal project style.
5. Do not run helper scripts unless the user asked for execution or execution is necessary and safe.
6. If a skill references a local path that does not exist on the current machine, inspect the current workspace first and ask only if the missing path changes the outcome.
7. If a skill is only for prompt creation, produce a copy-ready prompt and do not pretend it executed the downstream workflow.

## Routing

- Use `imagegen-auto-director` for image generation direction from local or attached images.
- Use `x-viral-image-director` for X-ready shareable image concepts from reference images.
- Use `visual-prompt-designer` before image generation when the request needs stronger composition, mood, or visual hierarchy.
- Use `prompt-architect` to route prompt-writing requests to the most specific prompt child skill.
- Use one prompt child skill per deliverable type:
  - `prompt-business-improvement`
  - `prompt-work-report`
  - `prompt-research-brief`
  - `prompt-writing-draft`
  - `prompt-codex-task`
  - `prompt-revision-request`
- Use `light-novel-creator` for Japanese fiction, light novel, story, plot, worldbuilding, or character-setting requests.
- Use `youtube-yoga-notifier` for recurring YouTube yoga recommendations or reminder workflows.
- Use `xurl` only for X/Twitter workflows, and verify authentication safely before posting or modifying anything.
- Use `skill-creator-2` when creating, modifying, or evaluating skills.

## Claude Code Adaptation Notes

These skills were originally stored in Codex format. Most are Markdown instruction bundles and can be used directly. Some contain references to Codex-specific behavior:

- `image_gen` means use Claude Code's available image-generation path, if configured, or produce a prompt/spec instead.
- `view_image` means inspect the image with whatever image-viewing or file-inspection capability is available.
- `~/.codex/skills` means the original source location, not the current Claude Code install path.
- `iCloud Drive/画像` on this Mac maps to `/Users/ryogokita/Library/Mobile Documents/com~apple~CloudDocs/画像`.

When a direct tool equivalent is missing, preserve the user's intent and clearly state what was done instead.

