# Skill Routing Reminder

このプロジェクトには `.claude/skills/` にカスタムスキルがある。依頼内容が以下のいずれかに該当する場合は、必ず該当スキルの `SKILL.md` を読み、その手順に従うこと。

- プロンプト作成・壁打ち → `prompt-architect` で分類し、子スキル1つに絞る（`prompt-business-improvement` / `prompt-work-report` / `prompt-research-brief` / `prompt-writing-draft` / `prompt-codex-task` / `prompt-revision-request`）
- 画像生成・画像プロンプト → `visual-prompt-designer`（プロンプト精錬）→ `imagegen-auto-director`（スペック化・生成）。X (Twitter) 向けは `x-viral-image-director`
- 小説・ライトノベル・物語・プロット・世界観・キャラクター設定 → `light-novel-creator`
- ヨガ動画レコメンド・朝ヨガ・夜ヨガ → `youtube-yoga-notifier`
- X (Twitter) API 操作・投稿・検索・DM → `xurl`
- スキルの作成・改善・評価 → `skill-creator`

該当しない場合は通常どおり対応してよい。詳細なルーティングは `CLAUDE.md` セクション9を参照。
