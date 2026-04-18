"""tests/test_shell_sort.py – シェルソートのテスト。"""

from __future__ import annotations

from src.algorithms.shell_sort import shell_sort
from src.core.events import EventType


class TestShellSort:
    """shell_sort() のテスト。"""

    def test_basic_sort(self) -> None:
        sorted_vals, _ = shell_sort([3, 1, 2])
        assert sorted_vals == [1, 2, 3]

    def test_events_not_empty(self) -> None:
        _, events = shell_sort([3, 1, 2])
        assert len(events) > 0

    def test_contains_compare(self) -> None:
        _, events = shell_sort([3, 1, 2])
        assert any(e.type is EventType.COMPARE for e in events)

    def test_contains_swap(self) -> None:
        _, events = shell_sort([3, 1, 2])
        assert any(e.type is EventType.SWAP for e in events)

    def test_contains_mark_sorted(self) -> None:
        _, events = shell_sort([3, 1, 2])
        mark_events = [e for e in events if e.type is EventType.MARK_SORTED]
        assert len(mark_events) == 3

    def test_already_sorted(self) -> None:
        sorted_vals, events = shell_sort([1, 2, 3])
        assert sorted_vals == [1, 2, 3]
        assert not any(e.type is EventType.SWAP for e in events)

    def test_reverse_sorted(self) -> None:
        sorted_vals, _ = shell_sort([5, 4, 3, 2, 1])
        assert sorted_vals == [1, 2, 3, 4, 5]

    def test_duplicates(self) -> None:
        sorted_vals, _ = shell_sort([2, 3, 1, 2, 3])
        assert sorted_vals == [1, 2, 2, 3, 3]

    def test_single_element(self) -> None:
        sorted_vals, events = shell_sort([42])
        assert sorted_vals == [42]
        assert any(e.type is EventType.MARK_SORTED for e in events)

    def test_large_array(self) -> None:
        import random
        rng = random.Random(0)
        data = list(range(1, 65))
        rng.shuffle(data)
        sorted_vals, _ = shell_sort(data)
        assert sorted_vals == list(range(1, 65))

    def test_step_monotonic(self) -> None:
        _, events = shell_sort([5, 3, 1, 4, 2])
        steps = [e.step for e in events]
        assert steps == sorted(steps)
        assert len(steps) == len(set(steps))

    def test_fewer_swaps_than_insertion(self) -> None:
        """シェルソートは逆順配列で挿入ソートより swap が少ない傾向。"""
        from src.algorithms.insertion_sort import insertion_sort
        data = list(range(20, 0, -1))
        _, shell_events = shell_sort(data)
        _, ins_events = insertion_sort(data)
        shell_swaps = sum(1 for e in shell_events if e.type is EventType.SWAP)
        ins_swaps = sum(1 for e in ins_events if e.type is EventType.SWAP)
        assert shell_swaps < ins_swaps
