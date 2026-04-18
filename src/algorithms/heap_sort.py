"""ヒープソートの実装。

SortArray を使い、操作ごとにイベントを記録する。
最大ヒープ (max-heap) で昇順ソートを行う。
"""

from __future__ import annotations

from src.core.array import SortArray
from src.core.events import SortEvent


def heap_sort(values: list[int]) -> tuple[list[int], list[SortEvent]]:
    """ヒープソートを実行し、ソート済み配列とイベント列を返す。

    最大ヒープを構築し、先頭要素を末尾に移動していくことで昇順にソートする。

    Args:
        values: ソート対象の整数リスト。

    Returns:
        (ソート済みリスト, イベント列) のタプル。
    """
    arr = SortArray(values)
    n = len(arr)

    if n <= 1:
        if n == 1:
            arr.mark_sorted(0)
        return arr.to_list(), arr.events()

    # ---- ヒープ構築 (heapify) ----
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(arr, i, n)

    # ---- ソート: 最大値を末尾に移動して縮小 ----
    for end in range(n - 1, 0, -1):
        arr.swap(0, end)
        arr.mark_sorted(end)
        _sift_down(arr, 0, end)

    arr.mark_sorted(0)

    return arr.to_list(), arr.events()


def _sift_down(arr: SortArray, root: int, size: int) -> None:
    """root を起点にヒープ条件を回復する (sift-down)。"""
    while True:
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2

        if left < size and arr.compare(left, largest) > 0:
            largest = left

        if right < size and arr.compare(right, largest) > 0:
            largest = right

        if largest == root:
            break

        arr.swap(root, largest)
        root = largest
