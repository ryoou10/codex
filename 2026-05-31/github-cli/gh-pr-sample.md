# GH CLI Pull Request Verification Sample

This file makes PR #1 a reusable sample for checking GitHub CLI pull request
flows. It keeps the changed file small, textual, and scoped to this project so
`gh pr view --json files` has an easy-to-read result.

## Sample Metadata

- Repository: `ryoou10/codex`
- Base branch: `main`
- Head branch: `codex/test-pr`
- PR number: `1`
- Suggested title: `[codex] Add gh CLI verification sample`

## Commands

Use these commands from the repository root.

```bash
gh pr create \
  --base main \
  --head codex/test-pr \
  --title "[codex] Add gh CLI verification sample" \
  --body-file 2026-05-31/github-cli/gh-pr-sample.md

gh pr view 1 \
  --json number,title,body,headRefName,baseRefName,state,isDraft,files

gh pr edit 1 \
  --title "[codex] Add gh CLI verification sample" \
  --body-file 2026-05-31/github-cli/gh-pr-sample.md
```

## Expected Checks

- `gh pr view 1` returns PR #1 with base `main` and head `codex/test-pr`.
- The title is `[codex] Add gh CLI verification sample`.
- The files list includes `2026-05-31/github-cli/gh-pr-sample.md`.
- `gh pr edit 1 --body-file 2026-05-31/github-cli/gh-pr-sample.md`
  can refresh the body without changing the sample file.

## Notes

PR #1 already exists, so the `create` command is recorded as the reproducible
command shape for this branch. Use `view` and `edit` directly against PR #1 when
checking the live GitHub CLI workflow.
