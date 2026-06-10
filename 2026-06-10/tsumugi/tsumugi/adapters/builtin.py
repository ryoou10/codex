"""組み込みアダプタ(6サービス)。

役割分担:
  script    : Claude        - 脚本・ナレーション(長文推論)
  music     : Suno          - 楽曲(BPM・展開)
  video     : Seedance 2.0  - 映像(カット割り・色温度)
  keyvisual : TapNow        - キービジュアル(パレット)
  player    : ChatGPT Codex - 同期再生プレイヤーのコード生成
  release   : Hermes agent  - 公開前チェック・権利確認の実行計画

シミュレーションモードでは、ブループリントから決定論的に
マニフェストを導出する。意図的に「各AIが独立に解釈したズレ」
(感情ノイズ・テンポ非同期)を含めてあり、整合性エンジンの
修正指示(directives)を受けた再生成で収束する。これは実運用時の
「独立した生成AI同士は最初は揃わない」挙動の再現である。
"""

from __future__ import annotations

import hashlib

from ..blueprint import Blueprint, Mood
from . import Adapter, JobContext, register


def _noise(*key: object) -> float:
    """キーから決定論的に [-1, 1] の擬似ノイズを得る。"""
    digest = hashlib.sha256(":".join(str(k) for k in key).encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") / 0xFFFFFFFF * 2.0 - 1.0


def _clamp(value: float, lo: float, hi: float) -> float:
    return min(max(value, lo), hi)


def _noisy_mood(base: Mood, scale: float, *key: object) -> Mood:
    return Mood(
        valence=_clamp(base.valence + _noise(*key, "v") * scale, -1.0, 1.0),
        arousal=_clamp(base.arousal + _noise(*key, "a") * scale, 0.0, 1.0),
        tension=_clamp(base.tension + _noise(*key, "t") * scale, 0.0, 1.0),
    )


def _avg_arousal(bp: Blueprint) -> float:
    return sum(b.mood.arousal for b in bp.beats) / len(bp.beats)


def _avg_valence(bp: Blueprint) -> float:
    return sum(b.mood.valence for b in bp.beats) / len(bp.beats)


def _has_directive(ctx: JobContext, kind: str) -> dict | None:
    for d in ctx.directives:
        if d.get("type") == kind:
            return d
    return None


class ClaudeScriptAdapter(Adapter):
    role = "script"
    service = "Claude"
    api_key_env = "ANTHROPIC_API_KEY"

    def generate_simulated(self, ctx: JobContext) -> dict:
        bp = ctx.blueprint
        scenes = [
            {
                "beat_id": b.id,
                "at": b.at,
                "label": b.label,
                "text": f"【{b.label}】{b.description}(テーマ: {bp.theme})",
                "mood": b.mood.to_dict(),
            }
            for b in bp.beats
        ]
        return {
            "service": self.service,
            "logline": f"『{bp.title}』- {bp.theme} を {int(bp.duration_sec)}秒で描く。",
            "scenes": scenes,
        }


class SunoMusicAdapter(Adapter):
    role = "music"
    service = "Suno"
    api_key_env = "SUNO_API_KEY"

    def generate_simulated(self, ctx: JobContext) -> dict:
        bp = ctx.blueprint
        noise_scale = 0.0 if _has_directive(ctx, "emotion_align") else 0.25
        bpm = round(70 + 70 * _avg_arousal(bp) + _noise(self.role, bp.title, "bpm") * 8)
        sections = [
            {
                "at": b.at,
                "label": b.label,
                "instrumentation": "strings, piano" if b.mood.arousal < 0.5 else "full band, percussion",
                "mood": _noisy_mood(b.mood, noise_scale, self.role, bp.title, b.id).to_dict(),
            }
            for b in bp.beats
        ]
        return {
            "service": self.service,
            "bpm": bpm,
            "duration_sec": bp.duration_sec,
            "sections": sections,
            "prompt": f"{bp.theme}, {bpm} BPM, emotional arc following blueprint beats",
        }


class SeedanceVideoAdapter(Adapter):
    role = "video"
    service = "Seedance 2.0"
    api_key_env = "SEEDANCE_API_KEY"

    def generate_simulated(self, ctx: JobContext) -> dict:
        bp = ctx.blueprint
        noise_scale = 0.0 if _has_directive(ctx, "emotion_align") else 0.25
        sync = _has_directive(ctx, "tempo_sync")
        if sync:
            # 修正指示: 楽曲BPMに対し 8拍 = 1カットで同期させる
            cuts_per_min = sync["target_bpm"] / 8.0
        else:
            cuts_per_min = 4 + 20 * _avg_arousal(bp) + _noise(self.role, bp.title, "cuts") * 3
        scenes = []
        for b in bp.beats:
            mood = _noisy_mood(b.mood, noise_scale, self.role, bp.title, b.id)
            scenes.append(
                {
                    "at": b.at,
                    "prompt": f"{bp.theme} - {b.description}",
                    # 色温度は valence から導出(陽=暖色/低K、陰=寒色/高K)
                    "color_temp_k": round(6500 - 2500 * mood.valence),
                    "mood": mood.to_dict(),
                }
            )
        return {
            "service": self.service,
            "duration_sec": bp.duration_sec,
            "cuts_per_min": round(cuts_per_min, 2),
            "scenes": scenes,
        }


class TapNowKeyVisualAdapter(Adapter):
    role = "keyvisual"
    service = "TapNow"
    api_key_env = "TAPNOW_API_KEY"

    def generate_simulated(self, ctx: JobContext) -> dict:
        bp = ctx.blueprint
        expected_warm = (_avg_valence(bp) + 1.0) / 2.0
        if _has_directive(ctx, "palette_align"):
            warm_fraction = round(expected_warm, 3)
        else:
            warm_fraction = round(
                _clamp(expected_warm + _noise(self.role, bp.title, "warm") * 0.3, 0.0, 1.0), 3
            )
        return {
            "service": self.service,
            "prompt": f"key visual for '{bp.title}' - {bp.theme}",
            "warm_fraction": warm_fraction,
            "palette": ["#E8A87C", "#C38D9E", "#41B3A3"] if warm_fraction >= 0.5 else ["#2B6777", "#52AB98", "#C8D8E4"],
        }


class CodexPlayerAdapter(Adapter):
    role = "player"
    service = "ChatGPT Codex"
    api_key_env = "OPENAI_API_KEY"

    def generate_simulated(self, ctx: JobContext) -> dict:
        import html as html_mod
        import json

        from .player_template import PLAYER_TEMPLATE

        bp = ctx.blueprint
        cues = [
            {"at_sec": round(b.at * bp.duration_sec, 2), "label": b.label}
            for b in bp.beats
        ]
        data = {
            "title": bp.title,
            "theme": bp.theme,
            "duration_sec": bp.duration_sec,
            "beats": [b.to_dict() for b in bp.beats],
            "script": ctx.upstream.get("script", {"scenes": []}),
            "music": ctx.upstream.get("music", {}),
            "video": ctx.upstream.get("video", {}),
            "keyvisual": ctx.upstream.get("keyvisual", {"palette": []}),
        }
        # "</" を含む文字列で <script> ブロックが壊れないようにエスケープする
        data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        html = PLAYER_TEMPLATE.replace("__TITLE__", html_mod.escape(bp.title)).replace(
            "__DATA_JSON__", data_json
        )
        return {
            "service": self.service,
            "entry": "player.html",
            "cues": cues,
            "files": {"player.html": html},
        }


class HermesReleaseAdapter(Adapter):
    role = "release"
    service = "Hermes agent"
    api_key_env = "HERMES_API_KEY"

    def generate_simulated(self, ctx: JobContext) -> dict:
        rights_review = [
            {
                "artifact": role,
                "generated_by": manifest.get("service", "unknown"),
                "note": "公開前に当該サービスの利用規約・商用利用条件・クレジット表記要否を確認すること。",
            }
            for role, manifest in sorted(ctx.upstream.items())
        ]
        return {
            "service": self.service,
            "rights_review": rights_review,
            "checklist": [
                "来歴台帳(ledger.jsonl)の検証が PASS であること",
                "整合性レポートの総合スコアが基準値以上であること",
                "各生成AIサービスの利用規約上、成果物の公開・商用利用が許諾されていること",
                "実在の人物・既存著作物に類似した出力が含まれないこと",
                "AI生成物である旨の表示が必要なプラットフォームでは明記すること",
            ],
            "publish_steps": [
                "成果物一式をエクスポート",
                "プラットフォーム別メタデータを付与",
                "公開・告知",
            ],
        }


register(ClaudeScriptAdapter())
register(SunoMusicAdapter())
register(SeedanceVideoAdapter())
register(TapNowKeyVisualAdapter())
register(CodexPlayerAdapter())
register(HermesReleaseAdapter())
