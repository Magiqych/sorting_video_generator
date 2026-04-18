"""ソートイベントの型定義。

ソートアルゴリズムの各操作を統一的なイベントとして表現する。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EventType(Enum):
    """ソート操作のイベント種別。"""

    COMPARE = "compare"
    SWAP = "swap"
    OVERWRITE = "overwrite"
    MARK_SORTED = "mark_sorted"
    SHUFFLE = "shuffle"


@dataclass(frozen=True, slots=True)
class SortEvent:
    """ソート操作 1 ステップを表すイベント。

    Attributes:
        type: イベント種別。
        step: 0 始まりの連番。
        indices: 操作対象のインデックス群。
        values: 操作に関連する値群。不要な場合は空タプル。
        meta: 任意の付加情報。
    """

    type: EventType
    step: int
    indices: tuple[int, ...]
    values: tuple[int, ...] = ()
    meta: dict[str, object] | None = field(default=None, repr=False)
