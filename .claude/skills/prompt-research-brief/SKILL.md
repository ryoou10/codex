---
name: prompt-research-brief
description: Create copy-ready prompts for source-aware research briefs, comparisons, and investigation summaries. Use this skill when the user asks for prompts about "調査", "リサーチ", "比較", "市場調査", "最新情報", "根拠付きでまとめる", "メリット・デメリット", or decision-ready research. This skill is intentionally narrow and should not be used for writing drafts, coding tasks, or workplace reports.
---

# Research Brief Prompt Builder

Use this skill to create a copy-ready prompt that makes another AI produce a research brief or comparison summary.

This skill has one use case: turning a question into a structured, source-aware research output.

## Default Goal

Create a prompt that produces:

- research question
- scope and exclusions
- current-source verification when needed
- key findings
- comparison table when relevant
- implications
- open questions
- source list or evidence notes

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
あなたは、意思決定に使える調査ブリーフを作成するリサーチアナリストです。

目的は、[調査テーマ]について、読み手が判断に使える形で重要情報、比較、示唆、未確認点を整理することです。

調査テーマ:
- [調査したいこと]

想定読者:
- [上司 / 自分 / チーム / 顧客など]

調査範囲:
- 含めること: [範囲]
- 除外すること: [範囲外]
- 地域・期間・対象: [必要に応じて入力]

情報の扱い:
- 事実、解釈、推測を分けてください。
- 最新性が重要な情報は、現在の情報源で確認してください。
- 情報源が確認できない内容は断定せず、「未確認」と明示してください。
- 可能なら一次情報または公式情報を優先してください。

制約条件:
- 言語: 日本語
- トーン: 中立、簡潔、実務的
- 長さ: 重要度順に要約し、必要以上に長くしない

出力形式:
1. 要約
2. 調査範囲
3. 主要な結論
4. 根拠・情報源
5. 比較表
6. 判断に使える示唆
7. リスク・注意点
8. 追加で確認すべきこと

品質チェック:
- 調査テーマに直接答えているか
- 事実と解釈が分かれているか
- 古い情報を最新情報として扱っていないか
- 判断に必要な比較軸が含まれているか
- 根拠が弱い点を明示しているか
```

## Strengthening Rules

- If the user says "最新", include current-source verification.
- If the user says "比較", force a comparison table with criteria.
- If the user asks for recommendations, separate findings from recommendation.
