---
name: prompt-revision-request
description: "既存の文章・成果物の改善依頼用プロンプトを作るスキル。 Create copy-ready prompts for improving an existing draft, output, prompt, proposal, message, or document. Use this skill when the user asks for prompts about \"改善して\", \"添削して\", \"ブラッシュアップ\", \"リライト\", \"もっと良くする\", \"既存文を直す\", \"出力を改善\", \"プロンプトを改善\", or making an existing artifact clearer, stronger, shorter, more persuasive, or more professional. This skill is intentionally narrow and should not be used to create a new draft from scratch."
---

# Revision Request Prompt Builder

Use this skill to create a copy-ready prompt that asks another AI to improve an existing artifact.

This skill has one use case: revision of something that already exists.

## Default Goal

Create a prompt that produces:

- diagnosis of current weaknesses
- revised version
- explanation of major changes
- optional alternatives
- quality checklist

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
あなたは、既存の文章・プロンプト・提案・メッセージを目的に合わせて改善する編集者兼レビュアーです。

目的は、以下の既存内容を、[改善したい方向性]に合わせて、より伝わりやすく、使いやすく、目的達成に近い形へ改善することです。

既存内容:
[ここに改善したい文章・プロンプト・出力を貼り付け]

改善したい方向性:
- [分かりやすくしたい / 短くしたい / 説得力を上げたい / 上司向けにしたい / 条件を強くしたい / など]

想定読者・利用先:
- [誰に見せるか / どこで使うか]

制約条件:
- 言語: 日本語
- 元の意図は残す
- 不要な情報は削る
- 変更理由が分かるようにする
- 事実を勝手に追加しない

作業手順:
1. 既存内容の目的、読者、弱点を整理してください。
2. 改善方針を3〜5点で示してください。
3. 改善版を作成してください。
4. 変更した主な点を簡潔に説明してください。
5. さらに良くするために必要な追加情報があれば示してください。

出力形式:
1. 診断
2. 改善方針
3. 改善版
4. 主な変更点
5. 追加すると精度が上がる情報

品質チェック:
- 元の目的を保っているか
- 読者に合わせた表現になっているか
- 不要な情報を増やしていないか
- 具体性、構成、トーンが改善されているか
- 変更理由が分かるか
```

## Strengthening Rules

- If the user says "短く", prioritize compression and remove repetition.
- If the user says "上司向け", prioritize decision points and business tone.
- If the user says "プロンプト改善", prioritize role, objective, constraints, output format, and quality criteria.
