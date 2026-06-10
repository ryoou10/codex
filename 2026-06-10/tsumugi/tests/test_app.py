"""Web アプリ(API)のテスト。実サーバーをスレッドで起動して検証する。"""

import json
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tsumugi.app import serve  # noqa: E402


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.server = serve(Path(cls.tmp.name), port=0)  # 空きポートに自動割当
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.tmp.cleanup()

    def request(self, method, path, body=None):
        req = urllib.request.Request(
            self.base + path,
            method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req) as res:
                return res.status, json.loads(res.read().decode())
        except urllib.error.HTTPError as e:
            payload = e.read().decode()
            try:
                return e.code, json.loads(payload)
            except json.JSONDecodeError:
                return e.code, {"raw": payload}

    def test_full_workflow(self):
        # 作成
        status, p = self.request("POST", "/api/projects", {
            "name": "trial", "title": "黎明", "theme": "夜明けの街", "duration_sec": 60,
        })
        self.assertEqual(status, 201)
        self.assertEqual(p["title"], "黎明")

        # 一覧に出る
        status, projects = self.request("GET", "/api/projects")
        self.assertIn("trial", [x["name"] for x in projects])

        # ブループリント取得・編集・保存
        status, bp = self.request("GET", "/api/projects/trial/blueprint")
        self.assertEqual(status, 200)
        bp["beats"][0]["mood"]["valence"] = -0.2
        status, saved = self.request("PUT", "/api/projects/trial/blueprint", bp)
        self.assertEqual(status, 200)
        self.assertEqual(saved["beats"][0]["mood"]["valence"], -0.2)

        # 自動収束
        status, result = self.request("POST", "/api/projects/trial/auto")
        self.assertEqual(status, 200)
        self.assertTrue(result["report"]["passed"])

        # レポート・成果物・台帳
        status, report = self.request("GET", "/api/projects/trial/report")
        self.assertTrue(report["passed"])
        status, files = self.request("GET", "/api/projects/trial/artifacts")
        self.assertIn("player.html", [f["name"] for f in files])
        status, verify = self.request("POST", "/api/projects/trial/ledger/verify")
        self.assertTrue(verify["ok"])

    def test_invalid_project_name_rejected(self):
        status, body = self.request("POST", "/api/projects", {
            "name": "../escape", "title": "t", "theme": "t", "duration_sec": 60,
        })
        self.assertEqual(status, 400)

    def test_duplicate_rejected(self):
        self.request("POST", "/api/projects", {
            "name": "dup", "title": "t", "theme": "t", "duration_sec": 60,
        })
        status, _ = self.request("POST", "/api/projects", {
            "name": "dup", "title": "t", "theme": "t", "duration_sec": 60,
        })
        self.assertEqual(status, 409)

    def test_missing_project_404(self):
        status, _ = self.request("GET", "/api/projects/nothing/blueprint")
        self.assertEqual(status, 404)

    def test_invalid_blueprint_rejected(self):
        self.request("POST", "/api/projects", {
            "name": "badbp", "title": "t", "theme": "t", "duration_sec": 60,
        })
        _, bp = self.request("GET", "/api/projects/badbp/blueprint")
        bp["beats"] = bp["beats"][:1]  # ビート1つは validate で拒否される
        status, body = self.request("PUT", "/api/projects/badbp/blueprint", bp)
        self.assertEqual(status, 500)
        self.assertIn("error", body)

    def test_artifact_traversal_blocked(self):
        self.request("POST", "/api/projects", {
            "name": "trav", "title": "t", "theme": "t", "duration_sec": 60,
        })
        self.request("POST", "/api/projects/trav/weave", {})
        status, _ = self.request("GET", "/api/projects/trav/artifacts/..%2Fblueprint.json")
        self.assertEqual(status, 404)

    def test_revise_without_report_conflict(self):
        self.request("POST", "/api/projects", {
            "name": "norep", "title": "t", "theme": "t", "duration_sec": 60,
        })
        status, _ = self.request("POST", "/api/projects/norep/weave", {"revise": True})
        self.assertEqual(status, 409)

    def test_index_served(self):
        with urllib.request.urlopen(self.base + "/") as res:
            self.assertEqual(res.status, 200)
            self.assertIn("TSUMUGI", res.read().decode())


if __name__ == "__main__":
    unittest.main()
