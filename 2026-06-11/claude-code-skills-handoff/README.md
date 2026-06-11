# Claude Code Skills Handoff

This folder packages the custom Codex skills that were created or adapted for this user's workflow so they can be reviewed, copied, or imported into Claude Code.

## Contents

- `CLAUDE.md`: Project-level instructions for Claude Code.
- `.claude/skills/`: Skill folders. Each skill keeps its original `SKILL.md` plus any supporting `scripts/`, `references/`, `agents/`, templates, or eval files.
- `manifest.json`: Inventory of included skills and their intended role.
- `install-to-claude.sh`: Optional local copy helper.

## Included Skills

Core image and visual workflow:

- `imagegen-auto-director`
- `x-viral-image-director`
- `visual-prompt-designer`

Prompt creation workflow:

- `prompt-architect`
- `prompt-business-improvement`
- `prompt-work-report`
- `prompt-research-brief`
- `prompt-writing-draft`
- `prompt-codex-task`
- `prompt-revision-request`

Other custom or adapted workflow skills:

- `light-novel-creator`
- `youtube-yoga-notifier`
- `skill-creator-2`
- `xurl`

## How To Use With Claude Code

Option A: Project-scoped use

1. Place this folder at the root of a Claude Code project.
2. Open the folder with Claude Code.
3. Ask Claude Code to read `CLAUDE.md` and use the skills under `.claude/skills`.

Option B: Copy into Claude's local skill folder

1. Review the files first.
2. Run `./install-to-claude.sh` from this folder, or manually copy the folders under `.claude/skills/` into the Claude Code skills directory used on your machine.
3. Restart or refresh Claude Code if needed.

## Safety Notes

- The copied skill files may reference Codex-specific tools such as `image_gen`, `view_image`, `tool_search`, or Codex skill paths.
- In Claude Code, those references should be treated as workflow guidance. If a tool is unavailable, Claude Code should use the closest local equivalent or ask before changing execution strategy.
- Do not run scripts from a skill until you have reviewed what they do.
- Do not expose credentials, API keys, private account files, or authentication stores to a skill.

## Source

Source skill directory on this Mac:

`/Users/ryogokita/.codex/skills`

