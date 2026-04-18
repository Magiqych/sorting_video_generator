"""ボゴソートの実装。

SortArray を使い、操作ごとにイベントを記録する。
ボゴソートは配列がソート済みか判定し、未ソートなら全体をランダムにシャッフルする。
期待計算量 O(n * n!) のため、小さい配列 (≤8) での使用を想定。
"""

from __future__ import annotations

import random

from src.core.array import SortArray
from src.core.events import SortEvent


def _is_sorted(arr: SortArray, n: int) -> bool:
    """配列がソート済みか compare イベントを記録しながら判定する。"""
    for i in range(n - 1):
        if arr.compare(i, i + 1) > 0:
            return False
    return True


def _fisher_yates_shuffle(arr: SortArray, n: int, rng: random.Random) -> None:
    """Fisher-Yates シャッフルを shuffle イベントとして記録する。"""
    for i in range(n - 1, 0, -1):
        j = rng.randint(0, i)
        if i != j:
            arr.shuffle(i, j)


def bogo_sort(
    values: list[int],
    seed: int = 42,
    max_attempts: int = 100_000,
) -> tuple[list[int], list[SortEvent]]:
    """ボゴソートを実行し、ソート済み配列とイベント列を返す。

    Args:
        values: ソート対象の整数リスト。
        seed: シャッフル用乱数シード。
        max_attempts: 最大試行回数。超えると RuntimeError。

    Returns:
        (ソート済みリスト, イベント列) のタプル。

    Raises:
        RuntimeError: max_attempts 以内にソートが完了しなかった場合。
    """
    arr = SortArray(values)
    n = len(arr)
    rng = random.Random(seed)

    if n <= 1:
        if n == 1:
            arr.mark_sorted(0)
        return arr.to_list(), arr.events()

    attempts = 0
    while not _is_sorted(arr, n):
        if attempts >= max_attempts:
            raise RuntimeError(
                f"ボゴソートが {max_attempts} 回以内に完了しませんでした。"
                f" 配列サイズ {n} は大きすぎる可能性があります。"
            )
        _fisher_yates_shuffle(arr, n, rng)
        attempts += 1

    # 全要素をソート済みとしてマーク
    for i in range(n):
        arr.mark_sorted(i)

    return arr.to_list(), arr.events()
