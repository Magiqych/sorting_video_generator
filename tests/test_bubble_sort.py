"""Bubble Sort のテスト。"""

from src.core.events import EventType
from src.algorithms.bubble_sort import bubble_sort


class TestBubbleSort:
    def test_basic_sort(self) -> None:
        sorted_list, events = bubble_sort([3, 2, 1])
        assert sorted_list == [1, 2, 3]

    def test_events_not_empty(self) -> None:
        _, events = bubble_sort([3, 2, 1])
        assert len(events) > 0

    def test_contains_compare(self) -> None:
        _, events = bubble_sort([3, 2, 1])
        assert any(e.type is EventType.COMPARE for e in events)

    def test_contains_swap(self) -> None:
        _, events = bubble_sort([3, 2, 1])
        assert any(e.type is EventType.SWAP for e in events)

    def test_contains_mark_sorted(self) -> None:
        _, events = bubble_sort([3, 2, 1])
        assert any(e.type is EventType.MARK_SORTED for e in events)

    def test_already_sorted(self) -> None:
        sorted_list, events = bubble_sort([1, 2, 3])
        assert sorted_list == [1, 2, 3]
        # 早期終了しても compare と mark_sorted は発生する
        assert any(e.type is EventType.COMPARE for e in events)
        assert any(e.type is EventType.MARK_SORTED for e in events)
        # 交換は不要
        assert not any(e.type is EventType.SWAP for e in events)

    def test_duplicates(self) -> None:
        sorted_list, events = bubble_sort([3, 1, 1, 2])
        assert sorted_list == [1, 1, 2, 3]
        assert len(events) > 0

    def test_single_element(self) -> None:
        sorted_list, events = bubble_sort([42])
        assert sorted_list == [42]
        # mark_sorted(0) のみ
        assert any(e.type is EventType.MARK_SORTED for e in events)

    def test_step_monotonic(self) -> None:
        """step が単調増加であることを確認。"""
        _, events = bubble_sort([5, 3, 4, 1, 2])
        steps = [e.step for e in events]
        assert steps == sorted(steps)
        assert len(steps) == len(set(steps))  # 重複なし
