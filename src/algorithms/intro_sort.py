"""イントロソート (Introsort) の実装。

SortArray を使い、操作ごとにイベントを記録する。
クイックソートをベースに、再帰深度が 2*floor(log2(n)) を超えたら
ヒープソートに切り替え、小さいパーティションには挿入ソートを使う
ハイブリッドアルゴリズム。
"""

from __future__ import annotations

import math

from src.core.array import SortArray
from src.core.events import SortEvent

_INSERTION_THRESHOLD = 16


def intro_sort(values: list[int]) -> tuple[list[int], list[SortEvent]]:
    """イントロソートを実行し、ソート済み配列とイベント列を返す。

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

    max_depth = 2 * math.floor(math.log2(n))
    _introsort_recursive(arr, 0, n - 1, max_depth)

    return arr.to_list(), arr.events()


def _introsort_recursive(
    arr: SortArray, low: int, high: int, depth_limit: int,
) -> None:
    """再帰的にイントロソートを実行する。"""
    size = high - low + 1

    if size <= 1:
        if size == 1:
            arr.mark_sorted(low)
        return

    if size <= _INSERTION_THRESHOLD:
        _insertion_sort_range(arr, low, high)
        for i in range(low, high + 1):
            arr.mark_sorted(i)
        return

    if depth_limit == 0:
        _heapsort_range(arr, low, high)
        for i in range(low, high + 1):
            arr.mark_sorted(i)
        return

    pivot_idx = _partition(arr, low, high)
    arr.mark_sorted(pivot_idx)

    _introsort_recursive(arr, low, pivot_idx - 1, depth_limit - 1)
    _introsort_recursive(arr, pivot_idx + 1, high, depth_limit - 1)


def _partition(arr: SortArray, low: int, high: int) -> int:
    """Lomuto パーティション。arr[high] をピボットとする。"""
    i = low
    for j in range(low, high):
        if arr.compare(j, high) <= 0:
            if i != j:
                arr.swap(i, j)
            i += 1
    if i != high:
        arr.swap(i, high)
    return i


def _insertion_sort_range(arr: SortArray, low: int, high: int) -> None:
    """arr[low..high] を挿入ソートで整列する。"""
    for i in range(low + 1, high + 1):
        j = i
        while j > low and arr.compare(j - 1, j) > 0:
            arr.swap(j - 1, j)
            j -= 1


def _heapsort_range(arr: SortArray, low: int, high: int) -> None:
    """arr[low..high] をヒープソートで整列する。"""
    size = high - low + 1

    def sift_down(root: int, heap_size: int) -> None:
        while True:
            largest = root
            left = 2 * (root - low) + 1 + low
            right = 2 * (root - low) + 2 + low

            if left < low + heap_size and arr.compare(left, largest) > 0:
                largest = left
            if right < low + heap_size and arr.compare(right, largest) > 0:
                largest = right
            if largest == root:
                break
            arr.swap(root, largest)
            root = largest

    # ヒープ構築
    for i in range(low + size // 2 - 1, low - 1, -1):
        sift_down(i, size)

    # ソート
    for end in range(high, low, -1):
        arr.swap(low, end)
        sift_down(low, end - low)
