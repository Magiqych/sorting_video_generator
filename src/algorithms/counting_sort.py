"""計数ソート (Counting Sort) の実装。

SortArray を使い、操作ごとにイベントを記録する。
非比較ソートで、値の出現回数を数えて overwrite で配列に書き戻す。
"""

from __future__ import annotations

from src.core.array import SortArray
from src.core.events import SortEvent


def counting_sort(values: list[int]) -> tuple[list[int], list[SortEvent]]:
    """計数ソートを実行し、ソート済み配列とイベント列を返す。

    各値の出現回数をカウントし、先頭から順に overwrite で書き戻す。
    比較ベースではないため compare / swap イベントは発生しない。

    Args:
        values: ソート対象の整数リスト（正の整数を想定）。

    Returns:
        (ソート済みリスト, イベント列) のタプル。
    """
    arr = SortArray(values)
    n = len(arr)

    if n <= 1:
        if n == 1:
            arr.mark_sorted(0)
        return arr.to_list(), arr.events()

    # ---- カウント ----
    min_val = min(values)
    max_val = max(values)
    count = [0] * (max_val - min_val + 1)
    for v in values:
        count[v - min_val] += 1

    # ---- 書き戻し ----
    idx = 0
    for val in range(min_val, max_val + 1):
        for _ in range(count[val - min_val]):
            arr.overwrite(idx, val)
            arr.mark_sorted(idx)
            idx += 1

    return arr.to_list(), arr.events()
