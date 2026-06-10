"""Provenance Ledger - ハッシュチェーン式の来歴台帳。

「どの成果物を・どのAIサービスが・どの指示で・いつ生成したか」を
追記専用の JSONL に記録する。各エントリは直前エントリのハッシュを
含むため、後からの改竄・差し替えは verify() で検出できる。

権利処理(各サービスの利用規約確認、AI生成物の表示義務への対応)の
根拠資料として使うことを想定している。
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

GENESIS = "0" * 64


def _entry_hash(entry: dict) -> str:
    payload = {k: v for k, v in entry.items() if k != "entry_hash"}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class Ledger:
    def __init__(self, path: Path):
        self.path = path

    def _entries(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [
            json.loads(line)
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def append(
        self,
        *,
        role: str,
        service: str,
        live: bool,
        revision: int,
        artifact_path: str,
        artifact_sha256: str,
    ) -> dict:
        entries = self._entries()
        prev_hash = entries[-1]["entry_hash"] if entries else GENESIS
        entry = {
            "seq": len(entries),
            "ts": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "service": service,
            "live": live,
            "revision": revision,
            "artifact_path": artifact_path,
            "artifact_sha256": artifact_sha256,
            "prev_hash": prev_hash,
        }
        entry["entry_hash"] = _entry_hash(entry)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def verify(self) -> tuple[bool, str]:
        """チェーン全体を検証する。(ok, message) を返す。"""
        entries = self._entries()
        prev_hash = GENESIS
        for i, entry in enumerate(entries):
            if entry.get("seq") != i:
                return False, f"entry {i}: seq mismatch"
            if entry.get("prev_hash") != prev_hash:
                return False, f"entry {i}: broken chain (prev_hash mismatch)"
            if _entry_hash(entry) != entry.get("entry_hash"):
                return False, f"entry {i}: content tampered (entry_hash mismatch)"
            prev_hash = entry["entry_hash"]
        return True, f"{len(entries)} entries verified"

    def entries(self) -> list[dict]:
        return self._entries()
