"""アダプタ基盤。

各生成AIサービスへの接続は Adapter として抽象化する。
- 対応する API キーが環境変数に無い場合は常にオフラインの
  シミュレーションモードで動作する(構造化された指示書/マニフェスト
  を決定論的に生成し、パイプライン全体を実機なしで検証できる)。
- 実サービスへの接続は各アダプタの `generate_live()` に実装する。
  本リポジトリでは未実装であり、呼び出すと明示的なエラーになる。
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ..blueprint import Blueprint


@dataclass
class JobContext:
    """1回の生成ジョブに渡されるコンテキスト。"""

    blueprint: Blueprint
    revision: int = 0
    # 先行ステージの成果物(role -> manifest dict)
    upstream: dict = field(default_factory=dict)
    # 整合性チェックが出した修正指示(このアダプタ宛てのもの)
    directives: list = field(default_factory=list)


class Adapter(ABC):
    """生成AIサービス1つ分の接続。"""

    #: パイプライン上の役割名(例: "music")
    role: str = ""
    #: 接続先サービス名(例: "Suno")
    service: str = ""
    #: 実接続に必要な環境変数名
    api_key_env: str = ""

    def is_live(self) -> bool:
        return bool(self.api_key_env and os.environ.get(self.api_key_env))

    def generate(self, ctx: JobContext) -> dict:
        """マニフェスト(構造化された成果物記述)を返す。"""
        if self.is_live():
            return self.generate_live(ctx)
        return self.generate_simulated(ctx)

    @abstractmethod
    def generate_simulated(self, ctx: JobContext) -> dict:
        """オフラインシミュレーション。決定論的であること。"""

    def generate_live(self, ctx: JobContext) -> dict:
        raise NotImplementedError(
            f"{self.service} への実接続は未実装です。"
            f" {type(self).__name__}.generate_live() に公式APIクライアントを実装してください。"
        )


_REGISTRY: dict[str, Adapter] = {}


def register(adapter: Adapter) -> Adapter:
    _REGISTRY[adapter.role] = adapter
    return adapter


def get_adapter(role: str) -> Adapter:
    if role not in _REGISTRY:
        raise KeyError(f"unknown adapter role: {role}")
    return _REGISTRY[role]


def all_adapters() -> dict[str, Adapter]:
    return dict(_REGISTRY)


# 組み込みアダプタを登録する
from . import builtin  # noqa: E402,F401
