"""動画描画用の設定定数。

解像度・fps・色・マージンなど、映像レンダラが参照する値をまとめる。
色は OpenCV の BGR タプルで定義する。
"""

from __future__ import annotations

# ---- 解像度・フレームレート ----
WIDTH: int = 1080
HEIGHT: int = 1920
FPS: int = 30

# ---- イントロ ----
INTRO_SECONDS: float = 2.0

# ---- 色 (BGR) ----
BACKGROUND_COLOR: tuple[int, int, int] = (30, 30, 30)       # ダークグレー
BAR_COLOR: tuple[int, int, int] = (200, 200, 200)           # ライトグレー
COMPARE_COLOR: tuple[int, int, int] = (0, 200, 255)         # オレンジ (BGR)
SWAP_COLOR: tuple[int, int, int] = (50, 50, 255)            # 赤系
SORTED_COLOR: tuple[int, int, int] = (50, 200, 50)          # 緑
SHUFFLE_COLOR: tuple[int, int, int] = (255, 180, 0)         # 水色系
TEXT_COLOR: tuple[int, int, int] = (255, 255, 255)           # 白

# ---- レイアウト (px) ----
TOP_MARGIN: int = 200       # タイトル表示用の上部余白
BOTTOM_MARGIN: int = 80     # 下部余白
SIDE_MARGIN: int = 40       # 左右余白
BAR_GAP: int = 2            # 棒と棒の間のギャップ
