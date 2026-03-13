"""ffprobe based media metadata extraction."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.config import ensure_ffmpeg_available


@dataclass(frozen=True)
class AudioTrackInfo:
    """Audio stream metadata."""

    index: int
    codec_name: str | None
    channels: int | None
    sample_rate: int | None
    language: str | None


@dataclass(frozen=True)
class VideoProbeInfo:
    """Video container metadata extracted by ffprobe."""

    width: int
    height: int
    fps: float
    duration_sec: float
    audio_tracks: list[AudioTrackInfo]


def _parse_fraction(fraction: str | None) -> float:
    if not fraction or fraction == "0/0":
        return 0.0
    if "/" in fraction:
        num, den = fraction.split("/", maxsplit=1)
        den_value = float(den)
        return float(num) / den_value if den_value else 0.0
    return float(fraction)


def probe_media(input_path: str | Path) -> VideoProbeInfo:
    """Probe media and return width/height/fps/duration/audio streams."""
    binaries = ensure_ffmpeg_available()
    source = Path(input_path)

    cmd = [
        binaries.ffprobe,
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-print_format",
        "json",
        str(source),
    ]

    try:
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip()
        raise RuntimeError(f"ffprobe 実行に失敗しました: {message}") from exc

    payload: dict[str, Any] = json.loads(proc.stdout)
    streams = payload.get("streams", [])
    format_data = payload.get("format", {})

    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    if video_stream is None:
        raise RuntimeError("映像ストリームが見つかりませんでした。")

    fps = _parse_fraction(video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate"))
    duration = video_stream.get("duration") or format_data.get("duration") or 0

    audio_tracks = [
        AudioTrackInfo(
            index=int(track.get("index", -1)),
            codec_name=track.get("codec_name"),
            channels=int(track["channels"]) if track.get("channels") is not None else None,
            sample_rate=int(track["sample_rate"]) if track.get("sample_rate") else None,
            language=(track.get("tags") or {}).get("language"),
        )
        for track in streams
        if track.get("codec_type") == "audio"
    ]

    return VideoProbeInfo(
        width=int(video_stream.get("width", 0)),
        height=int(video_stream.get("height", 0)),
        fps=float(fps),
        duration_sec=float(duration),
        audio_tracks=audio_tracks,
    )
