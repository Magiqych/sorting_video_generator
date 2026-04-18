"""tests/test_main.py – CLI エントリポイントのテスト。"""

from __future__ import annotations

import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.main import (
    SUPPORTED_ALGORITHMS,
    build_parser,
    resolve_output_path,
    ensure_parent_dir,
    run_generation,
)


# ===========================================================
# build_parser
# ===========================================================

class TestBuildParser:
    """build_parser() が返すパーサーのテスト。"""

    def test_required_algorithm(self) -> None:
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])  # --algorithm 未指定

    def test_valid_algorithm_bubble(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--algorithm", "bubble"])
        assert args.algorithm == "bubble"

    def test_invalid_algorithm_rejected(self) -> None:
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--algorithm", "bogus"])

    def test_defaults(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--algorithm", "bubble"])
        assert args.size == 32
        assert args.seed == 42
        assert args.output is None
        assert args.output_dir == "output"
        assert args.keep_intermediate is False
        assert args.silent_only is False
        assert args.audio_only is False
        assert args.intro_shuffle_steps is None

    def test_custom_values(self) -> None:
        parser = build_parser()
        args = parser.parse_args([
            "--algorithm", "bubble",
            "--size", "64",
            "--seed", "0",
            "--output", "my/video.mp4",
            "--output-dir", "results",
            "--keep-intermediate",
            "--intro-shuffle-steps", "100",
        ])
        assert args.size == 64
        assert args.seed == 0
        assert args.output == "my/video.mp4"
        assert args.output_dir == "results"
        assert args.keep_intermediate is True
        assert args.intro_shuffle_steps == 100

    def test_silent_only_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--algorithm", "bubble", "--silent-only"])
        assert args.silent_only is True

    def test_audio_only_flag(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["--algorithm", "bubble", "--audio-only"])
        assert args.audio_only is True


# ===========================================================
# resolve_output_path
# ===========================================================

class TestResolveOutputPath:
    """resolve_output_path() のテスト。"""

    def test_explicit_output(self) -> None:
        result = resolve_output_path("bubble", "my/video.mp4", "output")
        assert result == Path("my/video.mp4")

    def test_auto_output_mp4(self) -> None:
        result = resolve_output_path("bubble", None, "output")
        assert result == Path("output/bubble_sort.mp4")

    def test_auto_output_wav(self) -> None:
        result = resolve_output_path("bubble", None, "results", suffix=".wav")
        assert result == Path("results/bubble_sort.wav")

    def test_auto_output_silent(self) -> None:
        result = resolve_output_path("bubble", None, "output", suffix="_silent.mp4")
        assert result == Path("output/bubble_sort_silent.mp4")


# ===========================================================
# ensure_parent_dir
# ===========================================================

class TestEnsureParentDir:
    """ensure_parent_dir() のテスト。"""

    def test_creates_parent(self, tmp_path: Path) -> None:
        target = tmp_path / "sub" / "deep" / "file.mp4"
        ensure_parent_dir(target)
        assert target.parent.is_dir()


# ===========================================================
# SUPPORTED_ALGORITHMS
# ===========================================================

class TestSupportedAlgorithms:
    """SUPPORTED_ALGORITHMS レジストリのテスト。"""

    def test_bubble_registered(self) -> None:
        assert "bubble" in SUPPORTED_ALGORITHMS

    def test_display_name(self) -> None:
        assert SUPPORTED_ALGORITHMS["bubble"] == "Bubble Sort"


# ===========================================================
# run_generation (モック使用)
# ===========================================================

class TestRunGeneration:
    """run_generation() のテスト（重い処理はモックする）。"""

    @staticmethod
    def _make_args(**overrides: object) -> argparse.Namespace:
        defaults = dict(
            algorithm="bubble",
            size=8,
            seed=0,
            output=None,
            output_dir="output",
            keep_intermediate=False,
            silent_only=False,
            audio_only=False,
            intro_shuffle_steps=None,
        )
        defaults.update(overrides)
        return argparse.Namespace(**defaults)

    @patch("src.main.render_bubble_sort_video")
    def test_silent_only_mode(self, mock_render: MagicMock, tmp_path: Path) -> None:
        args = self._make_args(
            silent_only=True,
            output=str(tmp_path / "test_silent.mp4"),
        )
        result = run_generation(args)
        assert result == str(tmp_path / "test_silent.mp4")
        mock_render.assert_called_once()

    @patch("src.main.render_audio_track")
    @patch("src.main.prepare_bubble_sort_events")
    def test_audio_only_mode(
        self,
        mock_prepare: MagicMock,
        mock_audio: MagicMock,
        tmp_path: Path,
    ) -> None:
        mock_prepare.return_value = MagicMock(
            shuffle_events=[],
            sort_events=[],
            min_value=1,
            max_value=8,
            initial_hold_frames=0,
            end_hold_frames=0,
        )
        args = self._make_args(
            audio_only=True,
            output=str(tmp_path / "test.wav"),
        )
        result = run_generation(args)
        assert result == str(tmp_path / "test.wav")
        mock_audio.assert_called_once()

    @patch("src.main.mux_video_and_audio")
    @patch("src.main.render_audio_track")
    @patch("src.main.render_bubble_sort_video")
    @patch("src.main.prepare_bubble_sort_events")
    def test_normal_mode(
        self,
        mock_prepare: MagicMock,
        mock_video: MagicMock,
        mock_audio: MagicMock,
        mock_mux: MagicMock,
        tmp_path: Path,
    ) -> None:
        mock_prepare.return_value = MagicMock(
            shuffle_events=[],
            sort_events=[],
            min_value=1,
            max_value=8,
            initial_hold_frames=0,
            end_hold_frames=0,
        )
        args = self._make_args(
            output=str(tmp_path / "final.mp4"),
        )
        result = run_generation(args)
        assert result == str(tmp_path / "final.mp4")
        mock_video.assert_called_once()
        mock_audio.assert_called_once()
        mock_mux.assert_called_once()

    def test_unsupported_algorithm_raises(self) -> None:
        args = self._make_args(algorithm="bogus")
        with pytest.raises(NotImplementedError, match="bogus"):
            run_generation(args)
