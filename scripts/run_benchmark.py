#!/usr/bin/env python3
"""Video2VR3D benchmark runner.

- benchmarks/cases.yaml を読み込んでケースを実行
- 処理時間 / 成否 / 出力パスを収集
- logs/YYYYMMDD_HHMMSS/results.jsonl に逐次出力
- 失敗時は stacktrace を記録
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import time
import traceback
from pathlib import Path
from typing import Any

import yaml


class BenchmarkError(RuntimeError):
    """ベンチマーク実行時エラー。"""


def _run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def _load_cases(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    categories = data.get("categories", [])
    flat_cases: list[dict[str, Any]] = []

    for category in categories:
        category_id = category.get("id", "unknown")
        for case in category.get("cases", []):
            case["category_id"] = category_id
            flat_cases.append(case)

    return flat_cases


def _ffprobe_metadata(video_path: Path, ffprobe_bin: str) -> dict[str, Any]:
    cmd = [
        ffprobe_bin,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ]
    result = _run_cmd(cmd)
    if result.returncode != 0:
        raise BenchmarkError(f"ffprobe failed: {result.stderr.strip()}")

    return json.loads(result.stdout)


def _detect_orientation(metadata: dict[str, Any]) -> str:
    streams = metadata.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    if not video_stream:
        raise BenchmarkError("video stream not found")

    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))
    if width <= 0 or height <= 0:
        raise BenchmarkError(f"invalid resolution width={width}, height={height}")

    if width > height:
        return "landscape"
    if width < height:
        return "portrait"
    return "square"


def _extract_audio(video_path: Path, out_dir: Path, ffmpeg_bin: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{video_path.stem}.wav"
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        str(out_path),
    ]
    result = _run_cmd(cmd)
    if result.returncode != 0:
        raise BenchmarkError(f"ffmpeg audio extraction failed: {result.stderr.strip()}")
    return out_path


def _check_milestone0(
    video_path: Path,
    ffprobe_bin: str,
    ffmpeg_bin: str,
    audio_out_dir: Path,
) -> dict[str, Any]:
    checks: dict[str, Any] = {
        "metadata_retrieval": False,
        "orientation_detection": False,
        "audio_extraction": False,
    }

    metadata = _ffprobe_metadata(video_path, ffprobe_bin)
    checks["metadata_retrieval"] = True

    orientation = _detect_orientation(metadata)
    checks["orientation_detection"] = True

    audio_path = _extract_audio(video_path, audio_out_dir, ffmpeg_bin)
    checks["audio_extraction"] = True

    return {
        "checks": checks,
        "orientation": orientation,
        "audio_output_path": str(audio_path),
        "metadata": metadata,
    }


def run_benchmark(args: argparse.Namespace) -> int:
    cases = _load_cases(Path(args.cases))

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(args.log_root) / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    result_file = run_dir / "results.jsonl"
    audio_out_dir = run_dir / "audio"

    total = len(cases)
    success_count = 0

    with result_file.open("w", encoding="utf-8") as f:
        for idx, case in enumerate(cases, start=1):
            video_path = Path(case["path"])
            record: dict[str, Any] = {
                "timestamp": dt.datetime.now().isoformat(),
                "index": idx,
                "total": total,
                "category_id": case.get("category_id"),
                "case_id": case.get("case_id"),
                "input_path": str(video_path),
                "success": False,
                "duration_sec": 0.0,
                "output_path": None,
                "milestone0_checks": {
                    "metadata_retrieval": False,
                    "orientation_detection": False,
                    "audio_extraction": False,
                },
                "error": None,
                "stacktrace": None,
            }

            started = time.perf_counter()
            try:
                if not video_path.exists():
                    raise BenchmarkError(f"input not found: {video_path}")

                milestone_result = _check_milestone0(
                    video_path=video_path,
                    ffprobe_bin=args.ffprobe,
                    ffmpeg_bin=args.ffmpeg,
                    audio_out_dir=audio_out_dir,
                )
                record["milestone0_checks"] = milestone_result["checks"]
                record["orientation"] = milestone_result["orientation"]
                record["output_path"] = milestone_result["audio_output_path"]

                record["success"] = all(milestone_result["checks"].values())
                if record["success"]:
                    success_count += 1

            except Exception as exc:  # noqa: BLE001
                record["error"] = str(exc)
                record["stacktrace"] = traceback.format_exc()
            finally:
                record["duration_sec"] = round(time.perf_counter() - started, 4)
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                f.flush()

    summary = {
        "timestamp": ts,
        "total": total,
        "success": success_count,
        "failed": total - success_count,
        "results_path": str(result_file),
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["failed"] == 0 else 1


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Video2VR3D benchmark runner")
    p.add_argument("--cases", default="benchmarks/cases.yaml", help="ケース定義 YAML")
    p.add_argument("--log-root", default="logs", help="ログ出力ルート")
    p.add_argument("--ffprobe", default="ffprobe", help="ffprobe 実行ファイル")
    p.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg 実行ファイル")
    return p


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    return run_benchmark(args)


if __name__ == "__main__":
    raise SystemExit(main())
