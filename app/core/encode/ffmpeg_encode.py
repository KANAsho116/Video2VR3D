"""FFmpeg encode command builder."""

from __future__ import annotations

from pathlib import Path

from app.core.config import ensure_ffmpeg_available


def build_h265_encode_command(
    input_path: str | Path,
    output_path: str | Path,
    *,
    crf: int = 20,
    preset: str = "medium",
    keep_audio: bool = True,
    overwrite: bool = True,
) -> list[str]:
    """Build FFmpeg command for MP4(H.265) encode with optional audio passthrough."""
    binaries = ensure_ffmpeg_available()

    cmd = [binaries.ffmpeg]
    cmd.append("-y" if overwrite else "-n")
    cmd.extend(["-i", str(Path(input_path))])
    cmd.extend(["-c:v", "libx265", "-preset", preset, "-crf", str(crf)])

    if keep_audio:
        cmd.extend(["-c:a", "copy"])
    else:
        cmd.extend(["-an"])

    cmd.extend(["-movflags", "+faststart", "-pix_fmt", "yuv420p", str(Path(output_path))])
    return cmd
