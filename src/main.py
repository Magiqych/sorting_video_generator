"""CLI エントリポイント。

コマンドラインからソートアルゴリズム可視化動画を生成する。

使い方:
    python -m src.main --algorithm bubble
    python -m src.main --algorithm bubble --size 64 --seed 0 --output output/my_video.mp4
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Callable

from src.core import config as cfg
from src.core.intro import build_sorted_values, build_intro_shuffle_events
from src.render.audio import render_audio_track
from src.render.compose import mux_video_and_audio
from src.render.video import (
    prepare_bubble_sort_events,
    prepare_bogo_sort_events,
    prepare_selection_sort_events,
    prepare_insertion_sort_events,
    prepare_shell_sort_events,
    prepare_merge_sort_events,
    prepare_quick_sort_events,
    render_bubble_sort_video,
    render_bogo_sort_video,
    render_selection_sort_video,
    render_insertion_sort_video,
    render_shell_sort_video,
    render_merge_sort_video,
    render_quick_sort_video,
)

# ---- アルゴリズム registry ----
# 将来アルゴリズムを追加する場合はここにエントリを足す。

SUPPORTED_ALGORITHMS: dict[str, str] = {
    "bubble": "Bubble Sort",
    "bogo": "Bogo Sort",
    "selection": "Selection Sort",
    "insertion": "Insertion Sort",
    "shell": "Shell Sort",
    "merge": "Merge Sort",
    "quick": "Quick Sort",
}


def build_parser() -> argparse.ArgumentParser:
    """CLI 引数パーサーを構築する。"""
    parser = argparse.ArgumentParser(
        prog="python -m src.main",
        description="ソートアルゴリズム可視化動画を生成する",
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        required=True,
        choices=list(SUPPORTED_ALGORITHMS.keys()),
        help="ソートアルゴリズム名",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=32,
        help="配列の要素数 (default: 32)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="シャッフル用乱数シード (default: 42)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="出力 MP4 ファイルパス (--output-dir より優先)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="出力ディレクトリ (default: output)",
    )
    parser.add_argument(
        "--keep-intermediate",
        action="store_true",
        help="中間ファイル (無音 MP4, WAV) を残す",
    )
    parser.add_argument(
        "--silent-only",
        action="store_true",
        help="無音動画のみ生成して終了する",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="WAV 音声のみ生成して終了する",
    )
    parser.add_argument(
        "--intro-shuffle-steps",
        type=int,
        default=None,
        help="イントロシャッフル回数 (default: FPS * INTRO_SECONDS)",
    )
    return parser


def resolve_output_path(
    algorithm: str,
    output: str | None,
    output_dir: str,
    suffix: str = ".mp4",
) -> Path:
    """出力ファイルパスを決定する。

    --output が指定されていればそれを使い、
    なければ output_dir / {algorithm}_sort{suffix} を返す。

    Args:
        algorithm: アルゴリズム名。
        output: --output の値。None なら自動決定。
        output_dir: --output-dir の値。
        suffix: 拡張子。

    Returns:
        出力ファイルの Path。
    """
    if output is not None:
        return Path(output)
    return Path(output_dir) / f"{algorithm}_sort{suffix}"


def ensure_parent_dir(path: Path) -> None:
    """親ディレクトリが存在しなければ作成する。"""
    path.parent.mkdir(parents=True, exist_ok=True)


def run_generation(args: argparse.Namespace) -> str:
    """引数に基づいて動画生成を実行する。

    Args:
        args: パース済み引数。

    Returns:
        生成されたファイルのパス。
    """
    algorithm: str = args.algorithm
    size: int = args.size
    seed: int = args.seed

    if algorithm not in SUPPORTED_ALGORITHMS:
        raise NotImplementedError(
            f"アルゴリズム '{algorithm}' はまだ実装されていません。"
            f" 現在対応: {list(SUPPORTED_ALGORITHMS.keys())}"
        )

    # ---- アルゴリズム別の関数を選択 ----
    if algorithm == "bogo":
        render_video_fn = lambda path, **kw: render_bogo_sort_video(path, **kw, sort_seed=seed)
        prepare_events_fn = lambda **kw: prepare_bogo_sort_events(**kw, sort_seed=seed)
    elif algorithm == "selection":
        render_video_fn = render_selection_sort_video
        prepare_events_fn = prepare_selection_sort_events
    elif algorithm == "insertion":
        render_video_fn = render_insertion_sort_video
        prepare_events_fn = prepare_insertion_sort_events
    elif algorithm == "shell":
        render_video_fn = render_shell_sort_video
        prepare_events_fn = prepare_shell_sort_events
    elif algorithm == "merge":
        render_video_fn = render_merge_sort_video
        prepare_events_fn = prepare_merge_sort_events
    elif algorithm == "quick":
        render_video_fn = render_quick_sort_video
        prepare_events_fn = prepare_quick_sort_events
    else:
        render_video_fn = render_bubble_sort_video
        prepare_events_fn = prepare_bubble_sort_events

    # ---- silent-only モード ----
    if args.silent_only:
        out_path = resolve_output_path(algorithm, args.output, args.output_dir, suffix="_silent.mp4")
        if args.output is not None and not str(out_path).endswith("_silent.mp4"):
            pass  # ユーザー指定パスをそのまま使う
        ensure_parent_dir(out_path)
        render_video_fn(str(out_path), size=size, seed=seed)
        return str(out_path)

    # ---- audio-only モード ----
    if args.audio_only:
        out_path = resolve_output_path(algorithm, args.output, args.output_dir, suffix=".wav")
        ensure_parent_dir(out_path)
        plan = prepare_events_fn(size=size, seed=seed)
        all_events = plan.shuffle_events + plan.sort_events
        render_audio_track(
            all_events,
            str(out_path),
            min_value=plan.min_value,
            max_value=plan.max_value,
            frames_per_event=1,
            fps=cfg.FPS,
            pre_hold_frames=plan.initial_hold_frames,
            post_hold_frames=plan.end_hold_frames,
        )
        return str(out_path)

    # ---- 通常モード: 映像 + 音声 → 最終 MP4 ----
    final_path = resolve_output_path(algorithm, args.output, args.output_dir)
    ensure_parent_dir(final_path)

    out_dir = final_path.parent
    stem = final_path.stem

    silent_path = out_dir / f"{stem}_silent.mp4"
    wav_path = out_dir / f"{stem}.wav"

    # 1. イベント列を準備
    plan = prepare_events_fn(size=size, seed=seed)

    # 2. 無音動画を生成
    render_video_fn(str(silent_path), size=size, seed=seed)

    # 3. WAV を生成
    all_events = plan.shuffle_events + plan.sort_events
    render_audio_track(
        all_events,
        str(wav_path),
        min_value=plan.min_value,
        max_value=plan.max_value,
        frames_per_event=1,
        fps=cfg.FPS,
        pre_hold_frames=plan.initial_hold_frames,
        post_hold_frames=plan.end_hold_frames,
    )

    # 4. 合成
    mux_video_and_audio(str(silent_path), str(wav_path), str(final_path))

    # 5. 中間ファイルの削除
    if not args.keep_intermediate:
        silent_path.unlink(missing_ok=True)
        wav_path.unlink(missing_ok=True)

    return str(final_path)


def main() -> None:
    """CLI エントリポイント。"""
    parser = build_parser()
    args = parser.parse_args()

    print(f"Algorithm: {SUPPORTED_ALGORITHMS[args.algorithm]}")
    print(f"Size: {args.size}, Seed: {args.seed}")

    result_path = run_generation(args)

    print(f"Generated: {result_path}")


if __name__ == "__main__":
    main()
