"""音声レンダラ (sonification)。

イベント列を受け取り、値→周波数変換した短音を並べて WAV を生成する。
"""

from __future__ import annotations

import os

import numpy as np
from scipy.io import wavfile

from src.core.events import EventType, SortEvent

# ---- 音声定数 ----
SAMPLE_RATE: int = 44100

# イベント種別ごとの音の長さ (秒)
EVENT_DURATION_COMPARE: float = 0.025
EVENT_DURATION_SWAP: float = 0.035
EVENT_DURATION_OVERWRITE: float = 0.030
EVENT_DURATION_MARK_SORTED: float = 0.050
EVENT_DURATION_SHUFFLE: float = 0.020

MASTER_VOLUME: float = 0.30
FADE_MS: int = 5

# 周波数マッピング範囲 (Hz)
MIN_FREQ: float = 220.0
MAX_FREQ: float = 880.0


def value_to_frequency(
    value: int,
    min_value: int,
    max_value: int,
    min_freq: float = MIN_FREQ,
    max_freq: float = MAX_FREQ,
) -> float:
    """値を周波数へ線形変換する。

    Args:
        value: 変換対象の値。
        min_value: 値の最小値。
        max_value: 値の最大値。
        min_freq: 最小周波数 (Hz)。
        max_freq: 最大周波数 (Hz)。

    Returns:
        周波数 (Hz)。
    """
    if min_value == max_value:
        return (min_freq + max_freq) / 2.0
    t = (value - min_value) / (max_value - min_value)
    return min_freq + t * (max_freq - min_freq)


def generate_tone(
    frequency: float,
    duration_sec: float,
    sample_rate: int = SAMPLE_RATE,
    volume: float = MASTER_VOLUME,
    fade_ms: int = FADE_MS,
) -> np.ndarray:
    """正弦波トーンを生成する。

    fade in / fade out を適用し、クリックノイズを防止する。

    Args:
        frequency: 周波数 (Hz)。
        duration_sec: 長さ (秒)。
        sample_rate: サンプルレート。
        volume: 音量 (0.0〜1.0)。
        fade_ms: fade in / out の長さ (ミリ秒)。

    Returns:
        float32 の 1 次元配列。
    """
    n_samples = max(1, int(duration_sec * sample_rate))
    t = np.arange(n_samples, dtype=np.float32) / sample_rate
    wave = np.sin(2.0 * np.pi * frequency * t, dtype=np.float32) * volume

    # fade in / fade out
    fade_samples = min(int(fade_ms * sample_rate / 1000), n_samples // 2)
    if fade_samples > 0:
        fade_in = np.linspace(0.0, 1.0, fade_samples, dtype=np.float32)
        fade_out = np.linspace(1.0, 0.0, fade_samples, dtype=np.float32)
        wave[:fade_samples] *= fade_in
        wave[-fade_samples:] *= fade_out

    return wave


def generate_event_audio(
    event: SortEvent,
    min_value: int,
    max_value: int,
    sample_rate: int = SAMPLE_RATE,
) -> np.ndarray:
    """イベント 1 件に対応する短音を生成する。

    Args:
        event: ソートイベント。
        min_value: 配列の最小値。
        max_value: 配列の最大値。
        sample_rate: サンプルレート。

    Returns:
        float32 の 1 次元配列。
    """
    etype = event.type

    if etype is EventType.COMPARE:
        dur = EVENT_DURATION_COMPARE
        if len(event.values) >= 2:
            f1 = value_to_frequency(event.values[0], min_value, max_value)
            f2 = value_to_frequency(event.values[1], min_value, max_value)
            # 2 音を重ねる (和音)
            t1 = generate_tone(f1, dur, sample_rate, volume=MASTER_VOLUME * 0.6)
            t2 = generate_tone(f2, dur, sample_rate, volume=MASTER_VOLUME * 0.6)
            n = max(len(t1), len(t2))
            mixed = np.zeros(n, dtype=np.float32)
            mixed[: len(t1)] += t1
            mixed[: len(t2)] += t2
            return mixed
        return generate_tone(440.0, dur, sample_rate, volume=MASTER_VOLUME * 0.5)

    if etype is EventType.SWAP:
        dur = EVENT_DURATION_SWAP
        vol = MASTER_VOLUME * 1.0  # compare より強め
        if len(event.values) >= 2:
            f1 = value_to_frequency(event.values[0], min_value, max_value)
            f2 = value_to_frequency(event.values[1], min_value, max_value)
            t1 = generate_tone(f1, dur, sample_rate, volume=vol * 0.7)
            t2 = generate_tone(f2, dur, sample_rate, volume=vol * 0.7)
            n = max(len(t1), len(t2))
            mixed = np.zeros(n, dtype=np.float32)
            mixed[: len(t1)] += t1
            mixed[: len(t2)] += t2
            return mixed
        return generate_tone(440.0, dur, sample_rate, volume=vol)

    if etype is EventType.OVERWRITE:
        dur = EVENT_DURATION_OVERWRITE
        if len(event.values) >= 1:
            freq = value_to_frequency(event.values[0], min_value, max_value)
        else:
            freq = 440.0
        return generate_tone(freq, dur, sample_rate, volume=MASTER_VOLUME * 0.8)

    if etype is EventType.MARK_SORTED:
        dur = EVENT_DURATION_MARK_SORTED
        # 高めの完了音
        return generate_tone(660.0, dur, sample_rate, volume=MASTER_VOLUME * 0.4)

    if etype is EventType.SHUFFLE:
        dur = EVENT_DURATION_SHUFFLE
        if len(event.values) >= 2:
            f1 = value_to_frequency(event.values[0], min_value, max_value)
            f2 = value_to_frequency(event.values[1], min_value, max_value)
            freq = (f1 + f2) / 2.0
        elif len(event.values) == 1:
            freq = value_to_frequency(event.values[0], min_value, max_value)
        else:
            freq = 440.0
        return generate_tone(freq, dur, sample_rate, volume=MASTER_VOLUME * 0.5)

    # 未知のイベントは無音
    return np.zeros(1, dtype=np.float32)


def render_audio_track(
    events: list[SortEvent],
    output_wav_path: str,
    min_value: int,
    max_value: int,
    *,
    frames_per_event: int = 1,
    fps: int = 30,
    pre_hold_frames: int = 0,
    post_hold_frames: int = 0,
    sample_rate: int = SAMPLE_RATE,
    tail_seconds: float = 0.5,
) -> str:
    """イベント列全体から 1 本の WAV を生成する。

    タイミングは「1 イベント = frames_per_event / fps 秒」で計算し、
    動画側のフレーム進行と同期させる。

    Args:
        events: イベント列。
        output_wav_path: 出力 WAV パス。
        min_value: 配列の最小値。
        max_value: 配列の最大値。
        frames_per_event: 1 イベントあたりの動画フレーム数。
        fps: 動画のフレームレート。
        pre_hold_frames: イベント描画前の静止フレーム数 (無音)。
        post_hold_frames: イベント描画後の静止フレーム数 (無音)。
        sample_rate: サンプルレート。
        tail_seconds: 末尾に付加する無音時間。

    Returns:
        出力 WAV パス。
    """
    sec_per_event = frames_per_event / fps
    samples_per_event = int(sec_per_event * sample_rate)

    pre_samples = int(pre_hold_frames / fps * sample_rate)
    post_samples = int(post_hold_frames / fps * sample_rate)
    tail_samples = int(tail_seconds * sample_rate)

    total_event_samples = len(events) * samples_per_event
    total_samples = pre_samples + total_event_samples + post_samples + tail_samples

    track = np.zeros(total_samples, dtype=np.float32)

    for idx, event in enumerate(events):
        tone = generate_event_audio(event, min_value, max_value, sample_rate)
        start = pre_samples + idx * samples_per_event
        end = min(start + len(tone), total_samples)
        tone_len = end - start
        if tone_len > 0:
            track[start:end] += tone[:tone_len]

    # クリッピング防止: ピーク正規化
    peak = np.max(np.abs(track))
    if peak > 1.0:
        track /= peak
    elif peak > 0.0 and peak < 0.5:
        # 小さすぎる場合は少し持ち上げる
        track *= 0.8 / peak

    # 16bit PCM へ変換
    pcm = np.clip(track * 32767.0, -32768, 32767).astype(np.int16)

    os.makedirs(os.path.dirname(output_wav_path) or ".", exist_ok=True)
    wavfile.write(output_wav_path, sample_rate, pcm)

    return output_wav_path
