#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

if [ ! -d "$SOURCE_DIR/.claude/skills" ]; then
  echo "Missing source skills directory: $SOURCE_DIR/.claude/skills" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"

for skill_dir in "$SOURCE_DIR"/.claude/skills/*; do
  [ -d "$skill_dir" ] || continue
  skill_name="$(basename "$skill_dir")"
  target="$TARGET_DIR/$skill_name"
  if [ -e "$target" ]; then
    echo "Skipping existing skill: $target" >&2
    continue
  fi
  cp -R "$skill_dir" "$target"
  echo "Installed: $skill_name"
done

echo "Done. Target: $TARGET_DIR"

