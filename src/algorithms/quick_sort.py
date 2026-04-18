"""クイックソートの実装。

SortArray を使い、操作ごとにイベントを記録する。
Lomuto パーティション方式を採用。
"""

from __future__ import annotations

from src.core.array import SortArray
from src.core.events import SortEvent


def quick_sort(values: list[int]) -> tuple[list[int], list[SortEvent]]:
    """クイックソートを実行し、ソート済み配列とイベント列を返す。

    Lomuto パーティションで末尾要素をピボットとして選択する。

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

    _quick_sort_recursive(arr, 0, n - 1)

    return arr.to_list(), arr.events()


def _quick_sort_recursive(arr: SortArray, low: int, high: int) -> None:
    """再帰的にクイックソートを実行する。"""
    if low >= high:
        if low == high:
            arr.mark_sorted(low)
        return

    pivot_idx = _partition(arr, low, high)
    arr.mark_sorted(pivot_idx)

    _quick_sort_recursive(arr, low, pivot_idx - 1)
    _quick_sort_recursive(arr, pivot_idx + 1, high)


def _partition(arr: SortArray, low: int, high: int) -> int:
    """Lomuto パーティション。arr[high] をピボットとする。

    Returns:
        ピボットの最終位置。
    """
    # ピボットは末尾要素
    i = low  # 次に小さい値を置く位置

    for j in range(low, high):
        if arr.compare(j, high) <= 0:
            if i != j:
                arr.swap(i, j)
            i += 1

    # ピボットを正しい位置に配置
    if i != high:
        arr.swap(i, high)

    return i
