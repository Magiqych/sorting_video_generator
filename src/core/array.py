"""ソート用配列ラッパー。

配列操作のたびに SortEvent を記録し、アルゴリズムとレンダラを疎結合にする。
"""

from __future__ import annotations

from .events import EventType, SortEvent


class SortArray:
    """list[int] を包み、操作ごとに SortEvent を記録する配列ラッパー。

    Args:
        data: 初期配列。内部でコピーして保持する。
    """

    def __init__(self, data: list[int]) -> None:
        self._data: list[int] = list(data)
        self._events: list[SortEvent] = []
        self._step: int = 0

    # ---- 基本アクセス ----

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, index: int) -> int:
        self._check_index(index)
        return self._data[index]

    def to_list(self) -> list[int]:
        """現在の配列をコピーとして返す。"""
        return list(self._data)

    # ---- イベント付き操作 ----

    def compare(self, i: int, j: int) -> int:
        """arr[i] と arr[j] を比較し、compare イベントを記録する。

        Returns:
            -1 (arr[i] < arr[j]), 0 (等しい), 1 (arr[i] > arr[j])
        """
        self._check_index(i)
        self._check_index(j)
        self._record(EventType.COMPARE, indices=(i, j), values=(self._data[i], self._data[j]))
        if self._data[i] < self._data[j]:
            return -1
        if self._data[i] > self._data[j]:
            return 1
        return 0

    def swap(self, i: int, j: int) -> None:
        """arr[i] と arr[j] を交換し、swap イベントを記録する。"""
        self._check_index(i)
        self._check_index(j)
        old_i, old_j = self._data[i], self._data[j]
        self._data[i], self._data[j] = self._data[j], self._data[i]
        self._record(EventType.SWAP, indices=(i, j), values=(old_i, old_j))

    def overwrite(self, i: int, value: int) -> None:
        """arr[i] を value で上書きし、overwrite イベントを記録する。"""
        self._check_index(i)
        self._data[i] = value
        self._record(EventType.OVERWRITE, indices=(i,), values=(value,))

    def mark_sorted(self, i: int) -> None:
        """インデックス i を整列済みとしてマークする（配列は変更しない）。"""
        self._check_index(i)
        self._record(EventType.MARK_SORTED, indices=(i,))

    def shuffle(self, i: int, j: int) -> None:
        """arr[i] と arr[j] を入れ替え、shuffle イベントを記録する。"""
        self._check_index(i)
        self._check_index(j)
        old_i, old_j = self._data[i], self._data[j]
        self._data[i], self._data[j] = self._data[j], self._data[i]
        self._record(EventType.SHUFFLE, indices=(i, j), values=(old_i, old_j))

    def events(self) -> list[SortEvent]:
        """記録済みイベントのコピーを返す。"""
        return list(self._events)

    # ---- 内部ヘルパー ----

    def _check_index(self, index: int) -> None:
        if index < 0 or index >= len(self._data):
            raise IndexError(f"index {index} is out of range for array of length {len(self._data)}")

    def _record(
        self,
        event_type: EventType,
        *,
        indices: tuple[int, ...],
        values: tuple[int, ...] = (),
        meta: dict[str, object] | None = None,
    ) -> None:
        self._events.append(
            SortEvent(type=event_type, step=self._step, indices=indices, values=values, meta=meta)
        )
        self._step += 1
