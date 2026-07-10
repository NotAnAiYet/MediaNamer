"""Custom Qt widgets for media preview."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSlider,
    QStackedWidget,
    QStyle,
    QVBoxLayout,
    QWidget,
)


class ClickableVideoWidget(QVideoWidget):
    """Video preview that toggles playback on click."""

    clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class SeekSlider(QSlider):
    """Slider that jumps to the clicked position on the track."""

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.maximum() > self.minimum()
            and self.width() > 0
        ):
            value = QStyle.sliderValueFromPosition(
                self.minimum(),
                self.maximum(),
                int(event.position().x()),
                self.width(),
            )
            self.setValue(value)
        super().mousePressEvent(event)


class VideoPanel(QWidget):
    """Video preview with seekbar and time display."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.video = ClickableVideoWidget()
        layout.addWidget(self.video, stretch=1)

        controls = QHBoxLayout()
        self.time_label = QLabel("0:00 / 0:00")
        self.time_label.setMinimumWidth(90)
        self.seek_slider = SeekSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 0)
        controls.addWidget(self.time_label)
        controls.addWidget(self.seek_slider, stretch=1)
        layout.addLayout(controls)

    def set_controls_enabled(self, enabled: bool) -> None:
        self.seek_slider.setEnabled(enabled)
        self.video.setEnabled(enabled)


class PreviewPanel(QStackedWidget):
    """Stacked empty, image, and video preview pages."""

    PAGE_EMPTY = 0
    PAGE_IMAGE = 1
    PAGE_VIDEO = 2

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(380)
        self.setStyleSheet("QStackedWidget { background: #1e1e1e; border-radius: 8px; }")

        self.empty_label = QLabel("No file loaded")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #aaa; font-size: 14px;")

        self.image_label = QLabel("No preview")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("color: #aaa; font-size: 14px;")
        self.image_label.setScaledContents(False)

        self.video_panel = VideoPanel()

        self.addWidget(self.empty_label)
        self.addWidget(self.image_label)
        self.addWidget(self.video_panel)

    def show_empty(self) -> None:
        self.setCurrentIndex(self.PAGE_EMPTY)
        self.video_panel.set_controls_enabled(False)

    def show_image(self) -> None:
        self.setCurrentIndex(self.PAGE_IMAGE)
        self.video_panel.set_controls_enabled(False)

    def show_video(self) -> None:
        self.setCurrentIndex(self.PAGE_VIDEO)
        self.video_panel.set_controls_enabled(True)
