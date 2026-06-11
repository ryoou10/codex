---
name: prompt-business-improvement
description: "上司に出せる業務改善提案用のプロンプトを作るスキル。 Create copy-ready prompts for supervisor-ready business improvement proposals. Use this skill when the user asks for prompts about \"上司に出す業務改善案\", \"業務改善\", \"改善提案\", \"現場業務のムダ削減\", \"A4 1枚で提案\", \"上司が判断できる資料\", \"Copilot導入の効果を示す\", or daily workplace improvement prompt creation. This skill is intentionally narrow and should not be used for general writing, research, coding, or visual prompts."
---

# Business Improvement Prompt Builder

Use this skill to create a copy-ready prompt that makes another AI produce a supervisor-ready business improvement proposal.

This skill is intentionally narrow. It should optimize for one repeated workflow: turning rough workplace pain points into a concise proposal that a supervisor can review, judge, and approve or reject.

## Default Goal

Create a prompt that produces an improvement proposal with:

- current problem
- cause or bottleneck
- proposed improvement
- expected effect
- required preparation
- risks and countermeasures
- first small experiment
- decision points for the supervisor

## Input Handling

If the user gives only a rough request, proceed with assumptions. Do not ask a long questionnaire.

Ask at most one question only when the missing answer changes the proposal substantially, such as:

- the target business process is unknown
- the proposal reader is not a supervisor or manager
- there are strict workplace compliance limits

Otherwise, include replaceable fields in the final prompt.

## Output Format

Always respond in this structure:

```markdown
## 完成プロンプト

```text
[copy-ready prompt]
```

## 補った条件

- ...

## 使う前に差し替える箇所

- ...

## 追加すると精度が上がる情報

- ...
```

If there are no required replacements, write:

```text
差し替え必須の箇所はありません。
```

## Prompt Requirements

The completed prompt must include:

- a specific role, not just "professional"
- a concrete objective tied to supervisor decision-making
- assumptions and replaceable fields
- constraints for concise Japanese business writing
- an output structure suitable for review
- a quality checklist
- instructions to separate facts, assumptions, and proposals
- a small first experiment, preferably within one week

## Copy-Ready Prompt Template

Adapt this template to the user's situation.

```text
あなたは、現場業務の課題を整理し、上司が判断しやすい改善提案に落とし込む業務改善コンサルタントです。

目的は、上司が5分で「何が問題か」「何を変えるのか」「どの程度の効果が見込めるのか」「まず承認すべき小さな実験は何か」を判断できる業務改善案を作成することです。

前提・背景:
- 対象業務: [対象業務を入力]
- 現在困っていること: [困りごとを入力]
- 現在の作業手順: [分かる範囲で入力]
- 使えるツール・環境: [Excel、メール、社内システム、Copilotなど]
- 制約: [予算、人員、権限、期限、禁止事項など]

情報の扱い:
- 私が入力した内容を事実として扱ってください。
- 不足情報は作業を止めず、合理的な仮定を置いてください。
- 事実、仮定、提案を混同せず、必要に応じて明示してください。

制約条件:
- 言語: 日本語
- 読者: 忙しい上司
- トーン: 簡潔、実務的、提案型
- 長さ: A4 1枚相当
- 避けること: 抽象論、精神論、根拠のない断定、大規模投資ありきの提案
- 優先すること: 小さく試せる改善、判断しやすい効果、現場で実行できる手順

出力形式:
1. 要約
   - 3行以内で、問題・改善案・期待効果を示してください。
2. 現状の課題
   - 作業のどこに時間、手戻り、ミス、属人化があるかを整理してください。
3. 改善案
   - 何を変えるのか、誰が何をするのかを具体化してください。
4. 期待効果
   - 時間削減、ミス削減、確認負荷削減、判断速度向上などの観点で示してください。
   - 数値が不明な場合は、仮定を置いて概算してください。
5. 必要な準備
   - 使う資料、ツール、関係者、初期設定を示してください。
6. リスクと対策
   - 起こり得る問題と、その回避策を示してください。
7. まず1週間で試す小さな実験
   - すぐ試せる範囲に絞ってください。
8. 上司に判断してほしいこと
   - 承認、相談、確認、保留の判断点を明確にしてください。

品質チェック:
- 上司が次の判断をしやすい内容になっているか
- 現場で最初に試す行動が明確か
- 効果と手間のバランスが分かるか
- 事実、仮定、提案が混ざっていないか
- 抽象的な便利さではなく、業務上の変化として説明できているか
```

## Strengthening Rules

When the user's request is vague, add these defaults:

- Reader: busy supervisor
- Length: A4 one-page equivalent
- First experiment: one week
- Tone: concise and practical
- Success state: supervisor can decide whether to approve a small trial

When the user mentions AI tools such as Copilot, add:

- compare current manual workflow with AI-assisted workflow
- show a small measurable proof point
- avoid claiming broad transformation before proving value
- include a short logging plan for before/after comparison

## Weak-To-Strong Transformations

Weak:

```text
あなたは業務改善のプロです。業務改善案を作ってください。
```

Strong:

```text
あなたは、現場業務の課題を整理し、上司が判断しやすい改善提案に落とし込む業務改善コンサルタントです。目的は、上司が5分で小さな実験の承認可否を判断できる改善案を作成することです。
```
