"""Image preview display."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel


class ImagePreview:
    """Shows a scaled image in a QLabel."""

    def __init__(self, label: QLabel) -> None:
        self._label = label

    def show(self, path: Path, area_size: QSize) -> bool:
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            self._label.setText(f"Could not load image:\n{path.name}")
            return False

        scaled = pixmap.scaled(
            area_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label.setPixmap(scaled)
        return True

    def clear(self) -> None:
        self._label.clear()
