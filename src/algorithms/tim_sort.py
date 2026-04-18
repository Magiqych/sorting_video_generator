"""TimSort の実装。

SortArray を使い、操作ごとにイベントを記録する。
挿入ソートでランを整列し、マージで結合するハイブリッドアルゴリズム。
"""

from __future__ import annotations

from src.core.array import SortArray
from src.core.events import SortEvent

MIN_RUN = 4


def tim_sort(values: list[int]) -> tuple[list[int], list[SortEvent]]:
    """TimSort を実行し、ソート済み配列とイベント列を返す。

    小さなランを挿入ソートで整列し、ボトムアップでマージする。

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

    # ---- 各ランを挿入ソートで整列 ----
    for start in range(0, n, MIN_RUN):
        end = min(start + MIN_RUN - 1, n - 1)
        _insertion_sort_run(arr, start, end)

    # ---- ボトムアップマージ ----
    size = MIN_RUN
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(left + size - 1, n - 1)
            right = min(left + 2 * size - 1, n - 1)
            if mid < right:
                _merge(arr, left, mid, right)
        size *= 2

    for i in range(n):
        arr.mark_sorted(i)

    return arr.to_list(), arr.events()


def _insertion_sort_run(arr: SortArray, left: int, right: int) -> None:
    """arr[left..right] を挿入ソートで整列する。"""
    for i in range(left + 1, right + 1):
        j = i
        while j > left and arr.compare(j - 1, j) > 0:
            arr.swap(j - 1, j)
            j -= 1


def _merge(arr: SortArray, left: int, mid: int, right: int) -> None:
    """arr[left..mid] と arr[mid+1..right] をマージする。

    一時バッファに値を退避し、overwrite で書き戻す。
    """
    left_buf = [arr[i] for i in range(left, mid + 1)]
    right_buf = [arr[i] for i in range(mid + 1, right + 1)]

    i = 0
    j = 0
    k = left

    while i < len(left_buf) and j < len(right_buf):
        if left_buf[i] <= right_buf[j]:
            arr.overwrite(k, left_buf[i])
            i += 1
        else:
            arr.overwrite(k, right_buf[j])
            j += 1
        k += 1

    while i < len(left_buf):
        arr.overwrite(k, left_buf[i])
        i += 1
        k += 1

    while j < len(right_buf):
        arr.overwrite(k, right_buf[j])
        j += 1
        k += 1
