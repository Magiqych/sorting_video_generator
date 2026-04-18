"""冒頭シャッフル演出のテスト。"""

from src.core.events import EventType
from src.core.intro import build_intro_shuffle_events, build_sorted_values


class TestBuildSortedValues:
    def test_basic(self) -> None:
        assert build_sorted_values(5) == [1, 2, 3, 4, 5]

    def test_single(self) -> None:
        assert build_sorted_values(1) == [1]


class TestBuildIntroShuffleEvents:
    def test_reproducible(self) -> None:
        vals = build_sorted_values(10)
        result_a, events_a = build_intro_shuffle_events(vals, shuffle_steps=30, seed=123)
        result_b, events_b = build_intro_shuffle_events(vals, shuffle_steps=30, seed=123)
        assert result_a == result_b
        assert len(events_a) == len(events_b)

    def test_events_not_empty(self) -> None:
        vals = build_sorted_values(10)
        _, events = build_intro_shuffle_events(vals, shuffle_steps=30, seed=0)
        assert len(events) > 0

    def test_only_shuffle_events(self) -> None:
        vals = build_sorted_values(10)
        _, events = build_intro_shuffle_events(vals, shuffle_steps=30, seed=0)
        for e in events:
            assert e.type is EventType.SHUFFLE

    def test_does_not_mutate_input(self) -> None:
        vals = [1, 2, 3, 4, 5]
        original = list(vals)
        build_intro_shuffle_events(vals, shuffle_steps=20, seed=0)
        assert vals == original
