---
name: prompt-architect
description: "プロンプト作成依頼を最適な子スキルへ振り分ける親スキル。 Route prompt-creation requests to the most specific prompt-building child skill, then ensure the final prompt is copy-ready. Use this skill whenever the user asks for prompt creation, prompt refinement, prompt wall-bouncing, \"プロンプト作成\", \"壁打ち\", \"一度で質のいい条件\", \"あなたは〇〇に特化した〇〇のプロフェッショナルです\", or wants a prompt that makes ChatGPT or Codex produce a target output. This is the parent router skill; prefer a narrower child skill whenever one matches the requested prompt type."
---

# Prompt Architect

Use this as the parent router for prompt-building work. Its job is to classify the user's rough objective and route it to the narrowest matching child skill.

Do not turn this parent into a universal prompt-writing template. Add or use one focused child skill per repeated use case.

## Current Structure

```text
prompt-architect
├── prompt-business-improvement
├── prompt-work-report
├── prompt-research-brief
├── prompt-writing-draft
├── prompt-codex-task
└── prompt-revision-request
```

## Routing Rules

1. Identify the target deliverable the user wants another AI to produce.
2. Route to the child skill tied to that deliverable.
3. Prefer the narrowest match over a broader category.
4. If the request could match multiple child skills, choose by final output:
   - improvement proposal -> `prompt-business-improvement`
   - workplace report or status update -> `prompt-work-report`
   - research brief or comparison -> `prompt-research-brief`
   - article, post, essay, or general draft -> `prompt-writing-draft`
   - Codex coding task -> `prompt-codex-task`
   - improve an existing draft/output/prompt -> `prompt-revision-request`
5. Ask at most one question only when no route can be inferred.
6. If no child skill exists, propose a new child skill scope instead of forcing a generic answer.

## Child Skill Map

### `prompt-business-improvement`

Use for supervisor-ready business improvement proposal prompts.

Triggers:

- 上司に出す業務改善案
- 改善提案
- 現場業務のムダ削減
- A4 1枚で上司に見せる
- Copilot導入の効果を上司に示す

### `prompt-work-report`

Use for workplace report, status update, handoff, and internal sharing prompts.

Triggers:

- 業務報告
- 進捗報告
- 上司への報告文
- 共有文
- 引き継ぎ
- 今日やったことをまとめる

### `prompt-research-brief`

Use for source-aware research brief and comparison prompts.

Triggers:

- 調査して
- 比較して
- リサーチ
- 市場調査
- 最新情報を確認
- 根拠付きでまとめる

### `prompt-writing-draft`

Use for prompts that create a new piece of writing from scratch.

Triggers:

- 記事作成
- ブログ
- note
- SNS投稿
- 文章作成
- 構成案
- 原稿

### `prompt-codex-task`

Use for prompts that ask Codex to inspect, change, test, or explain code.

Triggers:

- Codexに頼む
- バグ修正
- 実装依頼
- リファクタ
- テスト追加
- 既存コードを見て

### `prompt-revision-request`

Use for prompts that improve an existing draft, output, prompt, proposal, or message.

Triggers:

- 改善して
- 添削して
- ブラッシュアップ
- リライト
- もっと良くする
- 既存文を直す
- プロンプトを改善

## Parent Response Format

When a child skill matches, respond with the child skill's final output. Keep routing notes short.

```markdown
## 使用するスキル

- [child skill name]

## 理由

- [short reason]

[child skill output]
```

When no child skill exists yet:

```markdown
## 判定

- 作成すべき子スキル: [proposed child skill name]
- 対象用途: [single use case]
- 理由: [why it should be separate]

## 子スキル案

- 入力:
- 出力:
- 成功条件:
- トリガー語:
```

## Quality Gate

Before finalizing, check:

- The selected child skill has exactly one main use case.
- The final prompt is copy-ready for ChatGPT or Codex.
- The prompt includes role, objective, context, inputs, constraints, output format, quality criteria, and missing-information handling.
- The response avoids returning to a vague "you are a professional" pattern.
- The user can reuse the same prompt shape without a long wall-bouncing session.
