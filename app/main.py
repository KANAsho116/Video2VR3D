"""Application bootstrap for Video2VR3D."""

from __future__ import annotations

from ui.main_window import MainWindow


def main() -> None:
    """Launch the UI shell."""
    window = MainWindow()
    window.run()


if __name__ == "__main__":
    main()
