"""tests/test_selection_sort.py – 選択ソートのテスト。"""

from __future__ import annotations

import pytest

from src.algorithms.selection_sort import selection_sort
from src.core.events import EventType


class TestSelectionSort:
    """selection_sort() のテスト。"""

    def test_basic_sort(self) -> None:
        sorted_vals, _ = selection_sort([3, 1, 2])
        assert sorted_vals == [1, 2, 3]

    def test_events_not_empty(self) -> None:
        _, events = selection_sort([3, 1, 2])
        assert len(events) > 0

    def test_contains_compare(self) -> None:
        _, events = selection_sort([3, 1, 2])
        assert any(e.type is EventType.COMPARE for e in events)

    def test_contains_swap(self) -> None:
        _, events = selection_sort([3, 1, 2])
        assert any(e.type is EventType.SWAP for e in events)

    def test_contains_mark_sorted(self) -> None:
        _, events = selection_sort([3, 1, 2])
        mark_events = [e for e in events if e.type is EventType.MARK_SORTED]
        assert len(mark_events) == 3  # 全要素分

    def test_already_sorted(self) -> None:
        sorted_vals, events = selection_sort([1, 2, 3])
        assert sorted_vals == [1, 2, 3]
        # ソート済みでも比較は発生する（swap は不要）
        assert any(e.type is EventType.COMPARE for e in events)
        assert not any(e.type is EventType.SWAP for e in events)

    def test_reverse_sorted(self) -> None:
        sorted_vals, _ = selection_sort([5, 4, 3, 2, 1])
        assert sorted_vals == [1, 2, 3, 4, 5]

    def test_duplicates(self) -> None:
        sorted_vals, _ = selection_sort([2, 3, 1, 2, 3])
        assert sorted_vals == [1, 2, 2, 3, 3]

    def test_single_element(self) -> None:
        sorted_vals, events = selection_sort([42])
        assert sorted_vals == [42]
        assert any(e.type is EventType.MARK_SORTED for e in events)

    def test_step_monotonic(self) -> None:
        _, events = selection_sort([5, 3, 1, 4, 2])
        steps = [e.step for e in events]
        assert steps == sorted(steps)
        assert len(steps) == len(set(steps))

    def test_no_unnecessary_swap(self) -> None:
        """最小値が既に正しい位置にある場合は swap しない。"""
        sorted_vals, events = selection_sort([1, 3, 2])
        assert sorted_vals == [1, 2, 3]
        # index 0 は既に最小なので最初のパスで swap 無し
        swaps = [e for e in events if e.type is EventType.SWAP]
        # swap は [3,2] → [2,3] の 1 回のみ
        assert len(swaps) == 1
