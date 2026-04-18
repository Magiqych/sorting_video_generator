"""SortEvent / EventType の基本テスト。"""

from src.core.events import EventType, SortEvent


class TestEventType:
    def test_values(self) -> None:
        assert EventType.COMPARE.value == "compare"
        assert EventType.SWAP.value == "swap"
        assert EventType.OVERWRITE.value == "overwrite"
        assert EventType.MARK_SORTED.value == "mark_sorted"
        assert EventType.SHUFFLE.value == "shuffle"

    def test_member_count(self) -> None:
        assert len(EventType) == 5


class TestSortEvent:
    def test_create_compare_event(self) -> None:
        event = SortEvent(type=EventType.COMPARE, step=0, indices=(0, 1), values=(3, 5))
        assert event.type is EventType.COMPARE
        assert event.step == 0
        assert event.indices == (0, 1)
        assert event.values == (3, 5)
        assert event.meta is None

    def test_default_values(self) -> None:
        event = SortEvent(type=EventType.MARK_SORTED, step=1, indices=(2,))
        assert event.values == ()
        assert event.meta is None

    def test_with_meta(self) -> None:
        event = SortEvent(
            type=EventType.SWAP, step=5, indices=(1, 2), values=(10, 20), meta={"reason": "test"}
        )
        assert event.meta == {"reason": "test"}

    def test_frozen(self) -> None:
        event = SortEvent(type=EventType.COMPARE, step=0, indices=(0, 1))
        try:
            event.step = 99  # type: ignore[misc]
            assert False, "Should raise FrozenInstanceError"
        except AttributeError:
            pass
