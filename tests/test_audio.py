"""音声レンダラのテスト。"""

import os
import tempfile

import numpy as np

from src.core.events import EventType, SortEvent
from src.render.audio import (
    generate_event_audio,
    generate_tone,
    render_audio_track,
    value_to_frequency,
)


class TestValueToFrequency:
    def test_min_maps_to_min_freq(self) -> None:
        freq = value_to_frequency(1, 1, 10, 220.0, 880.0)
        assert abs(freq - 220.0) < 1e-6

    def test_max_maps_to_max_freq(self) -> None:
        freq = value_to_frequency(10, 1, 10, 220.0, 880.0)
        assert abs(freq - 880.0) < 1e-6

    def test_mid_value(self) -> None:
        freq = value_to_frequency(5, 0, 10, 200.0, 800.0)
        assert 400.0 - 1e-6 < freq < 600.0 + 1e-6

    def test_equal_min_max(self) -> None:
        freq = value_to_frequency(5, 5, 5, 220.0, 880.0)
        assert abs(freq - 550.0) < 1e-6


class TestGenerateTone:
    def test_returns_ndarray(self) -> None:
        tone = generate_tone(440.0, 0.05)
        assert isinstance(tone, np.ndarray)

    def test_not_empty(self) -> None:
        tone = generate_tone(440.0, 0.05)
        assert len(tone) > 0

    def test_one_dimensional(self) -> None:
        tone = generate_tone(440.0, 0.05)
        assert tone.ndim == 1

    def test_no_clipping(self) -> None:
        tone = generate_tone(440.0, 0.1, volume=1.0)
        assert np.max(np.abs(tone)) <= 1.0 + 1e-6


class TestGenerateEventAudio:
    def _make_event(self, etype: EventType, values: tuple[int, ...] = ()) -> SortEvent:
        return SortEvent(type=etype, step=0, indices=(0, 1), values=values)

    def test_compare(self) -> None:
        audio = generate_event_audio(self._make_event(EventType.COMPARE, (3, 7)), 1, 10)
        assert isinstance(audio, np.ndarray)
        assert len(audio) > 0

    def test_swap(self) -> None:
        audio = generate_event_audio(self._make_event(EventType.SWAP, (3, 7)), 1, 10)
        assert len(audio) > 0

    def test_mark_sorted(self) -> None:
        event = SortEvent(type=EventType.MARK_SORTED, step=0, indices=(5,))
        audio = generate_event_audio(event, 1, 10)
        assert len(audio) > 0

    def test_shuffle_with_values(self) -> None:
        audio = generate_event_audio(self._make_event(EventType.SHUFFLE, (2, 8)), 1, 10)
        assert len(audio) > 0

    def test_shuffle_without_values(self) -> None:
        audio = generate_event_audio(self._make_event(EventType.SHUFFLE), 1, 10)
        assert len(audio) > 0

    def test_overwrite(self) -> None:
        event = SortEvent(type=EventType.OVERWRITE, step=0, indices=(0,), values=(5,))
        audio = generate_event_audio(event, 1, 10)
        assert len(audio) > 0


class TestRenderAudioTrack:
    def test_creates_wav(self) -> None:
        events = [
            SortEvent(type=EventType.COMPARE, step=0, indices=(0, 1), values=(3, 5)),
            SortEvent(type=EventType.SWAP, step=1, indices=(0, 1), values=(3, 5)),
            SortEvent(type=EventType.MARK_SORTED, step=2, indices=(1,)),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            wav_path = os.path.join(tmpdir, "test.wav")
            result = render_audio_track(events, wav_path, min_value=1, max_value=10)
            assert os.path.isfile(result)
            assert os.path.getsize(result) > 0
