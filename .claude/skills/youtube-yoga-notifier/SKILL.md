---
name: youtube-yoga-notifier
description: "朝・夜の定時YouTubeヨガ動画レコメンドスキル(3部位×3本=9本構成)。 Use this skill whenever the user asks for recurring YouTube yoga video recommendations, yoga reminder automations, fixed-time morning/evening yoga notifications, or A/B/C yoga pattern selection. It creates or maintains a fixed-time notification workflow that recommends 9 public YouTube yoga videos as 3 body-part patterns with 3 videos per pattern."
---

# YouTube Yoga Notifier

Use this skill to create, repair, or run the user's recurring YouTube yoga video recommendation workflow.

## Core Schedule

Keep the visible notification times fixed:

- Morning notification: Asia/Tokyo `7:00`
- Evening notification: Asia/Tokyo `18:50`
- Destination: the current Claude Code session unless the user explicitly asks otherwise

## Scheduling On Claude Code

Claude Code skills cannot schedule themselves. Choose the mechanism that fits the environment:

- On demand: when the user asks for a morning or evening set, produce the matching notification immediately using the current Asia/Tokyo date.
- Recurring inside a session: if the harness offers a recurring-run capability (such as a `/loop` command or scheduled triggers), run a check on an interval and emit a notification only inside the `7:00-7:09` or `18:50-18:59` Asia/Tokyo windows. Outside those windows, do nothing and produce no user-facing prose.
- Recurring outside Claude Code: suggest cron or launchd on the user's machine to start a session or send a reminder at the fixed times.

Never emit duplicate morning or evening yoga notifications for the same local date.

## Recommendation Rules

Every notification must contain exactly 9 videos:

- 3 body-part patterns
- 3 videos per pattern
- Each pattern must focus on one body area only

Channel diversity:

- Do not rely only on B-Life, B-Flow, or any single channel.
- Include videos from other public yoga or stretch channels whenever verified URLs are available.
- In each 9-video notification, use at least 3 distinct channels whenever possible.
- Prefer no more than 3 videos from the same channel in one notification.
- If live search is unavailable and the pre-verified pool is channel-skewed, still avoid using a single channel for all 9 videos whenever any verified non-B-Life or non-B-Flow URLs are available.

Valid structure:

- Pattern A: neck and shoulders, 3 videos
- Pattern B: hips and pelvis, 3 videos
- Pattern C: lower back, 3 videos

Invalid structure:

- Pattern A: legs, back, neck mixed in one pattern

Use public YouTube videos. Do not depend on the user's YouTube account, subscriptions, watch history, or private data.

Do not invent URLs. Use only:

- Search results that can be verified during the current run
- URLs already verified and used in this session
- The pre-verified pool below

## Time-Specific Content

Morning notifications:

- Title as `朝ヨガ候補 YYYY-MM-DD（曜）`
- Target total time: 20-30 minutes per selected pattern
- Prefer 8-12 minutes per video
- Use energizing, posture-reset, mobility, or gentle wake-up videos

Evening notifications:

- Title as `夜ヨガ候補 YYYY-MM-DD（曜）`
- Target total time: 30-45 minutes per selected pattern
- Prefer 10-15 minutes per video
- Prefer relaxing, recovery, sleep-prep, stretch-heavy videos
- Keep the body-part consistency rule above all other content preferences

## Output Format

Use this structure:

```markdown
朝ヨガ候補 YYYY-MM-DD（曜）

**パターンA：[部位] 約[合計時間]分**

1. [タイトル](URL)
   チャンネル名 | 目安時間 | 選んだ理由

...

今日のおすすめは **パターンX：[部位]** です。[短い理由]
```

## Pre-Verified Candidate Pool

Use these when live search is slow or unreliable. Rotate choices when possible, while keeping body-part consistency and avoiding duplicate URLs inside one notification. Do not let this pool override the channel diversity rules above.

### Neck And Shoulders

- https://youtu.be/jLZHZnlHjFc
- https://youtu.be/4L9c972FRYc
- https://youtu.be/Pwn3PZZ9754
- https://youtu.be/iF6kEb32ajI
- https://youtu.be/fypCTSbsscU

### Shoulders And Back

- https://youtu.be/1RP7DZH28Cg
- https://youtu.be/kVpvhgWbRdo
- https://youtu.be/7Gm6KkTrHN0
- https://youtu.be/A22Qhp6APt8
- https://youtu.be/CgYd8LHn8MA

### Hips And Pelvis

- https://youtu.be/qqfTG6mpX0E
- https://youtu.be/UvWXo-1bJvw
- https://youtu.be/TyNH1CweC_M
- https://youtu.be/XGzvp5R2kZ8
- https://youtu.be/vEBVtOpTBhw

### Lower Back

- https://youtu.be/GISUPMLKtak
- https://youtu.be/wOhJ4UJzn-U
- https://youtu.be/zCHw2fWcnw4

### Core

- https://youtu.be/iDExNhTqads
- https://youtu.be/pIjgh6PxFd8
- https://youtu.be/ghRcigrapwo

## A/B/C Pattern Replies

If the user replies `A`, `B`, or `C` after a yoga notification:

- Treat it as the selected pattern for that notification.
- Return only the 3 videos from that pattern.
- Do not claim to write to YouTube watch history.
- Explain briefly that YouTube watch history updates when the user opens and watches the videos while logged in.
