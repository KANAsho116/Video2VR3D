# Quality Metrics（暫定）

本ドキュメントは Milestone 0〜1 の暫定的な品質計測方法を定義します。正式な閾値は後続マイルストーンで更新予定です。

## 1. 深度フリッカー回数

### 定義
- 連続フレーム間で深度マップの差分が急増したイベント回数。

### 暫定計測方法
1. 深度推定済みフレーム列 `D_t` を取得。
2. `Δ_t = mean(abs(D_t - D_{t-1}))` を計算。
3. `Δ_t` が動画全体中央値の `k` 倍（暫定 `k=2.5`）を超えたフレームをフリッカー候補とする。
4. 連続候補は 1 イベントにマージし、総イベント数を `depth_flicker_count` として記録。

### 出力例
- `depth_flicker_count`: 7
- `depth_flicker_per_min`: 2.3

## 2. VRAM ピーク

### 定義
- 1 本の動画処理中に観測された GPU メモリ使用量の最大値（MiB）。

### 暫定計測方法
- NVIDIA GPU 環境では `nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits` を 1 秒ごとにポーリング。
- 推論開始からエンコード完了までの最大値を `vram_peak_mib` とする。
- 複数 GPU の場合は処理対象デバイスのみを採用。

### 出力例
- `vram_peak_mib`: 6120

## 3. Milestone 0 完了判定（自動チェック）

`python scripts/run_benchmark.py` 実行時に、各入力動画で以下をチェックします。

1. **メタデータ取得**: `ffprobe` で `format/streams` を取得できること。
2. **横縦判定**: 動画ストリームの `width/height` から `landscape/portrait/square` 判定できること。
3. **音声抽出**: `ffmpeg` で WAV を抽出できること。

各チェック結果は `logs/YYYYMMDD_HHMMSS/results.jsonl` の `milestone0_checks` に真偽値で保存します。

## 4. ログ保存ルール

- ラン単位ディレクトリ: `logs/YYYYMMDD_HHMMSS/`
- ケースごとの逐次ログ: `results.jsonl`
- ラン集計: `summary.json`
- 音声抽出物（検証用）: `audio/*.wav`
- 失敗時は `stacktrace` を `results.jsonl` に保存

