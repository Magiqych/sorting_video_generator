"""バケットソート (Bucket Sort) の実装。

SortArray を使い、操作ごとにイベントを記録する。
値をバケットに分配し、各バケット内を挿入ソートで整列後、
overwrite で元の配列に書き戻す。
"""

from __future__ import annotations

from src.core.array import SortArray
from src.core.events import SortEvent


def bucket_sort(values: list[int]) -> tuple[list[int], list[SortEvent]]:
    """バケットソートを実行し、ソート済み配列とイベント列を返す。

    値の範囲に基づきバケットに分配し、各バケット内を挿入ソートで整列する。
    compare / swap は発生せず overwrite + mark_sorted で書き戻す。

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

    min_val = min(values)
    max_val = max(values)

    # バケット数は要素数と同じ
    bucket_count = n
    spread = max_val - min_val + 1

    buckets: list[list[int]] = [[] for _ in range(bucket_count)]

    # ---- 分配 ----
    for v in values:
        idx = (v - min_val) * bucket_count // spread
        if idx >= bucket_count:
            idx = bucket_count - 1
        buckets[idx].append(v)

    # ---- 各バケット内を挿入ソート ----
    for bucket in buckets:
        _insertion_sort_bucket(bucket)

    # ---- 書き戻し ----
    pos = 0
    for bucket in buckets:
        for v in bucket:
            arr.overwrite(pos, v)
            arr.mark_sorted(pos)
            pos += 1

    return arr.to_list(), arr.events()


def _insertion_sort_bucket(bucket: list[int]) -> None:
    """リストを挿入ソートでインプレース整列する（イベントなし）。"""
    for i in range(1, len(bucket)):
        key = bucket[i]
        j = i - 1
        while j >= 0 and bucket[j] > key:
            bucket[j + 1] = bucket[j]
            j -= 1
        bucket[j + 1] = key
