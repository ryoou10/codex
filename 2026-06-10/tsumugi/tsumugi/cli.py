"""TSUMUGI CLI.

使い方:
    python -m tsumugi.cli new <dir> --title 題名 --theme テーマ --duration 60
    python -m tsumugi.cli weave <dir> [--revise]
    python -m tsumugi.cli check <dir>
    python -m tsumugi.cli auto <dir>          # 収束するまで生成と検証を繰り返す
    python -m tsumugi.cli report <dir>
    python -m tsumugi.cli verify <dir>        # 来歴台帳の検証
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import conductor
from .blueprint import default_blueprint


def _print_report(report_dict: dict) -> None:
    status = "PASS" if report_dict["passed"] else "FAIL"
    print(f"総合スコア: {report_dict['score']:.4f} [{status}]")
    for check in report_dict["checks"]:
        mark = "o" if check["passed"] else "x"
        print(f"  [{mark}] {check['name']:<16} {check['score']:.4f}  {check['detail']}")
        for d in check["directives"]:
            print(f"      -> 修正指示 ({d['role']}): {d.get('reason', d['type'])}")


def cmd_new(args: argparse.Namespace) -> int:
    bp = default_blueprint(args.title, args.theme, args.duration)
    project = conductor.init_project(Path(args.project), bp)
    print(f"プロジェクトを作成しました: {project.root}")
    print(f"ブループリント({project.blueprint_path})を編集してから weave を実行してください。")
    return 0


def cmd_weave(args: argparse.Namespace) -> int:
    project = conductor.Project(Path(args.project))
    manifests = conductor.weave(project, revise=args.revise)
    revision = project.state()["revision"]
    print(f"revision {revision}: {len(manifests)} ステージを生成しました。")
    for role, manifest in manifests.items():
        print(f"  - {role:<10} ({manifest.get('service', '?')})")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    project = conductor.Project(Path(args.project))
    report = conductor.check(project)
    _print_report(report.to_dict())
    return 0 if report.passed else 1


def cmd_auto(args: argparse.Namespace) -> int:
    project = conductor.Project(Path(args.project))
    report = conductor.weave_until_harmony(project, max_iterations=args.max_iterations)
    revision = project.state()["revision"]
    print(f"{revision + 1} 回の生成で終了。")
    _print_report(report.to_dict())
    return 0 if report.passed else 1


def cmd_report(args: argparse.Namespace) -> int:
    project = conductor.Project(Path(args.project))
    report = project.last_report()
    if not report:
        print("レポートがありません。先に check を実行してください。", file=sys.stderr)
        return 1
    _print_report(report)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    project = conductor.Project(Path(args.project))
    ok, message = project.ledger().verify()
    print(f"来歴台帳: {'PASS' if ok else 'FAIL'} ({message})")
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tsumugi", description="Cross-Modal Consistency Orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("new", help="プロジェクトを作成")
    p.add_argument("project")
    p.add_argument("--title", required=True)
    p.add_argument("--theme", required=True)
    p.add_argument("--duration", type=float, default=60.0, help="秒")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("weave", help="全ステージを生成")
    p.add_argument("project")
    p.add_argument("--revise", action="store_true", help="直前レポートの修正指示を適用")
    p.set_defaults(func=cmd_weave)

    p = sub.add_parser("check", help="整合性を検証")
    p.add_argument("project")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("auto", help="収束するまで生成と検証を繰り返す")
    p.add_argument("project")
    p.add_argument("--max-iterations", type=int, default=5)
    p.set_defaults(func=cmd_auto)

    p = sub.add_parser("report", help="直近の整合性レポートを表示")
    p.add_argument("project")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("verify", help="来歴台帳を検証")
    p.add_argument("project")
    p.set_defaults(func=cmd_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
