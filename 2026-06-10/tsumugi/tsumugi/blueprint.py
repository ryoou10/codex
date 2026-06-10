"""Creative Blueprint - 全モダリティが従う単一の作品仕様。

ブループリントは「感情の時間軸(ビート列)」を中核に持つ。
各ビートは正規化時刻 at(0.0〜1.0)と感情ベクトル mood を持ち、
音楽の展開・映像のカット・ビジュアルの色調はすべてこの曲線に
従うことが要求される。整合性の判定基準そのものでもある。
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

MOOD_AXES = ("valence", "arousal", "tension")


@dataclass(frozen=True)
class Mood:
    """感情ベクトル。

    valence: -1.0(陰)〜 1.0(陽)
    arousal:  0.0(静)〜 1.0(動)
    tension:  0.0(弛緩)〜 1.0(緊張)
    """

    valence: float
    arousal: float
    tension: float

    def __post_init__(self) -> None:
        if not -1.0 <= self.valence <= 1.0:
            raise ValueError(f"valence out of range: {self.valence}")
        for axis in ("arousal", "tension"):
            value = getattr(self, axis)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{axis} out of range: {value}")

    def as_vector(self) -> tuple[float, float, float]:
        return (self.valence, self.arousal, self.tension)

    def similarity(self, other: "Mood") -> float:
        """コサイン類似度。ゼロベクトル同士は 1.0、片方のみゼロは 0.0。"""
        a, b = self.as_vector(), other.as_vector()
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0.0 and norm_b == 0.0:
            return 1.0
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        return dot / (norm_a * norm_b)

    def to_dict(self) -> dict:
        return {"valence": self.valence, "arousal": self.arousal, "tension": self.tension}

    @classmethod
    def from_dict(cls, data: dict) -> "Mood":
        return cls(**{axis: float(data[axis]) for axis in MOOD_AXES})


@dataclass(frozen=True)
class Beat:
    """物語上の1拍。正規化時刻 at における目標感情を定義する。"""

    id: str
    at: float
    label: str
    description: str
    mood: Mood

    def __post_init__(self) -> None:
        if not 0.0 <= self.at <= 1.0:
            raise ValueError(f"beat {self.id}: at must be 0.0-1.0, got {self.at}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "at": self.at,
            "label": self.label,
            "description": self.description,
            "mood": self.mood.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Beat":
        return cls(
            id=data["id"],
            at=float(data["at"]),
            label=data["label"],
            description=data["description"],
            mood=Mood.from_dict(data["mood"]),
        )


@dataclass
class Blueprint:
    """作品全体の仕様。全アダプタへの指示書はここから導出される。"""

    title: str
    theme: str
    duration_sec: float
    language: str = "ja"
    beats: list[Beat] = field(default_factory=list)

    def validate(self) -> None:
        if self.duration_sec <= 0:
            raise ValueError("duration_sec must be positive")
        if len(self.beats) < 2:
            raise ValueError("blueprint needs at least 2 beats (start and end)")
        ats = [b.at for b in self.beats]
        if ats != sorted(ats):
            raise ValueError("beats must be ordered by 'at'")
        if len({b.id for b in self.beats}) != len(self.beats):
            raise ValueError("beat ids must be unique")
        if ats[0] != 0.0:
            raise ValueError("first beat must be at 0.0")

    def mood_at(self, at: float) -> Mood:
        """任意の正規化時刻における目標感情(ビート間は線形補間)。"""
        at = min(max(at, 0.0), 1.0)
        beats = self.beats
        if at <= beats[0].at:
            return beats[0].mood
        for prev, nxt in zip(beats, beats[1:]):
            if at <= nxt.at:
                span = nxt.at - prev.at
                t = 0.0 if span == 0 else (at - prev.at) / span
                return Mood(
                    valence=prev.mood.valence + t * (nxt.mood.valence - prev.mood.valence),
                    arousal=prev.mood.arousal + t * (nxt.mood.arousal - prev.mood.arousal),
                    tension=prev.mood.tension + t * (nxt.mood.tension - prev.mood.tension),
                )
        return beats[-1].mood

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "theme": self.theme,
            "duration_sec": self.duration_sec,
            "language": self.language,
            "beats": [b.to_dict() for b in self.beats],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Blueprint":
        bp = cls(
            title=data["title"],
            theme=data["theme"],
            duration_sec=float(data["duration_sec"]),
            language=data.get("language", "ja"),
            beats=[Beat.from_dict(b) for b in data["beats"]],
        )
        bp.validate()
        return bp

    def save(self, path: Path) -> None:
        path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> "Blueprint":
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))


def default_blueprint(title: str, theme: str, duration_sec: float) -> Blueprint:
    """標準的な起承転結カーブを持つ雛形。生成後にユーザーが編集する想定。"""
    beats = [
        Beat("ki", 0.0, "起", "静かな導入。世界観の提示。", Mood(0.1, 0.2, 0.2)),
        Beat("sho", 0.35, "承", "展開。期待感が高まる。", Mood(0.4, 0.5, 0.4)),
        Beat("ten", 0.7, "転", "クライマックス。感情の頂点。", Mood(0.7, 0.9, 0.8)),
        Beat("ketsu", 1.0, "結", "解放と余韻。", Mood(0.6, 0.3, 0.1)),
    ]
    bp = Blueprint(title=title, theme=theme, duration_sec=duration_sec, beats=beats)
    bp.validate()
    return bp
