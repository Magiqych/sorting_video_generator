"""挿入ソートの実装。

SortArray を使い、操作ごとにイベントを記録する。
"""

from __future__ import annotations

from src.core.array import SortArray
from src.core.events import SortEvent


def insertion_sort(values: list[int]) -> tuple[list[int], list[SortEvent]]:
    """挿入ソートを実行し、ソート済み配列とイベント列を返す。

    先頭要素は整列済みとし、2 番目以降の要素を適切な位置に挿入していく。
    挿入位置を見つけるために隣接要素を比較し、必要なら swap で左にずらす。

    Args:
        values: ソート対象の整数リスト。

    Returns:
        (ソート済みリスト, イベント列) のタプル。
    """
    arr = SortArray(values)
    n = len(arr)

    if n > 0:
        arr.mark_sorted(0)

    for i in range(1, n):
        j = i
        while j > 0 and arr.compare(j - 1, j) > 0:
            arr.swap(j - 1, j)
            j -= 1
        arr.mark_sorted(i)

    return arr.to_list(), arr.events()
