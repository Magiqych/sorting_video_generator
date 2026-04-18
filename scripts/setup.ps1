<#
.SYNOPSIS
    Sorting Video Generator のセットアップスクリプト
.DESCRIPTION
    Python 仮想環境の作成、pip の更新、依存パッケージのインストールを行います。
    FFmpeg の存在確認と確認手順の案内も表示します。
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot ".venv"
$RequirementsPath = Join-Path $ProjectRoot "requirements.txt"
$OutputPath = Join-Path $ProjectRoot "output"

Write-Host "=== Sorting Video Generator Setup ===" -ForegroundColor Cyan

# Python の存在確認
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[ERROR] Python が見つかりません。Python 3.11 系を推奨します。" -ForegroundColor Red
    exit 1
}

$pythonVersion = & python --version 2>&1
Write-Host "[INFO] $pythonVersion を検出しました。" -ForegroundColor Green

# 仮想環境の作成
if (Test-Path $VenvPath) {
    Write-Host "[INFO] 仮想環境が既に存在します: $VenvPath" -ForegroundColor Yellow
} else {
    Write-Host "[INFO] 仮想環境を作成しています..." -ForegroundColor Cyan
    & python -m venv $VenvPath
    Write-Host "[INFO] 仮想環境を作成しました: $VenvPath" -ForegroundColor Green
}

# 仮想環境を有効化
$activateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Host "[ERROR] 仮想環境の Activate スクリプトが見つかりません。" -ForegroundColor Red
    exit 1
}
& $activateScript

# pip のアップグレード
Write-Host "[INFO] pip をアップグレードしています..." -ForegroundColor Cyan
& python -m pip install --upgrade pip

# 依存パッケージのインストール
Write-Host "[INFO] 依存パッケージをインストールしています..." -ForegroundColor Cyan
& pip install -r $RequirementsPath

# output ディレクトリの作成
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath | Out-Null
    Write-Host "[INFO] output ディレクトリを作成しました。" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== セットアップ完了 ===" -ForegroundColor Cyan
Write-Host ""

# FFmpeg の確認案内
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) {
    Write-Host "[WARN] FFmpeg が PATH 上に見つかりません。" -ForegroundColor Yellow
    Write-Host "       動画生成には FFmpeg が必要です。以下のいずれかでインストールしてください:" -ForegroundColor Yellow
    Write-Host "         winget install Gyan.FFmpeg" -ForegroundColor White
    Write-Host "         scoop install ffmpeg" -ForegroundColor White
} else {
    Write-Host "[INFO] FFmpeg を検出しました。" -ForegroundColor Green
}

Write-Host ""
Write-Host "FFmpeg の動作確認:" -ForegroundColor White
Write-Host "  ffmpeg -version" -ForegroundColor White
Write-Host ""
Write-Host "仮想環境を有効化するには:" -ForegroundColor White
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
