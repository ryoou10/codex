"""TSUMUGI Web App - ブラウザから操作するローカルアプリ。

依存ライブラリなし(Python 標準ライブラリのみ)。

起動:
    python3 -m tsumugi.app --port 8765 --workspace ./tsumugi-workspace

セキュリティ:
    既定で 127.0.0.1 にのみバインドする(ローカル専用)。
    プロジェクト名は英数字・ハイフン・アンダースコアに制限し、
    成果物の配信はプロジェクトディレクトリ内に限定する。

API:
    GET  /api/projects                          プロジェクト一覧
    POST /api/projects                          作成 {name,title,theme,duration_sec}
    GET  /api/projects/<name>/blueprint         ブループリント取得
    PUT  /api/projects/<name>/blueprint         ブループリント保存
    POST /api/projects/<name>/weave             生成 {revise: bool}
    POST /api/projects/<name>/check             整合性検証
    POST /api/projects/<name>/auto              収束まで自動実行
    GET  /api/projects/<name>/report            直近レポート
    GET  /api/projects/<name>/artifacts         成果物一覧
    GET  /api/projects/<name>/artifacts/<file>  成果物本体
    GET  /api/projects/<name>/ledger            来歴台帳
    POST /api/projects/<name>/ledger/verify     台帳検証
"""

from __future__ import annotations

import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import conductor
from .blueprint import Blueprint, default_blueprint

NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
WEB_DIR = Path(__file__).parent / "web"

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
}


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


class Workspace:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def project_names(self) -> list[str]:
        return sorted(
            p.name
            for p in self.root.iterdir()
            if p.is_dir() and (p / conductor.BLUEPRINT_FILE).exists()
        )

    def project(self, name: str) -> conductor.Project:
        if not NAME_RE.match(name):
            raise ApiError(400, "プロジェクト名は英数字・ハイフン・アンダースコアのみ(64文字以内)")
        project = conductor.Project(self.root / name)
        if not project.blueprint_path.exists():
            raise ApiError(404, f"プロジェクトが存在しません: {name}")
        return project

    def create(self, name: str, title: str, theme: str, duration_sec: float) -> conductor.Project:
        if not NAME_RE.match(name):
            raise ApiError(400, "プロジェクト名は英数字・ハイフン・アンダースコアのみ(64文字以内)")
        if (self.root / name).exists():
            raise ApiError(409, f"既に存在します: {name}")
        if not title or not theme:
            raise ApiError(400, "title と theme は必須です")
        if not 1 <= float(duration_sec) <= 3600:
            raise ApiError(400, "duration_sec は 1〜3600 の範囲で指定してください")
        bp = default_blueprint(title, theme, float(duration_sec))
        return conductor.init_project(self.root / name, bp)


class Handler(BaseHTTPRequestHandler):
    workspace: Workspace  # serve() で設定する

    # ---- 低レベルヘルパ ----

    def log_message(self, fmt: str, *args) -> None:  # 静かに
        pass

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data: dict | list, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length == 0:
            return {}
        if length > 1_000_000:
            raise ApiError(413, "リクエストが大きすぎます")
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ApiError(400, f"JSON が不正です: {e}")

    # ---- ルーティング ----

    def _route(self, method: str) -> None:
        path = self.path.split("?", 1)[0]
        try:
            if path == "/" and method == "GET":
                self._serve_static("index.html")
                return
            parts = [p for p in path.split("/") if p]
            if parts[:1] != ["api"]:
                raise ApiError(404, "not found")
            self._route_api(method, parts[1:])
        except ApiError as e:
            self._json({"error": e.message}, e.status)
        except Exception as e:  # 想定外はメッセージのみ返す
            self._json({"error": f"{type(e).__name__}: {e}"}, 500)

    def _route_api(self, method: str, parts: list[str]) -> None:
        ws = self.workspace
        if parts == ["projects"]:
            if method == "GET":
                self._json([self._summary(ws.project(n)) for n in ws.project_names()])
                return
            if method == "POST":
                body = self._read_body()
                project = ws.create(
                    str(body.get("name", "")),
                    str(body.get("title", "")),
                    str(body.get("theme", "")),
                    float(body.get("duration_sec", 60)),
                )
                self._json(self._summary(project), 201)
                return
        if len(parts) >= 3 and parts[0] == "projects":
            project = ws.project(parts[1])
            self._route_project(method, project, parts[2:])
            return
        raise ApiError(404, "not found")

    def _route_project(self, method: str, project: conductor.Project, rest: list[str]) -> None:
        if rest == ["blueprint"]:
            if method == "GET":
                self._json(project.blueprint().to_dict())
                return
            if method == "PUT":
                bp = Blueprint.from_dict(self._read_body())  # from_dict が validate する
                bp.save(project.blueprint_path)
                self._json(bp.to_dict())
                return
        if rest == ["weave"] and method == "POST":
            revise = bool(self._read_body().get("revise", False))
            try:
                conductor.weave(project, revise=revise)
            except RuntimeError as e:
                raise ApiError(409, str(e))
            self._json({"revision": project.state()["revision"]})
            return
        if rest == ["check"] and method == "POST":
            self._json(conductor.check(project).to_dict())
            return
        if rest == ["auto"] and method == "POST":
            report = conductor.weave_until_harmony(project)
            self._json({"revision": project.state()["revision"], "report": report.to_dict()})
            return
        if rest == ["report"] and method == "GET":
            report = project.last_report()
            if report is None:
                raise ApiError(404, "レポートがありません。先に検証を実行してください。")
            self._json(report)
            return
        if rest == ["artifacts"] and method == "GET":
            files = []
            if project.artifacts_dir.exists():
                for p in sorted(project.artifacts_dir.iterdir()):
                    if p.is_file():
                        files.append({"name": p.name, "bytes": p.stat().st_size})
            self._json(files)
            return
        if len(rest) == 2 and rest[0] == "artifacts" and method == "GET":
            self._serve_artifact(project, rest[1])
            return
        if rest == ["ledger"] and method == "GET":
            self._json(project.ledger().entries())
            return
        if rest == ["ledger", "verify"] and method == "POST":
            ok, message = project.ledger().verify()
            self._json({"ok": ok, "message": message})
            return
        raise ApiError(404, "not found")

    # ---- 配信 ----

    def _summary(self, project: conductor.Project) -> dict:
        bp = project.blueprint()
        report = project.last_report()
        return {
            "name": project.root.name,
            "title": bp.title,
            "theme": bp.theme,
            "duration_sec": bp.duration_sec,
            "revision": project.state()["revision"],
            "score": report["score"] if report else None,
            "passed": report["passed"] if report else None,
        }

    def _serve_artifact(self, project: conductor.Project, filename: str) -> None:
        target = (project.artifacts_dir / filename).resolve()
        if target.parent != project.artifacts_dir.resolve() or not target.is_file():
            raise ApiError(404, "成果物が見つかりません")
        content_type = CONTENT_TYPES.get(target.suffix, "application/octet-stream")
        self._send(200, target.read_bytes(), content_type)

    def _serve_static(self, filename: str) -> None:
        target = (WEB_DIR / filename).resolve()
        if target.parent != WEB_DIR.resolve() or not target.is_file():
            raise ApiError(404, "not found")
        content_type = CONTENT_TYPES.get(target.suffix, "application/octet-stream")
        self._send(200, target.read_bytes(), content_type)

    # ---- HTTP メソッド ----

    def do_GET(self) -> None:
        self._route("GET")

    def do_POST(self) -> None:
        self._route("POST")

    def do_PUT(self) -> None:
        self._route("PUT")


def serve(workspace: Path, host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    """サーバーを生成して返す(serve_forever は呼び出し側で)。"""
    handler = type("BoundHandler", (Handler,), {"workspace": Workspace(workspace)})
    return ThreadingHTTPServer((host, port), handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tsumugi-app", description="TSUMUGI Web App")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--workspace", default="./tsumugi-workspace")
    args = parser.parse_args(argv)
    server = serve(Path(args.workspace), args.host, args.port)
    print(f"TSUMUGI app: http://{args.host}:{server.server_address[1]}/")
    print(f"workspace : {Path(args.workspace).resolve()}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
