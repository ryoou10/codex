---
name: prompt-writing-draft
description: Create copy-ready prompts for drafting new articles, blog posts, note posts, SNS posts, essays, and structured written content. Use this skill when the user asks for prompts about "記事作成", "ブログ", "note", "SNS投稿", "文章作成", "原稿", "構成案", or creating a new piece of writing from a rough idea. This skill is intentionally narrow and should not be used for improving an existing draft, research briefs, coding tasks, or workplace reports.
---

# Writing Draft Prompt Builder

Use this skill to create a copy-ready prompt that makes another AI produce a new piece of writing from a rough idea.

This skill has one use case: drafting new written content.

## Default Goal

Create a prompt that produces:

- audience-aware structure
- clear thesis or message
- tone and style constraints
- outline before draft when useful
- final draft
- title or headline candidates when relevant

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
あなたは、読者の関心と目的に合わせて構成から本文まで設計する編集者兼ライターです。

目的は、[テーマ]について、[読者]が最後まで読みやすく、読み終えた後に[期待する行動・理解]へ進める文章を作成することです。

テーマ:
- [書きたいテーマ]

想定読者:
- [読者像]

伝えたいこと:
- [主張、体験、学び、紹介したい内容]

制約条件:
- 言語: 日本語
- 媒体: [ブログ / note / SNS / メール / その他]
- トーン: [丁寧 / 親しみやすい / 専門的 / 熱量高めなど]
- 長さ: [文字数または目安]
- 避けること: [誇張、煽り、専門用語過多など]

作業手順:
1. 読者が知りたいことを整理してください。
2. 文章の主張と読後の到達点を明確にしてください。
3. 構成案を作ってください。
4. 構成に沿って本文を作成してください。
5. タイトル案を3つ出してください。

出力形式:
1. 想定読者
2. 主張
3. 構成案
4. 本文
5. タイトル案
6. 改善するとさらに良くなる点

品質チェック:
- 誰に向けた文章か明確か
- 冒頭で読む理由が伝わるか
- 話の流れに飛躍がないか
- 抽象論だけでなく具体例があるか
- 指定した媒体に合う長さとトーンか
```

## Strengthening Rules

- If the user gives no audience, assume a general reader and make it replaceable.
- If the user gives only a topic, add thesis, reader, and structure fields.
- If the user asks for SNS, make the prompt request multiple short variants.
