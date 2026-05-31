# Codex + VS Code workspace

This folder is prepared as a Codex-managed workspace that can be opened directly in Visual Studio Code.

## Open in VS Code

Run:

```sh
./scripts/open-vscode.sh
```

If the `code` command is available, the script uses it. Otherwise, it opens the workspace through the macOS Visual Studio Code app.

## Files

- `codex-vscode-codex.code-workspace`: VS Code workspace entry point.
- `.vscode/settings.json`: Local editor defaults for this workspace.
- `.vscode/extensions.json`: Recommended VS Code extensions.
- `scripts/open-vscode.sh`: Helper script for opening this workspace.
