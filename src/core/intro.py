"""冒頭シャッフル演出用のユーティリティ。

整列済み配列を作り、ランダムにばらすイベント列を生成する。
"""

from __future__ import annotations

import random

from src.core.array import SortArray
from src.core.events import SortEvent


def build_sorted_values(size: int) -> list[int]:
    """1..size の昇順配列を返す。

    Args:
        size: 配列の要素数。

    Returns:
        [1, 2, ..., size]
    """
    return list(range(1, size + 1))


def build_intro_shuffle_events(
    values: list[int],
    shuffle_steps: int,
    seed: int | None = None,
) -> tuple[list[int], list[SortEvent]]:
    """整列済み配列をランダムにばらし、shuffle イベント列を返す。

    Args:
        values: 初期配列（整列済みを想定）。
        shuffle_steps: シャッフル操作の回数。
        seed: 乱数シード。None の場合はランダム。

    Returns:
        (シャッフル後の配列, shuffle イベント列) のタプル。
    """
    rng = random.Random(seed)
    arr = SortArray(values)
    n = len(arr)

    for _ in range(shuffle_steps):
        i = rng.randint(0, n - 1)
        j = rng.randint(0, n - 1)
        if i != j:
            arr.shuffle(i, j)

    return arr.to_list(), arr.events()
