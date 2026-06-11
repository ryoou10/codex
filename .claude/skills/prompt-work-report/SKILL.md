---
name: prompt-work-report
description: "業務報告・進捗共有用のプロンプトを作るスキル。 Create copy-ready prompts for workplace reports, status updates, handoffs, and internal sharing messages. Use this skill when the user asks for prompts about \"業務報告\", \"進捗報告\", \"上司への報告文\", \"共有文\", \"引き継ぎ\", \"今日やったことをまとめる\", or making work status clear for a supervisor or team. This skill is intentionally narrow and should not be used for research, public articles, coding tasks, or improvement proposals."
---

# Workplace Report Prompt Builder

Use this skill to create a copy-ready prompt that makes another AI produce a clear workplace report or internal status update.

This skill has one use case: turning rough work notes into a report that a supervisor or team member can quickly understand.

## Default Goal

Create a prompt that produces:

- what was done
- current status
- results or evidence
- blockers or risks
- next action
- decisions or confirmations needed

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
あなたは、現場の作業内容を上司や関係者に伝わる業務報告へ整理するビジネスコミュニケーション編集者です。

目的は、読み手が短時間で「何が終わったか」「今どこで止まっているか」「次に何を判断すべきか」を把握できる業務報告文を作成することです。

入力情報:
- 作業日: [日付]
- 報告先: [上司 / チーム / 関係者]
- 今日やったこと: [箇条書きで入力]
- 結果・数字・証拠: [分かる範囲で入力]
- 困っていること: [あれば入力]
- 次にやること: [分かる範囲で入力]

情報の扱い:
- 入力情報を事実として扱ってください。
- 不足情報は推測で断定せず、「未確認」または「確認が必要」としてください。
- 読み手が判断しやすい順番に並べ替えてください。

制約条件:
- 言語: 日本語
- トーン: 簡潔、丁寧、実務的
- 長さ: 300〜600字程度
- 避けること: 言い訳調、抽象的な頑張った報告、不要な感想

出力形式:
1. 件名
2. 本文
   - 要点
   - 実施内容
   - 結果
   - 課題・確認事項
   - 次のアクション
3. 必要なら、読み手に確認してほしいこと

品質チェック:
- 読み手が状況をすぐ理解できるか
- 完了、進行中、未着手が分かれているか
- 次の行動または判断点が明確か
- 事実と未確認事項が混ざっていないか
```

## Strengthening Rules

- If the user mentions a supervisor, prioritize decision points.
- If the user mentions handoff, prioritize next owner, deadline, and unresolved items.
- If the user mentions daily report, keep it concise and scannable.
