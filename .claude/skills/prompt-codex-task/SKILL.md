---
name: prompt-codex-task
description: Create copy-ready prompts for Codex coding tasks such as bug fixes, feature implementation, refactors, tests, code review, and repository investigation. Use this skill when the user asks for prompts about "Codexに頼む", "バグ修正", "実装依頼", "リファクタ", "テスト追加", "既存コードを見て", "PRレビュー", or asking Codex to work in a local repo. This skill is intentionally narrow and should not be used for general ChatGPT writing or research prompts.
---

# Codex Task Prompt Builder

Use this skill to create a copy-ready prompt that asks Codex to work on code or a repository.

This skill has one use case: coding-agent task prompts.

## Default Goal

Create a prompt that tells Codex to:

- inspect the current files first
- understand existing patterns
- implement or diagnose the requested change
- avoid unrelated refactors
- run relevant checks
- report changed files, commands, and residual risks

## Output Format

Always respond with:

```markdown
## 完成プロンプト

```text
[copy-ready prompt]
```

## 補った条件

- ...

## 使う前に差し替える箇所

- ...
```

## Copy-Ready Prompt Template

```text
目的:
[実装したいこと / 直したい不具合 / 調査したいこと] を、既存コードの流儀に合わせて対応してください。

前提:
- 対象リポジトリ: 現在の作業ディレクトリ
- 関連しそうな画面・機能: [分かる範囲で入力]
- 期待する挙動: [期待する状態]
- 現在の問題: [エラー、再現手順、困っている点]

作業方針:
1. まず関連ファイルを検索・確認し、既存の設計、命名、テスト方針を把握してください。
2. 変更範囲を必要最小限に絞ってください。
3. 既存のユーザー変更や無関係な差分を戻さないでください。
4. 実装前に、原因または変更方針を簡潔に整理してください。
5. 実装後、可能な範囲でテスト、lint、型チェック、または再現確認を実行してください。
6. 検証できなかった場合は、その理由と代替確認方法を明記してください。

制約条件:
- 不要な大規模リファクタはしない
- 既存スタイルを優先する
- 推測でファイル構成を決めず、実ファイルを確認する
- 破壊的な git 操作はしない

最終報告:
- 変更したファイル
- 変更内容の要約
- 実行した確認コマンドと結果
- 残っているリスクや未確認点
```

## Strengthening Rules

- If the user mentions a bug, include reproduction steps and expected/actual behavior fields.
- If the user mentions tests, include test target and success criteria.
- If the user mentions review, switch the final report to findings-first review format.
