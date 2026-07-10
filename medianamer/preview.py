"""Image preview display."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtWidgets import QLabel


class ImagePreview:
    """Shows a scaled image in a QLabel, with animation for GIFs."""

    def __init__(self, label: QLabel) -> None:
        self._label = label
        self._movie: QMovie | None = None

    def show(self, path: Path, area_size: QSize) -> bool:
        self.clear()

        if path.suffix.lower() == ".gif":
            return self._show_gif(path, area_size)

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

    def _show_gif(self, path: Path, area_size: QSize) -> bool:
        movie = QMovie(str(path))
        if not movie.isValid():
            self._label.setText(f"Could not load image:\n{path.name}")
            return False

        movie.jumpToFrame(0)
        frame_size = movie.currentImage().size()
        if frame_size.isEmpty():
            frame_size = movie.scaledSize()

        if not frame_size.isEmpty():
            scaled = frame_size.scaled(area_size, Qt.AspectRatioMode.KeepAspectRatio)
            movie.setScaledSize(scaled)

        self._movie = movie
        self._label.setMovie(movie)
        movie.start()
        return True

    def clear(self) -> None:
        if self._movie is not None:
            self._movie.stop()
            self._movie = None
        self._label.setMovie(None)
        self._label.clear()
