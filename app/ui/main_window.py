"""UI entrypoint for Video2VR3D Milestone 0."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class MainWindow:
    """Simple UI shell for Milestone 0."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Video2VR3D - Milestone 0")
        self.root.geometry("640x360")

        container = ttk.Frame(self.root, padding=24)
        container.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(
            container,
            text="Video2VR3D",
            font=("Arial", 20, "bold"),
        )
        title.pack(anchor=tk.W)

        subtitle = ttk.Label(
            container,
            text="Milestone 0: UI シェル起動確認",
            font=("Arial", 12),
        )
        subtitle.pack(anchor=tk.W, pady=(8, 24))

        status = ttk.Label(
            container,
            text="現時点では空実装です。次のマイルストーンで機能を追加します。",
            wraplength=560,
        )
        status.pack(anchor=tk.W)

    def run(self) -> None:
        """Start the UI event loop."""
        self.root.mainloop()
