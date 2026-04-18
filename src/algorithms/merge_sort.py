"""マージソートの実装。

SortArray を使い、操作ごとにイベントを記録する。
ボトムアップではなくトップダウン（再帰）方式で実装し、
merge 時に compare と overwrite イベントを記録する。
"""

from __future__ import annotations

from src.core.array import SortArray
from src.core.events import SortEvent


def merge_sort(values: list[int]) -> tuple[list[int], list[SortEvent]]:
    """マージソートを実行し、ソート済み配列とイベント列を返す。

    トップダウン再帰で分割し、マージ時に compare/overwrite を記録する。

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

    _merge_sort_recursive(arr, 0, n - 1)

    for i in range(n):
        arr.mark_sorted(i)

    return arr.to_list(), arr.events()


def _merge_sort_recursive(arr: SortArray, left: int, right: int) -> None:
    """再帰的にマージソートを実行する。"""
    if left >= right:
        return

    mid = (left + right) // 2
    _merge_sort_recursive(arr, left, mid)
    _merge_sort_recursive(arr, mid + 1, right)
    _merge(arr, left, mid, right)


def _merge(arr: SortArray, left: int, mid: int, right: int) -> None:
    """arr[left..mid] と arr[mid+1..right] をマージする。

    一時バッファに値を退避し、比較しながら overwrite で書き戻す。
    比較はバッファの値で行う（配列は overwrite で更新中のため）。
    """
    # 一時バッファに現在の値をコピー
    left_buf = [arr[i] for i in range(left, mid + 1)]
    right_buf = [arr[i] for i in range(mid + 1, right + 1)]

    i = 0  # left_buf のインデックス
    j = 0  # right_buf のインデックス
    k = left  # 書き込み先

    while i < len(left_buf) and j < len(right_buf):
        # バッファの値で比較（配列は overwrite 中なので直接比較できない）
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
