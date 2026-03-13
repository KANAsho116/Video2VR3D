# Video2VR3D

## プロジェクト概要

Video2VR3D は、通常の動画から VR 向け立体視映像への変換パイプラインを段階的に構築するプロジェクトです。
現在は **Milestone 0** として、最小限のアプリ骨組みと UI 起動導線を整備しています。

## 現時点の実装範囲（Milestone 0）

- ディレクトリ構成を初期化（`app/`, `models/`, `scripts/`, `docs/`, `tests/`, `benchmarks/`）。
- `app/core/` 配下に以下の空モジュールを作成。
  - `ingest`
  - `depth`
  - `temporal`
  - `stereo`
  - `comfort`
  - `encode`
- UI エントリとして `app/ui/main_window.py` を作成。
- `app/main.py` から UI を起動可能な状態に設定。

## 起動手順

1. Python 3.10 以上を用意します。
2. プロジェクトルートで以下を実行します。

```bash
python app/main.py
```

3. `Video2VR3D - Milestone 0` というタイトルのウィンドウが表示されれば成功です。

## Milestone 0 の通過条件

- **空実装であっても、`python app/main.py` の起動で画面が開くこと**を最初の通過条件とします。
- 機能実装（推論・変換・エンコード）は次マイルストーン以降で段階的に追加します。
