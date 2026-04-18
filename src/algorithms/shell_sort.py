"""シェルソートの実装。

SortArray を使い、操作ごとにイベントを記録する。
ギャップ列は Knuth の数列 (1, 4, 13, 40, ...) を使用する。
"""

from __future__ import annotations

from src.core.array import SortArray
from src.core.events import SortEvent


def shell_sort(values: list[int]) -> tuple[list[int], list[SortEvent]]:
    """シェルソートを実行し、ソート済み配列とイベント列を返す。

    Knuth のギャップ列 (h = 3h + 1) を使い、各ギャップで挿入ソートを行う。
    最終的にギャップ 1 で通常の挿入ソートを実行して完了する。

    Args:
        values: ソート対象の整数リスト。

    Returns:
        (ソート済みリスト, イベント列) のタプル。
    """
    arr = SortArray(values)
    n = len(arr)

    # Knuth のギャップ列を構築: 1, 4, 13, 40, 121, ...
    gap = 1
    while gap < n // 3:
        gap = gap * 3 + 1

    while gap >= 1:
        for i in range(gap, n):
            j = i
            while j >= gap and arr.compare(j - gap, j) > 0:
                arr.swap(j - gap, j)
                j -= gap
        gap //= 3

    # 全要素をソート済みとしてマーク
    for i in range(n):
        arr.mark_sorted(i)

    return arr.to_list(), arr.events()
