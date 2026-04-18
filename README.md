# Sorting Video Generator

ソートアルゴリズムを可視化する **縦長 9:16 ショート動画** を自動生成する Python プロジェクトです。

---

## 1. プロジェクト概要

- 各種ソートアルゴリズムの動作を、棒グラフアニメーション + sonification（値→周波数変換の短音）で表現する
- アルゴリズムごとに 1 本ずつ動画を生成する
- 音声は TTS ではなく **sonification** — 配列の値を周波数にマッピングした短い正弦波を鳴らす
- SNS ショート動画としてそのまま公開できる縦長 MP4 を出力する

## 2. 目的

ソートアルゴリズムの比較・交換・上書きといった操作を、視覚（棒グラフの色と動き）と聴覚（値に対応した周波数の短音）の両面でわかりやすく伝えること。

## 3. 仕様（FIX）

| 項目 | 値 |
|---|---|
| アスペクト比 | 9:16（縦長） |
| 解像度 | 1080 × 1920 |
| フレームレート | 30 fps |
| 動画形式 | MP4 (H.264 + AAC) |
| 音声方式 | sonification（値→周波数→短い正弦波） |
| 生成単位 | アルゴリズム別に 1 本ずつ |

### 動画構成

| 区間 | 内容 |
|---|---|
| 0 〜 2 秒 | **シャッフルフェーズ** — 整列済みの棒グラフをランダムにばらす。シャッフル中も値に対応する周波数の音を鳴らす |
| 2 秒〜 | **ソートフェーズ** — 対象アルゴリズムでソートしていく様子をアニメーションと音で表現 |

### イベント駆動設計

アルゴリズムの実行は **イベント列** を中心に設計します。

| イベント | 説明 |
|---|---|
| `compare` | 2 つの要素を比較 |
| `swap` | 2 つの要素を交換 |
| `overwrite` | 要素を上書き |
| `mark_sorted` | 要素がソート済みであることをマーク |
| `shuffle` | シャッフル操作 |

映像レンダラと音声レンダラはこのイベント列を受け取り、それぞれフレームとサンプルを生成します。

## 4. 採用技術と役割

| 技術 | 役割 |
|---|---|
| **OpenCV** (`cv2`) | 棒グラフの描画・フレーム生成 |
| **NumPy** | 配列操作・音声波形の数値計算 |
| **SciPy** | WAV 書き出し・信号処理補助 |
| **Pillow** | テキスト描画・画像加工の補助 |
| **ffmpeg-python** | FFmpeg コマンド組み立て・映像＋音声の最終合成 |
| **FFmpeg** (外部) | 実際のエンコード・mux 処理 |

## 5. 推奨 Python バージョン

- **Python 3.11 系** を推奨
- 3.10 以上であれば動作する想定

## 6. 使い方（CLI）

仮想環境を有効化した状態で実行します。

```powershell
# バブルソート動画を生成（デフォルト: 要素数 32, seed 42）
python -m src.main --algorithm bubble

# 要素数・シードを指定
python -m src.main --algorithm bubble --size 64 --seed 0

# 出力パスを指定
python -m src.main --algorithm bubble --output output/my_video.mp4

# 無音動画のみ生成
python -m src.main --algorithm bubble --silent-only

# 音声 (WAV) のみ生成
python -m src.main --algorithm bubble --audio-only

# 中間ファイルを残す
python -m src.main --algorithm bubble --keep-intermediate
```

### CLI オプション一覧

| オプション | 型 | デフォルト | 説明 |
|---|---|---|---|
| `--algorithm` | str | (必須) | ソートアルゴリズム名 (`bubble`) |
| `--size` | int | 32 | 配列の要素数 |
| `--seed` | int | 42 | シャッフル用乱数シード |
| `--output` | str | 自動 | 出力 MP4/WAV パス |
| `--output-dir` | str | `output` | 出力ディレクトリ |
| `--keep-intermediate` | flag | false | 中間ファイル (無音 MP4, WAV) を残す |
| `--silent-only` | flag | false | 無音動画のみ生成 |
| `--audio-only` | flag | false | WAV 音声のみ生成 |
| `--intro-shuffle-steps` | int | 自動 | イントロシャッフル回数 |

## 7. セットアップ手順（Windows PowerShell）

### 前提

- Python 3.11 系がインストール済みであること
- FFmpeg がインストール済みで `PATH` に通っていること

### FFmpeg のインストール（未導入の場合）

```powershell
# winget を使う場合
winget install Gyan.FFmpeg

# scoop を使う場合
scoop install ffmpeg
```

### セットアップ

```powershell
# 1. リポジトリをクローン
git clone <リポジトリURL>
cd sorting_video_generator

# 2. セットアップスクリプトを実行
.\scripts\setup.ps1

# 3. FFmpeg が使えるか確認
ffmpeg -version
```

`scripts/setup.ps1` は以下を自動で行います:

1. `.venv` 仮想環境の作成
2. 仮想環境の有効化
3. `pip` のアップグレード
4. `requirements.txt` からパッケージインストール
5. `output/` ディレクトリの作成

手動でセットアップする場合:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
ffmpeg -version
```

## 8. ディレクトリ構成

```
sorting_video_generator/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── scripts/
│   └── setup.ps1           # Windows PowerShell セットアップスクリプト
├── src/
│   ├── __init__.py
│   ├── __main__.py          # python -m src エントリポイント
│   ├── main.py              # CLI 引数解析・生成フロー
│   ├── algorithms/
│   │   ├── __init__.py
│   │   └── bubble_sort.py   # バブルソート
│   ├── core/
│   │   ├── __init__.py
│   │   ├── array.py         # SortArray ラッパー
│   │   ├── config.py        # 定数・設定値
│   │   ├── events.py        # SortEvent データクラス
│   │   └── intro.py         # イントロシャッフル
│   └── render/
│       ├── __init__.py
│       ├── audio.py         # 音声レンダラ (sonification)
│       ├── compose.py       # FFmpeg 映像+音声合成
│       └── video.py         # 映像レンダラ (OpenCV)
├── tests/                   # pytest テスト
└── output/                  # 生成動画出力先（git 管理外）
```

## 9. モジュール方針

| モジュール | 責務 | 状態 |
|---|---|---|
| `src/core/` | `SortEvent` データクラス、`SortArray` ラッパー、設定値、イントロ | 実装済み |
| `src/algorithms/` | 各ソートアルゴリズムの実装（バブルソート対応済み） | 実装済み (bubble) |
| `src/render/` | 映像レンダラ (OpenCV)、音声レンダラ (sonification)、FFmpeg 合成 | 実装済み |
| `src/main.py` | CLI エントリポイント・引数解析・生成フロー | 実装済み |
| `scripts/` | セットアップ・ビルド補助スクリプト | 実装済み |

## 10. 実装方針

- ソートアルゴリズムは **ジェネレータ関数** として実装し、各操作を `SortEvent` として `yield` する
- レンダラはイベント列を受け取り、フレーム列（映像）とサンプル列（音声）を生成する
- 映像と音声は独立に生成し、最後に FFmpeg (`ffmpeg-python`) で合成する
- 設定値（解像度・fps・配列サイズ・色など）は定数 or config として一箇所にまとめる
- アルゴリズム追加時はジェネレータ関数を 1 つ追加するだけで済む設計にする

## 11. 実装済み

- `src/core/` — SortEvent データクラス、SortArray ラッパー、config、イントロシャッフル
- `src/algorithms/` — バブルソート
- `src/render/` — OpenCV 映像レンダラ、sonification 音声レンダラ、FFmpeg 合成
- CLI エントリポイント (`src/main.py`)
- テスト (`tests/`)

## 12. 今後実装予定

### 対応予定アルゴリズム

- [x] バブルソート
- [ ] 選択ソート
- [ ] 挿入ソート
- [ ] マージソート
- [ ] クイックソート
- [ ] ヒープソート
- [ ] シェルソート
- [ ] 基数ソート

### 実装ロードマップ

1. ~~`src/core/` — `SortEvent` データクラスと `SortArray` ラッパーの実装~~ ✅
2. ~~`src/algorithms/` — バブルソートを最初の 1 本として実装~~ ✅
3. ~~`src/render/` — OpenCV 映像レンダラの実装~~ ✅
4. ~~`src/render/` — NumPy/SciPy 音声レンダラ（sonification）の実装~~ ✅
5. ~~FFmpeg による映像 + 音声合成パイプラインの実装~~ ✅
6. ~~CLI エントリポイント (`src/main.py`) の実装~~ ✅
7. 残りのソートアルゴリズムの追加
8. テストの拡充

## ライセンス

[LICENSE](LICENSE) を参照してください。
