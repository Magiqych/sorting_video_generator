"""tests/test_insertion_sort.py – 挿入ソートのテスト。"""

from __future__ import annotations

from src.algorithms.insertion_sort import insertion_sort
from src.core.events import EventType


class TestInsertionSort:
    """insertion_sort() のテスト。"""

    def test_basic_sort(self) -> None:
        sorted_vals, _ = insertion_sort([3, 1, 2])
        assert sorted_vals == [1, 2, 3]

    def test_events_not_empty(self) -> None:
        _, events = insertion_sort([3, 1, 2])
        assert len(events) > 0

    def test_contains_compare(self) -> None:
        _, events = insertion_sort([3, 1, 2])
        assert any(e.type is EventType.COMPARE for e in events)

    def test_contains_swap(self) -> None:
        _, events = insertion_sort([3, 1, 2])
        assert any(e.type is EventType.SWAP for e in events)

    def test_contains_mark_sorted(self) -> None:
        _, events = insertion_sort([3, 1, 2])
        mark_events = [e for e in events if e.type is EventType.MARK_SORTED]
        assert len(mark_events) == 3

    def test_already_sorted(self) -> None:
        sorted_vals, events = insertion_sort([1, 2, 3])
        assert sorted_vals == [1, 2, 3]
        assert any(e.type is EventType.COMPARE for e in events)
        assert not any(e.type is EventType.SWAP for e in events)

    def test_reverse_sorted(self) -> None:
        sorted_vals, _ = insertion_sort([5, 4, 3, 2, 1])
        assert sorted_vals == [1, 2, 3, 4, 5]

    def test_duplicates(self) -> None:
        sorted_vals, _ = insertion_sort([2, 3, 1, 2, 3])
        assert sorted_vals == [1, 2, 2, 3, 3]

    def test_single_element(self) -> None:
        sorted_vals, events = insertion_sort([42])
        assert sorted_vals == [42]
        assert any(e.type is EventType.MARK_SORTED for e in events)

    def test_step_monotonic(self) -> None:
        _, events = insertion_sort([5, 3, 1, 4, 2])
        steps = [e.step for e in events]
        assert steps == sorted(steps)
        assert len(steps) == len(set(steps))
