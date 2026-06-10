"""Conductor - パイプライン実行と修正ループ。

ステージ依存関係:
    script ─┬─ music ────┬─ player ── release
            ├─ video ────┤
            └─ keyvisual ┘

weave() は全ステージを実行してマニフェストと成果物を保存し、
来歴台帳に記録する。check() は整合性レポートを生成する。
weave(revise=True) は直前のレポートの修正指示を各アダプタに
渡して再生成する(整合ループの1反復)。
"""

from __future__ import annotations

import json
from pathlib import Path

from . import harmony
from .adapters import JobContext, get_adapter
from .blueprint import Blueprint
from .ledger import Ledger, sha256_text

STAGES = ["script", "music", "video", "keyvisual", "player", "release"]

BLUEPRINT_FILE = "blueprint.json"
ARTIFACTS_DIR = "artifacts"
LEDGER_FILE = "ledger.jsonl"
REPORT_FILE = "harmony_report.json"
STATE_FILE = "state.json"


class Project:
    def __init__(self, root: Path):
        self.root = Path(root)

    @property
    def blueprint_path(self) -> Path:
        return self.root / BLUEPRINT_FILE

    @property
    def artifacts_dir(self) -> Path:
        return self.root / ARTIFACTS_DIR

    @property
    def report_path(self) -> Path:
        return self.root / REPORT_FILE

    def ledger(self) -> Ledger:
        return Ledger(self.root / LEDGER_FILE)

    def blueprint(self) -> Blueprint:
        return Blueprint.load(self.blueprint_path)

    def state(self) -> dict:
        path = self.root / STATE_FILE
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return {"revision": -1}

    def save_state(self, state: dict) -> None:
        (self.root / STATE_FILE).write_text(
            json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def manifests(self) -> dict:
        manifests = {}
        if self.artifacts_dir.exists():
            for path in self.artifacts_dir.glob("*.json"):
                manifests[path.stem] = json.loads(path.read_text(encoding="utf-8"))
        return manifests

    def last_report(self) -> dict | None:
        if self.report_path.exists():
            return json.loads(self.report_path.read_text(encoding="utf-8"))
        return None


def init_project(root: Path, blueprint: Blueprint) -> Project:
    project = Project(root)
    project.root.mkdir(parents=True, exist_ok=False)
    project.artifacts_dir.mkdir()
    blueprint.save(project.blueprint_path)
    project.save_state({"revision": -1})
    return project


def weave(project: Project, revise: bool = False) -> dict:
    """全ステージを実行する。revise=True なら直前レポートの修正指示を適用。"""
    bp = project.blueprint()
    state = project.state()
    revision = state["revision"] + 1

    directives_by_role: dict[str, list] = {}
    if revise:
        report = project.last_report()
        if not report:
            raise RuntimeError("修正指示がありません。先に check を実行してください。")
        for check in report["checks"]:
            for d in check["directives"]:
                directives_by_role.setdefault(d["role"], []).append(d)

    manifests: dict[str, dict] = {}
    ledger = project.ledger()
    for role in STAGES:
        adapter = get_adapter(role)
        ctx = JobContext(
            blueprint=bp,
            revision=revision,
            upstream=dict(manifests),
            directives=directives_by_role.get(role, []),
        )
        manifest = adapter.generate(ctx)
        manifests[role] = manifest

        # マニフェスト本体を保存
        manifest_path = project.artifacts_dir / f"{role}.json"
        text = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        manifest_path.write_text(text, encoding="utf-8")
        ledger.append(
            role=role,
            service=adapter.service,
            live=adapter.is_live(),
            revision=revision,
            artifact_path=str(manifest_path.relative_to(project.root)),
            artifact_sha256=sha256_text(text),
        )

        # 付随ファイル(コード等)を保存
        for filename, content in manifest.get("files", {}).items():
            file_path = project.artifacts_dir / filename
            file_path.write_text(content, encoding="utf-8")
            ledger.append(
                role=role,
                service=adapter.service,
                live=adapter.is_live(),
                revision=revision,
                artifact_path=str(file_path.relative_to(project.root)),
                artifact_sha256=sha256_text(content),
            )

    project.save_state({"revision": revision})
    return manifests


def check(project: Project) -> harmony.HarmonyReport:
    """整合性を評価し、レポートを保存して返す。"""
    bp = project.blueprint()
    report = harmony.evaluate(bp, project.manifests())
    project.report_path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def weave_until_harmony(project: Project, max_iterations: int = 5) -> harmony.HarmonyReport:
    """生成→検証→修正指示→再生成 を収束まで繰り返す。"""
    weave(project)
    report = check(project)
    iterations = 1
    while not report.passed and iterations < max_iterations:
        weave(project, revise=True)
        report = check(project)
        iterations += 1
    return report
