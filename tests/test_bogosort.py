"""tests/test_bogosort.py – ボゴソートのテスト。"""

from __future__ import annotations

import pytest

from src.algorithms.bogosort import bogo_sort
from src.core.events import EventType


class TestBogoSort:
    """bogo_sort() のテスト。"""

    def test_basic_sort(self) -> None:
        sorted_vals, _ = bogo_sort([3, 1, 2], seed=0)
        assert sorted_vals == [1, 2, 3]

    def test_already_sorted(self) -> None:
        sorted_vals, events = bogo_sort([1, 2, 3], seed=0)
        assert sorted_vals == [1, 2, 3]
        # ソート済みなら比較 + mark_sorted のみ（シャッフル無し）
        types = {e.type for e in events}
        assert EventType.COMPARE in types
        assert EventType.MARK_SORTED in types
        assert EventType.SHUFFLE not in types

    def test_single_element(self) -> None:
        sorted_vals, events = bogo_sort([42], seed=0)
        assert sorted_vals == [42]
        assert any(e.type is EventType.MARK_SORTED for e in events)

    def test_empty(self) -> None:
        sorted_vals, events = bogo_sort([], seed=0)
        assert sorted_vals == []
        assert events == []

    def test_contains_compare(self) -> None:
        _, events = bogo_sort([2, 1], seed=0)
        assert any(e.type is EventType.COMPARE for e in events)

    def test_contains_shuffle(self) -> None:
        _, events = bogo_sort([3, 1, 2], seed=0)
        assert any(e.type is EventType.SHUFFLE for e in events)

    def test_contains_mark_sorted(self) -> None:
        _, events = bogo_sort([2, 1], seed=0)
        mark_events = [e for e in events if e.type is EventType.MARK_SORTED]
        assert len(mark_events) == 2  # 全要素分

    def test_deterministic(self) -> None:
        _, events1 = bogo_sort([3, 1, 2], seed=42)
        _, events2 = bogo_sort([3, 1, 2], seed=42)
        assert len(events1) == len(events2)
        for e1, e2 in zip(events1, events2):
            assert e1.type == e2.type
            assert e1.indices == e2.indices

    def test_step_monotonic(self) -> None:
        _, events = bogo_sort([3, 2, 1], seed=10)
        steps = [e.step for e in events]
        assert steps == sorted(steps)
        assert len(steps) == len(set(steps))  # 重複なし

    def test_max_attempts_exceeded(self) -> None:
        # max_attempts=0 なら即エラー（ソート済みでない限り）
        with pytest.raises(RuntimeError, match="完了しませんでした"):
            bogo_sort([2, 1], seed=0, max_attempts=0)

    def test_five_elements(self) -> None:
        """5要素でもソートできることを確認。"""
        sorted_vals, events = bogo_sort([5, 3, 1, 4, 2], seed=42)
        assert sorted_vals == [1, 2, 3, 4, 5]
        assert len(events) > 0
