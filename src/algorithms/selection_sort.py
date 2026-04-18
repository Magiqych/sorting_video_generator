"""選択ソートの実装。

SortArray を使い、操作ごとにイベントを記録する。
"""

from __future__ import annotations

from src.core.array import SortArray
from src.core.events import SortEvent


def selection_sort(values: list[int]) -> tuple[list[int], list[SortEvent]]:
    """選択ソートを実行し、ソート済み配列とイベント列を返す。

    各パスで未ソート部分の最小値を見つけ、先頭と交換する。
    交換後に確定した要素に mark_sorted を付与する。

    Args:
        values: ソート対象の整数リスト。

    Returns:
        (ソート済みリスト, イベント列) のタプル。
    """
    arr = SortArray(values)
    n = len(arr)

    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            if arr.compare(min_idx, j) > 0:
                min_idx = j
        if min_idx != i:
            arr.swap(i, min_idx)
        arr.mark_sorted(i)

    # 最後の要素も整列済み
    if n > 0:
        arr.mark_sorted(n - 1)

    return arr.to_list(), arr.events()
