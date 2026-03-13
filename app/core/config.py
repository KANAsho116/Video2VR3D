"""Runtime configuration utilities."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_FILES = (
    Path("video2vr3d.config.json"),
    Path("config/video2vr3d.config.json"),
)


@dataclass(frozen=True)
class FFmpegBinaries:
    """Resolved FFmpeg executable paths."""

    ffmpeg: str
    ffprobe: str


class FFmpegNotFoundError(RuntimeError):
    """Raised when ffmpeg/ffprobe binaries are unavailable."""


def _load_config_file(config_path: Path | None = None) -> dict[str, Any]:
    """Load JSON config file if present."""
    if config_path is not None:
        candidates = (config_path,)
    else:
        env_path = os.getenv("VIDEO2VR3D_CONFIG")
        candidates = (Path(env_path),) if env_path else DEFAULT_CONFIG_FILES

    for candidate in candidates:
        if candidate.is_file():
            with candidate.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
            if isinstance(data, dict):
                return data
            raise ValueError(f"設定ファイルが辞書形式ではありません: {candidate}")
    return {}


def detect_ffmpeg_binaries(config_path: Path | None = None) -> FFmpegBinaries:
    """Resolve ffmpeg and ffprobe paths from config file or PATH.

    Priority:
    1. JSON config file (`ffmpeg.ffmpeg_path`, `ffmpeg.ffprobe_path`)
    2. Environment variables (`FFMPEG_PATH`, `FFPROBE_PATH`)
    3. PATH lookup (`ffmpeg`, `ffprobe`)
    """
    config = _load_config_file(config_path)
    ffmpeg_cfg = config.get("ffmpeg", {}) if isinstance(config, dict) else {}

    ffmpeg_value = ffmpeg_cfg.get("ffmpeg_path") or os.getenv("FFMPEG_PATH")
    ffprobe_value = ffmpeg_cfg.get("ffprobe_path") or os.getenv("FFPROBE_PATH")

    ffmpeg_path = ffmpeg_value or shutil.which("ffmpeg")
    ffprobe_path = ffprobe_value or shutil.which("ffprobe")

    if not ffmpeg_path or not ffprobe_path:
        hint = (
            "FFmpeg が見つかりません。`ffmpeg` と `ffprobe` を PATH に追加するか、"
            "設定ファイル（video2vr3d.config.json）の `ffmpeg.ffmpeg_path` / "
            "`ffmpeg.ffprobe_path` を指定してください。"
        )
        raise FFmpegNotFoundError(hint)

    return FFmpegBinaries(ffmpeg=str(ffmpeg_path), ffprobe=str(ffprobe_path))


def ensure_ffmpeg_available(config_path: Path | None = None) -> FFmpegBinaries:
    """Validate ffmpeg availability before execution."""
    return detect_ffmpeg_binaries(config_path=config_path)
