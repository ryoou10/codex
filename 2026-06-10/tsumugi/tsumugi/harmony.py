"""Harmony Engine - クロスモーダル整合性の検証と修正指示の生成。

各モダリティのマニフェストをブループリントと相互に突き合わせ、
  1. duration   : 音楽・映像の尺がブループリントと一致するか
  2. tempo_sync : 楽曲BPMと映像のカット間隔が音楽的に同期するか
                  (1カットあたりの拍数が4拍=1小節の倍数に乗るか)
  3. emotion    : 各モダリティが報告する感情曲線がブループリントの
                  感情曲線とどれだけ一致するか(コサイン類似度)
  4. palette    : ビジュアルの暖色比率が作品全体の valence と整合するか
を採点する。不合格の項目には、該当アダプタ宛ての修正指示
(directive)を生成する。これが再生成ループの入力になる。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .blueprint import Blueprint, Mood

DURATION_TOLERANCE = 0.02
TEMPO_TOLERANCE = 0.05
EMOTION_THRESHOLD = 0.95
PALETTE_TOLERANCE = 0.15
PASS_SCORE = 0.95


@dataclass
class Check:
    name: str
    score: float  # 0.0 - 1.0
    passed: bool
    detail: str
    directives: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "score": round(self.score, 4),
            "passed": self.passed,
            "detail": self.detail,
            "directives": self.directives,
        }


@dataclass
class HarmonyReport:
    checks: list[Check]

    @property
    def score(self) -> float:
        if not self.checks:
            return 0.0
        return sum(c.score for c in self.checks) / len(self.checks)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks) and self.score >= PASS_SCORE

    def directives_for(self, role: str) -> list[dict]:
        return [
            d
            for c in self.checks
            for d in c.directives
            if d.get("role") == role
        ]

    def to_dict(self) -> dict:
        return {
            "score": round(self.score, 4),
            "passed": self.passed,
            "checks": [c.to_dict() for c in self.checks],
        }


def _check_duration(bp: Blueprint, manifests: dict) -> list[Check]:
    checks = []
    for role in ("music", "video"):
        manifest = manifests.get(role)
        if not manifest:
            continue
        actual = float(manifest.get("duration_sec", 0))
        error = abs(actual - bp.duration_sec) / bp.duration_sec
        passed = error <= DURATION_TOLERANCE
        directives = []
        if not passed:
            directives.append(
                {
                    "role": role,
                    "type": "duration_fix",
                    "target_sec": bp.duration_sec,
                    "reason": f"尺が {actual}s(目標 {bp.duration_sec}s、誤差 {error:.1%})",
                }
            )
        checks.append(
            Check(
                name=f"duration:{role}",
                score=max(0.0, 1.0 - error),
                passed=passed,
                detail=f"{role} の尺 {actual}s / 目標 {bp.duration_sec}s",
                directives=directives,
            )
        )
    return checks


def _check_tempo_sync(manifests: dict) -> list[Check]:
    music = manifests.get("music")
    video = manifests.get("video")
    if not music or not video:
        return []
    bpm = float(music["bpm"])
    cpm = float(video["cuts_per_min"])
    if cpm <= 0:
        return [
            Check(
                name="tempo_sync",
                score=0.0,
                passed=False,
                detail="映像のカットレートが不正",
                directives=[{"role": "video", "type": "tempo_sync", "target_bpm": bpm}],
            )
        ]
    beats_per_cut = bpm / cpm
    # 1カットあたりの拍数が 1小節(4拍)の倍数に乗っているか
    nearest_bar_multiple = max(4.0, round(beats_per_cut / 4.0) * 4.0)
    error = abs(beats_per_cut - nearest_bar_multiple) / nearest_bar_multiple
    passed = error <= TEMPO_TOLERANCE
    directives = []
    if not passed:
        directives.append(
            {
                "role": "video",
                "type": "tempo_sync",
                "target_bpm": bpm,
                "reason": (
                    f"1カット {beats_per_cut:.2f}拍は小節境界({nearest_bar_multiple:.0f}拍)から"
                    f" {error:.1%} ズレている"
                ),
            }
        )
    return [
        Check(
            name="tempo_sync",
            score=max(0.0, 1.0 - error),
            passed=passed,
            detail=f"BPM {bpm} / {cpm} cuts/min = {beats_per_cut:.2f} 拍/カット",
            directives=directives,
        )
    ]


def _emotion_points(manifest: dict) -> list[tuple[float, Mood]]:
    points = []
    for entry in manifest.get("sections", []) + manifest.get("scenes", []):
        if "mood" in entry and "at" in entry:
            points.append((float(entry["at"]), Mood.from_dict(entry["mood"])))
    return points


def _check_emotion(bp: Blueprint, manifests: dict) -> list[Check]:
    checks = []
    for role in ("music", "video"):
        manifest = manifests.get(role)
        if not manifest:
            continue
        points = _emotion_points(manifest)
        if not points:
            checks.append(
                Check(
                    name=f"emotion:{role}",
                    score=0.0,
                    passed=False,
                    detail=f"{role} が感情情報を報告していない",
                    directives=[{"role": role, "type": "emotion_align", "reason": "感情情報の欠落"}],
                )
            )
            continue
        sims = [bp.mood_at(at).similarity(mood) for at, mood in points]
        avg = sum(sims) / len(sims)
        passed = avg >= EMOTION_THRESHOLD
        directives = []
        if not passed:
            worst_at = points[sims.index(min(sims))][0]
            directives.append(
                {
                    "role": role,
                    "type": "emotion_align",
                    "reason": f"感情曲線の平均一致度 {avg:.3f}(最不一致点 at={worst_at})",
                }
            )
        checks.append(
            Check(
                name=f"emotion:{role}",
                score=avg,
                passed=passed,
                detail=f"{role} の感情曲線一致度 {avg:.3f}(閾値 {EMOTION_THRESHOLD})",
                directives=directives,
            )
        )
    return checks


def _check_palette(bp: Blueprint, manifests: dict) -> list[Check]:
    manifest = manifests.get("keyvisual")
    if not manifest:
        return []
    avg_valence = sum(b.mood.valence for b in bp.beats) / len(bp.beats)
    expected_warm = (avg_valence + 1.0) / 2.0
    actual_warm = float(manifest.get("warm_fraction", 0.5))
    error = abs(actual_warm - expected_warm)
    passed = error <= PALETTE_TOLERANCE
    directives = []
    if not passed:
        directives.append(
            {
                "role": "keyvisual",
                "type": "palette_align",
                "target_warm_fraction": round(expected_warm, 3),
                "reason": f"暖色比率 {actual_warm}(期待値 {expected_warm:.3f})",
            }
        )
    return [
        Check(
            name="palette",
            score=max(0.0, 1.0 - error),
            passed=passed,
            detail=f"暖色比率 {actual_warm} / 期待値 {expected_warm:.3f}(valence平均 {avg_valence:.2f})",
            directives=directives,
        )
    ]


def evaluate(bp: Blueprint, manifests: dict) -> HarmonyReport:
    """全チェックを実行し、レポートと修正指示を返す。"""
    checks: list[Check] = []
    checks += _check_duration(bp, manifests)
    checks += _check_tempo_sync(manifests)
    checks += _check_emotion(bp, manifests)
    checks += _check_palette(bp, manifests)
    return HarmonyReport(checks=checks)
