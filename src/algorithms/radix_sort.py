"""基数ソート (Radix Sort) の実装。

SortArray を使い、操作ごとにイベントを記録する。
LSD (Least Significant Digit) 方式で、各桁ごとに安定な配置を行う。
"""

from __future__ import annotations

from src.core.array import SortArray
from src.core.events import SortEvent


def radix_sort(values: list[int]) -> tuple[list[int], list[SortEvent]]:
    """基数ソート (LSD) を実行し、ソート済み配列とイベント列を返す。

    各桁について計数ソートを適用し、overwrite で配列を書き戻す。
    比較ベースではないため compare / swap イベントは発生しない。

    Args:
        values: ソート対象の正の整数リスト。

    Returns:
        (ソート済みリスト, イベント列) のタプル。
    """
    arr = SortArray(values)
    n = len(arr)

    if n <= 1:
        if n == 1:
            arr.mark_sorted(0)
        return arr.to_list(), arr.events()

    max_val = max(values)

    exp = 1
    while max_val // exp > 0:
        _counting_sort_by_digit(arr, n, exp)
        exp *= 10

    for i in range(n):
        arr.mark_sorted(i)

    return arr.to_list(), arr.events()


def _counting_sort_by_digit(arr: SortArray, n: int, exp: int) -> None:
    """指定桁 (exp) に基づく安定な計数ソートを適用する。"""
    # 現在の配列の値を読み取る
    current = [arr[i] for i in range(n)]

    count = [0] * 10
    for val in current:
        digit = (val // exp) % 10
        count[digit] += 1

    # 累積和で出力位置を決定
    for i in range(1, 10):
        count[i] += count[i - 1]

    # 安定ソートのため後ろから配置
    output = [0] * n
    for i in range(n - 1, -1, -1):
        digit = (current[i] // exp) % 10
        count[digit] -= 1
        output[count[digit]] = current[i]

    # 結果を配列に書き戻す
    for i in range(n):
        arr.overwrite(i, output[i])
