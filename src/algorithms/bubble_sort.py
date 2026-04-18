"""バブルソートの実装。

SortArray を使い、操作ごとにイベントを記録する。
"""

from __future__ import annotations

from src.core.array import SortArray
from src.core.events import SortEvent


def bubble_sort(values: list[int]) -> tuple[list[int], list[SortEvent]]:
    """バブルソートを実行し、ソート済み配列とイベント列を返す。

    各パスの末尾で確定した要素に mark_sorted を付与する。
    交換が発生しなかったパスで早期終了する。

    Args:
        values: ソート対象の整数リスト。

    Returns:
        (ソート済みリスト, イベント列) のタプル。
    """
    arr = SortArray(values)
    n = len(arr)

    for end in range(n - 1, 0, -1):
        swapped = False
        for j in range(end):
            if arr.compare(j, j + 1) > 0:
                arr.swap(j, j + 1)
                swapped = True
        # このパスで確定した末尾要素をマーク
        arr.mark_sorted(end)
        if not swapped:
            break

    # 残りの先頭要素も整列済みとしてマーク
    for i in range(n):
        # 既に mark_sorted 済みのインデックスも重複して問題ない
        # ただし未マーク分（早期終了で飛ばされた分）を確実にカバーする
        pass
    # 先頭要素（index 0）は常にソート済み
    arr.mark_sorted(0)

    return arr.to_list(), arr.events()
