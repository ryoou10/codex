---
name: youtube-yoga-notifier
description: Use this skill whenever the user asks for recurring YouTube yoga video recommendations, yoga reminder automations, fixed-time morning/evening yoga notifications, or A/B/C yoga pattern selection. It creates or maintains a fixed-time thread notification workflow that recommends 9 public YouTube yoga videos as 3 body-part patterns with 3 videos per pattern.
---

# YouTube Yoga Notifier

Use this skill to create, repair, or run the user's recurring YouTube yoga video recommendation workflow.

## Core Schedule

Keep the visible notification times fixed:

- Morning notification: Asia/Tokyo `7:00`
- Evening notification: Asia/Tokyo `18:50`
- Destination: the current Codex thread unless the user explicitly asks otherwise

If the automation system cannot express two exact wall-clock times in one thread heartbeat, use an internal quiet-check schedule and strict notification guards:

- Run internal checks every 1 minute.
- Notify only during `7:00-7:09` or `18:50-18:59` Asia/Tokyo.
- For all other heartbeat executions, return `DONT_NOTIFY` and do not show user-facing prose.
- Do not emit duplicate morning or evening yoga notifications for the same local date.

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
- URLs already verified and used in this thread
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

<heartbeat>
  <automation_id>7-15</automation_id>
  <decision>NOTIFY</decision>
  <message>朝ヨガ候補を9本提示しました。</message>
</heartbeat>
```

For quiet checks, output only:

```xml
<heartbeat>
  <automation_id>7-15</automation_id>
  <decision>DONT_NOTIFY</decision>
  <message>[short reason]</message>
</heartbeat>
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

## Automation Maintenance

When creating or repairing the automation:

1. Search for `automation_update` if the tool is not available.
2. Prefer updating automation id `7-15` instead of creating duplicates.
3. Keep the automation active.
4. Use a thread heartbeat destination.
5. Use `FREQ=MINUTELY;INTERVAL=1` only as an internal quiet-check mechanism.
6. Put the fixed visible notification times in the prompt as hard guards: `7:00-7:09` and `18:50-18:59` Asia/Tokyo.
7. After updating, verify the local automation file parses as TOML and contains:
   - `status = "ACTIVE"`
   - `RRULE:FREQ=MINUTELY;INTERVAL=1`
   - morning-only notify guard
   - evening-only notify guard
   - duplicate-prevention language

## A/B/C Pattern Replies

If the user replies `A`, `B`, or `C` after a yoga notification:

- Treat it as the selected pattern for that notification.
- Return only the 3 videos from that pattern.
- Do not claim to write to YouTube watch history.
- Explain briefly that YouTube watch history updates when the user opens and watches the videos while logged in.
