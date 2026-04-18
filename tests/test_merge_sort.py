"""tests/test_merge_sort.py – マージソートのテスト。"""

from __future__ import annotations

from src.algorithms.merge_sort import merge_sort
from src.core.events import EventType


class TestMergeSort:
    """merge_sort() のテスト。"""

    def test_basic_sort(self) -> None:
        sorted_vals, _ = merge_sort([3, 1, 2])
        assert sorted_vals == [1, 2, 3]

    def test_events_not_empty(self) -> None:
        _, events = merge_sort([3, 1, 2])
        assert len(events) > 0

    def test_contains_overwrite(self) -> None:
        """マージソートは overwrite イベントを使う。"""
        _, events = merge_sort([3, 1, 2])
        assert any(e.type is EventType.OVERWRITE for e in events)

    def test_no_compare_or_swap(self) -> None:
        """マージソートはバッファ比較のため compare/swap イベントを出さない。"""
        _, events = merge_sort([3, 1, 2])
        assert not any(e.type is EventType.COMPARE for e in events)
        assert not any(e.type is EventType.SWAP for e in events)

    def test_contains_mark_sorted(self) -> None:
        _, events = merge_sort([3, 1, 2])
        mark_events = [e for e in events if e.type is EventType.MARK_SORTED]
        assert len(mark_events) == 3

    def test_already_sorted(self) -> None:
        sorted_vals, _ = merge_sort([1, 2, 3])
        assert sorted_vals == [1, 2, 3]

    def test_reverse_sorted(self) -> None:
        sorted_vals, _ = merge_sort([5, 4, 3, 2, 1])
        assert sorted_vals == [1, 2, 3, 4, 5]

    def test_duplicates(self) -> None:
        sorted_vals, _ = merge_sort([2, 3, 1, 2, 3])
        assert sorted_vals == [1, 2, 2, 3, 3]

    def test_single_element(self) -> None:
        sorted_vals, events = merge_sort([42])
        assert sorted_vals == [42]
        assert any(e.type is EventType.MARK_SORTED for e in events)

    def test_empty(self) -> None:
        sorted_vals, events = merge_sort([])
        assert sorted_vals == []
        assert events == []

    def test_large_array(self) -> None:
        import random
        rng = random.Random(0)
        data = list(range(1, 65))
        rng.shuffle(data)
        sorted_vals, _ = merge_sort(data)
        assert sorted_vals == list(range(1, 65))

    def test_step_monotonic(self) -> None:
        _, events = merge_sort([5, 3, 1, 4, 2])
        steps = [e.step for e in events]
        assert steps == sorted(steps)
        assert len(steps) == len(set(steps))


