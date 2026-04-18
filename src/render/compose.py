"""映像と音声の合成。

無音 MP4 と WAV を FFmpeg で結合し、最終 MP4 を出力する。
"""

from __future__ import annotations

import os
import subprocess


def mux_video_and_audio(
    video_path: str,
    audio_path: str,
    output_path: str,
) -> str:
    """無音動画と WAV を合成して最終 MP4 を出力する。

    Args:
        video_path: 無音 MP4 のパス。
        audio_path: WAV のパス。
        output_path: 出力 MP4 のパス。

    Returns:
        出力ファイルパス。

    Raises:
        FileNotFoundError: 入力ファイルが存在しない場合。
        RuntimeError: FFmpeg の実行に失敗した場合。
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"音声ファイルが見つかりません: {audio_path}")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "faststart",
        output_path,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg が失敗しました (exit code {result.returncode}):\n{result.stderr}"
        )

    return output_path
