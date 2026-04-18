"""映像レンダラの最小テスト。"""

import numpy as np

from src.core import config as cfg
from src.render.video import render_bars_frame


class TestRenderBarsFrame:
    def test_returns_ndarray(self) -> None:
        frame = render_bars_frame([3, 1, 2])
        assert isinstance(frame, np.ndarray)

    def test_shape(self) -> None:
        frame = render_bars_frame([3, 1, 2])
        assert frame.shape == (cfg.HEIGHT, cfg.WIDTH, 3)

    def test_empty_values(self) -> None:
        frame = render_bars_frame([])
        assert frame.shape == (cfg.HEIGHT, cfg.WIDTH, 3)

    def test_with_highlight(self) -> None:
        frame = render_bars_frame(
            [5, 3, 4, 1, 2],
            highlighted_indices=(0, 1),
            state="compare",
            sorted_indices={4},
            title="Test",
        )
        assert frame.shape == (cfg.HEIGHT, cfg.WIDTH, 3)
