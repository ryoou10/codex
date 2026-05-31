#!/usr/bin/env zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE_FILE="$ROOT_DIR/codex-vscode-codex.code-workspace"

if command -v code >/dev/null 2>&1; then
  exec code "$WORKSPACE_FILE"
fi

exec open -a "Visual Studio Code" "$WORKSPACE_FILE"
