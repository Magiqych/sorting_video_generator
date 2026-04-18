"""映像レンダラ。

イベント列を受け取り、OpenCV で縦長の棒グラフ可視化動画を生成する。
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import cv2
import numpy as np

from src.core import config as cfg
from src.core.events import EventType, SortEvent
from src.core.intro import build_intro_shuffle_events, build_sorted_values
from src.algorithms.bubble_sort import bubble_sort
from src.algorithms.bogosort import bogo_sort


@dataclass
class VideoEventPlan:
    """動画生成時のイベント構成情報。音声レンダラとの同期に使う。"""

    shuffle_events: list[SortEvent]
    sort_events: list[SortEvent]
    initial_hold_frames: int
    end_hold_frames: int
    size: int
    min_value: int
    max_value: int


def render_bars_frame(
    values: list[int],
    *,
    max_value: int | None = None,
    highlighted_indices: tuple[int, ...] = (),
    state: str | None = None,
    sorted_indices: set[int] | None = None,
    title: str | None = None,
) -> np.ndarray:
    """配列の現在状態を棒グラフとして 1 フレーム描画する。

    Args:
        values: 描画する配列。
        max_value: 棒の高さ正規化用の最大値。None なら values の最大値。
        highlighted_indices: ハイライト対象のインデックス群。
        state: ハイライトの種類 ("compare", "swap", "shuffle")。
        sorted_indices: ソート済みインデックスの集合。
        title: 上部に表示するタイトル文字列。

    Returns:
        shape (HEIGHT, WIDTH, 3) の BGR 画像 (numpy.ndarray)。
    """
    frame = np.full((cfg.HEIGHT, cfg.WIDTH, 3), cfg.BACKGROUND_COLOR, dtype=np.uint8)

    n = len(values)
    if n == 0:
        return frame

    if max_value is None:
        max_value = max(values)
    if sorted_indices is None:
        sorted_indices = set()

    highlight_set = set(highlighted_indices)

    # 色マッピング
    highlight_color = cfg.BAR_COLOR
    if state == "compare":
        highlight_color = cfg.COMPARE_COLOR
    elif state == "swap":
        highlight_color = cfg.SWAP_COLOR
    elif state == "shuffle":
        highlight_color = cfg.SHUFFLE_COLOR

    # 棒のレイアウト計算
    draw_width = cfg.WIDTH - 2 * cfg.SIDE_MARGIN
    draw_height = cfg.HEIGHT - cfg.TOP_MARGIN - cfg.BOTTOM_MARGIN

    total_gap = cfg.BAR_GAP * (n - 1) if n > 1 else 0
    bar_width = max(1, (draw_width - total_gap) // n)

    # 実際の描画幅を中央寄せ
    actual_width = bar_width * n + cfg.BAR_GAP * (n - 1) if n > 1 else bar_width
    x_offset = cfg.SIDE_MARGIN + (draw_width - actual_width) // 2

    for i, val in enumerate(values):
        # 棒の高さ (最低 1px)
        bar_height = max(1, int(val / max_value * draw_height))

        x1 = x_offset + i * (bar_width + cfg.BAR_GAP)
        x2 = x1 + bar_width
        y2 = cfg.HEIGHT - cfg.BOTTOM_MARGIN
        y1 = y2 - bar_height

        # 色決定: highlight > sorted > default
        if i in highlight_set:
            color = highlight_color
        elif i in sorted_indices:
            color = cfg.SORTED_COLOR
        else:
            color = cfg.BAR_COLOR

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)

    # タイトル描画
    if title:
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.0
        thickness = 4
        text_size = cv2.getTextSize(title, font, font_scale, thickness)[0]
        text_x = (cfg.WIDTH - text_size[0]) // 2
        text_y = cfg.TOP_MARGIN // 2 + text_size[1] // 2
        cv2.putText(frame, title, (text_x, text_y), font, font_scale, cfg.TEXT_COLOR, thickness)

    return frame


def _apply_event(
    values: list[int],
    event: SortEvent,
    sorted_indices: set[int],
) -> tuple[tuple[int, ...], str | None]:
    """イベントを配列に適用し、ハイライト情報を返す。

    Returns:
        (highlighted_indices, state) のタプル。
    """
    etype = event.type

    if etype is EventType.COMPARE:
        return event.indices, "compare"

    if etype is EventType.SWAP:
        i, j = event.indices
        values[i], values[j] = values[j], values[i]
        return event.indices, "swap"

    if etype is EventType.OVERWRITE:
        i = event.indices[0]
        val = event.values[0]
        values[i] = val
        return event.indices, None

    if etype is EventType.MARK_SORTED:
        for idx in event.indices:
            sorted_indices.add(idx)
        return (), None

    if etype is EventType.SHUFFLE:
        i, j = event.indices
        values[i], values[j] = values[j], values[i]
        return event.indices, "shuffle"

    return (), None


def render_bubble_sort_video(
    output_path: str,
    size: int = 32,
    seed: int = 42,
) -> str:
    """Bubble Sort の可視化動画を生成する。

    1. 整列済み配列を作る
    2. 冒頭 0〜2 秒でシャッフル
    3. Bubble Sort のイベント列を描画
    4. 最後に整列済み状態を静止表示

    Args:
        output_path: 出力 MP4 ファイルパス。
        size: 配列の要素数。
        seed: シャッフル用乱数シード。

    Returns:
        出力ファイルパス。
    """
    # ---- イベント列の準備 ----
    sorted_values = build_sorted_values(size)
    max_value = size  # 1..size なので最大値は size

    intro_frames = int(cfg.INTRO_SECONDS * cfg.FPS)

    shuffled_values, shuffle_events = build_intro_shuffle_events(
        sorted_values, shuffle_steps=intro_frames, seed=seed,
    )

    _, sort_events = bubble_sort(shuffled_values)

    # ---- VideoWriter ----
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, cfg.FPS, (cfg.WIDTH, cfg.HEIGHT))

    if not writer.isOpened():
        raise RuntimeError(f"VideoWriter を開けませんでした: {output_path}")

    try:
        # ---- Phase 1: 整列済み状態を数フレーム表示 ----
        initial_hold = cfg.FPS // 2  # 0.5 秒
        for _ in range(initial_hold):
            frame = render_bars_frame(
                list(sorted_values), max_value=max_value, title="Shuffle",
            )
            writer.write(frame)

        # ---- Phase 2: シャッフル演出 ----
        current = list(sorted_values)
        sorted_indices: set[int] = set()

        for event in shuffle_events:
            highlighted, state = _apply_event(current, event, sorted_indices)
            frame = render_bars_frame(
                current,
                max_value=max_value,
                highlighted_indices=highlighted,
                state=state,
                title="Shuffle",
            )
            writer.write(frame)

        # ---- Phase 3: Bubble Sort ----
        current = list(shuffled_values)
        sorted_indices = set()

        for event in sort_events:
            highlighted, state = _apply_event(current, event, sorted_indices)
            frame = render_bars_frame(
                current,
                max_value=max_value,
                highlighted_indices=highlighted,
                state=state,
                sorted_indices=sorted_indices,
                title="Bubble Sort",
            )
            writer.write(frame)

        # ---- Phase 4: 整列済み静止フレーム ----
        all_sorted = set(range(size))
        end_hold = cfg.FPS // 2  # 0.5 秒
        for _ in range(end_hold):
            frame = render_bars_frame(
                current,
                max_value=max_value,
                sorted_indices=all_sorted,
                title="Bubble Sort",
            )
            writer.write(frame)

    finally:
        writer.release()

    return output_path


def prepare_bubble_sort_events(
    size: int = 32,
    seed: int = 42,
) -> VideoEventPlan:
    """Bubble Sort 動画用のイベント列とフレーム構成情報を準備する。

    Args:
        size: 配列の要素数。
        seed: シャッフル用乱数シード。

    Returns:
        VideoEventPlan。
    """
    sorted_values = build_sorted_values(size)
    intro_frames = int(cfg.INTRO_SECONDS * cfg.FPS)

    shuffled_values, shuffle_events = build_intro_shuffle_events(
        sorted_values, shuffle_steps=intro_frames, seed=seed,
    )

    _, sort_events = bubble_sort(shuffled_values)

    return VideoEventPlan(
        shuffle_events=shuffle_events,
        sort_events=sort_events,
        initial_hold_frames=cfg.FPS // 2,
        end_hold_frames=cfg.FPS // 2,
        size=size,
        min_value=1,
        max_value=size,
    )


def render_bubble_sort_with_audio(
    output_dir: str,
    size: int = 32,
    seed: int = 42,
) -> str:
    """Bubble Sort の映像 + 音声付き最終 MP4 を生成する。

    1. 無音動画を生成
    2. イベント列から WAV を生成
    3. FFmpeg で合成して最終 MP4 を出力

    Args:
        output_dir: 出力ディレクトリ。
        size: 配列の要素数。
        seed: シャッフル用乱数シード。

    Returns:
        最終 MP4 のパス。
    """
    from src.render.audio import render_audio_track
    from src.render.compose import mux_video_and_audio

    os.makedirs(output_dir, exist_ok=True)

    video_path = os.path.join(output_dir, "bubble_sort_silent.mp4")
    wav_path = os.path.join(output_dir, "bubble_sort.wav")
    final_path = os.path.join(output_dir, "bubble_sort.mp4")

    # 1. イベント列を準備
    plan = prepare_bubble_sort_events(size=size, seed=seed)

    # 2. 無音動画を生成
    render_bubble_sort_video(video_path, size=size, seed=seed)

    # 3. 全イベントを結合して WAV を生成
    all_events = plan.shuffle_events + plan.sort_events
    render_audio_track(
        all_events,
        wav_path,
        min_value=plan.min_value,
        max_value=plan.max_value,
        frames_per_event=1,
        fps=cfg.FPS,
        pre_hold_frames=plan.initial_hold_frames,
        post_hold_frames=plan.end_hold_frames,
    )

    # 4. 合成
    mux_video_and_audio(video_path, wav_path, final_path)

    return final_path


# ===========================================================
# Bogo Sort
# ===========================================================


def render_bogo_sort_video(
    output_path: str,
    size: int = 5,
    seed: int = 42,
    sort_seed: int = 42,
) -> str:
    """Bogo Sort の可視化動画を生成する。

    Args:
        output_path: 出力 MP4 ファイルパス。
        size: 配列の要素数。
        seed: イントロシャッフル用乱数シード。
        sort_seed: ボゴソート内部シャッフル用乱数シード。

    Returns:
        出力ファイルパス。
    """
    sorted_values = build_sorted_values(size)
    max_value = size

    intro_frames = int(cfg.INTRO_SECONDS * cfg.FPS)

    shuffled_values, shuffle_events = build_intro_shuffle_events(
        sorted_values, shuffle_steps=intro_frames, seed=seed,
    )

    _, sort_events = bogo_sort(shuffled_values, seed=sort_seed)

    # ---- VideoWriter ----
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, cfg.FPS, (cfg.WIDTH, cfg.HEIGHT))

    if not writer.isOpened():
        raise RuntimeError(f"VideoWriter を開けませんでした: {output_path}")

    try:
        # Phase 1: 整列済み状態を 0.5 秒表示
        initial_hold = cfg.FPS // 2
        for _ in range(initial_hold):
            frame = render_bars_frame(
                list(sorted_values), max_value=max_value, title="Shuffle",
            )
            writer.write(frame)

        # Phase 2: シャッフル演出
        current = list(sorted_values)
        sorted_indices: set[int] = set()

        for event in shuffle_events:
            highlighted, state = _apply_event(current, event, sorted_indices)
            frame = render_bars_frame(
                current,
                max_value=max_value,
                highlighted_indices=highlighted,
                state=state,
                title="Shuffle",
            )
            writer.write(frame)

        # Phase 3: Bogo Sort
        current = list(shuffled_values)
        sorted_indices = set()

        for event in sort_events:
            highlighted, state = _apply_event(current, event, sorted_indices)
            frame = render_bars_frame(
                current,
                max_value=max_value,
                highlighted_indices=highlighted,
                state=state,
                sorted_indices=sorted_indices,
                title="Bogo Sort",
            )
            writer.write(frame)

        # Phase 4: 整列済み静止フレーム
        all_sorted = set(range(size))
        end_hold = cfg.FPS // 2
        for _ in range(end_hold):
            frame = render_bars_frame(
                current,
                max_value=max_value,
                sorted_indices=all_sorted,
                title="Bogo Sort",
            )
            writer.write(frame)

    finally:
        writer.release()

    return output_path


def prepare_bogo_sort_events(
    size: int = 5,
    seed: int = 42,
    sort_seed: int = 42,
) -> VideoEventPlan:
    """Bogo Sort 動画用のイベント列とフレーム構成情報を準備する。

    Args:
        size: 配列の要素数。
        seed: イントロシャッフル用乱数シード。
        sort_seed: ボゴソート内部シャッフル用乱数シード。

    Returns:
        VideoEventPlan。
    """
    sorted_values = build_sorted_values(size)
    intro_frames = int(cfg.INTRO_SECONDS * cfg.FPS)

    shuffled_values, shuffle_events = build_intro_shuffle_events(
        sorted_values, shuffle_steps=intro_frames, seed=seed,
    )

    _, sort_events = bogo_sort(shuffled_values, seed=sort_seed)

    return VideoEventPlan(
        shuffle_events=shuffle_events,
        sort_events=sort_events,
        initial_hold_frames=cfg.FPS // 2,
        end_hold_frames=cfg.FPS // 2,
        size=size,
        min_value=1,
        max_value=size,
    )
