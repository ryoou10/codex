"""TSUMUGI のユニットテスト(標準ライブラリのみで実行可能)。

実行: python -m unittest discover -s tests -v
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tsumugi import conductor  # noqa: E402
from tsumugi.blueprint import Blueprint, Mood, default_blueprint  # noqa: E402
from tsumugi.ledger import Ledger  # noqa: E402


class MoodTests(unittest.TestCase):
    def test_similarity_identical(self):
        m = Mood(0.5, 0.5, 0.5)
        self.assertAlmostEqual(m.similarity(m), 1.0)

    def test_similarity_orthogonal(self):
        a = Mood(1.0, 0.0, 0.0)
        b = Mood(0.0, 1.0, 0.0)
        self.assertAlmostEqual(a.similarity(b), 0.0)

    def test_range_validation(self):
        with self.assertRaises(ValueError):
            Mood(2.0, 0.0, 0.0)
        with self.assertRaises(ValueError):
            Mood(0.0, -0.1, 0.0)


class BlueprintTests(unittest.TestCase):
    def test_default_blueprint_valid(self):
        bp = default_blueprint("T", "テーマ", 60)
        bp.validate()
        self.assertEqual(len(bp.beats), 4)

    def test_mood_interpolation(self):
        bp = default_blueprint("T", "テーマ", 60)
        # 起(at=0, arousal=0.2)と承(at=0.35, arousal=0.5)の中間
        mid = bp.mood_at(0.175)
        self.assertAlmostEqual(mid.arousal, 0.35, places=4)

    def test_roundtrip(self):
        bp = default_blueprint("T", "テーマ", 60)
        bp2 = Blueprint.from_dict(bp.to_dict())
        self.assertEqual(bp.to_dict(), bp2.to_dict())

    def test_validation_rejects_unordered_beats(self):
        bp = default_blueprint("T", "テーマ", 60)
        bp.beats = list(reversed(bp.beats))
        with self.assertRaises(ValueError):
            bp.validate()


class PipelineTests(unittest.TestCase):
    def _make_project(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        bp = default_blueprint("黎明", "夜明けの街と一杯の珈琲", 60)
        return conductor.init_project(Path(tmp.name) / "proj", bp)

    def test_weave_produces_all_stages(self):
        project = self._make_project()
        manifests = conductor.weave(project)
        self.assertEqual(set(manifests), set(conductor.STAGES))
        # プレイヤーコードが成果物として書き出される
        self.assertTrue((project.artifacts_dir / "player.html").exists())

    def test_player_is_self_contained_preview(self):
        """プレイヤーはマニフェスト埋め込み済みで、音と映像を自前合成できること。"""
        project = self._make_project()
        manifests = conductor.weave(project)
        html = (project.artifacts_dir / "player.html").read_text(encoding="utf-8")
        self.assertIn("AudioContext", html)          # 音声合成
        self.assertIn("getContext", html)            # 映像合成
        self.assertIn(str(manifests["music"]["bpm"]), html)  # マニフェスト埋め込み
        self.assertNotIn("__DATA_JSON__", html)      # プレースホルダ置換済み
        self.assertNotIn('src="music.mp3"', html)    # 外部ファイル非依存

    def test_harmony_loop_converges(self):
        project = self._make_project()
        report = conductor.weave_until_harmony(project, max_iterations=5)
        self.assertTrue(report.passed, msg=json.dumps(report.to_dict(), ensure_ascii=False))

    def test_first_pass_is_imperfect(self):
        """独立生成された初回出力は完全には揃わない(修正ループの存在意義)。"""
        project = self._make_project()
        conductor.weave(project)
        report = conductor.check(project)
        self.assertLess(report.score, 1.0)

    def test_directives_target_failing_roles(self):
        project = self._make_project()
        conductor.weave(project)
        report = conductor.check(project)
        for check in report.checks:
            for d in check.directives:
                self.assertIn(d["role"], conductor.STAGES)

    def test_release_includes_rights_review(self):
        project = self._make_project()
        manifests = conductor.weave(project)
        reviewed = {r["artifact"] for r in manifests["release"]["rights_review"]}
        # release は自分より前の全ステージの権利確認項目を持つ
        self.assertEqual(reviewed, set(conductor.STAGES) - {"release"})


class LedgerTests(unittest.TestCase):
    def test_chain_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.jsonl")
            for i in range(3):
                ledger.append(
                    role="music",
                    service="Suno",
                    live=False,
                    revision=i,
                    artifact_path=f"artifacts/music{i}.json",
                    artifact_sha256="0" * 64,
                )
            ok, _ = ledger.verify()
            self.assertTrue(ok)

    def test_tampering_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            ledger = Ledger(path)
            for i in range(3):
                ledger.append(
                    role="video",
                    service="Seedance 2.0",
                    live=False,
                    revision=i,
                    artifact_path=f"artifacts/video{i}.json",
                    artifact_sha256="0" * 64,
                )
            lines = path.read_text(encoding="utf-8").splitlines()
            entry = json.loads(lines[1])
            entry["service"] = "改竄"
            lines[1] = json.dumps(entry, ensure_ascii=False)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            ok, message = ledger.verify()
            self.assertFalse(ok)
            self.assertIn("entry 1", message)

    def test_pipeline_ledger_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            bp = default_blueprint("T", "テーマ", 60)
            project = conductor.init_project(Path(tmp) / "proj", bp)
            conductor.weave_until_harmony(project)
            ok, _ = project.ledger().verify()
            self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
