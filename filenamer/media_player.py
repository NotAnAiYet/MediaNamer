"""Video playback via QMediaPlayer."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QObject, QTimer, QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import QApplication, QLabel

from filenamer.settings import AppSettings
from filenamer.widgets import SeekSlider, VideoPanel

SEEK_TOLERANCE_MS = 500


def format_time(ms: int) -> str:
    if ms < 0:
        ms = 0
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


class VideoPlayer(QObject):
    """Wraps QMediaPlayer with seekbar sync and first-frame preview."""

    def __init__(self, panel: VideoPanel, settings: AppSettings) -> None:
        super().__init__(panel)
        self._panel = panel
        self._settings = settings
        self._seeking = False
        self._video_at_end = False
        self._prime_first_frame = False
        self._first_frame_prime_started = False

        self._player = QMediaPlayer()
        self._audio = QAudioOutput()
        self._player.setAudioOutput(self._audio)
        self._audio.setVolume(0.4)

        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)

        panel.video.clicked.connect(self.toggle_playback)
        panel.seek_slider.sliderPressed.connect(self._on_seek_pressed)
        panel.seek_slider.sliderMoved.connect(self._on_seek_moved)
        panel.seek_slider.valueChanged.connect(self._seek_to)

        self._apply_loop_setting()

    @property
    def video_widget(self):
        return self._panel.video

    def _time_label(self) -> QLabel:
        return self._panel.time_label

    def _seek_slider(self) -> SeekSlider:
        return self._panel.seek_slider

    def _apply_loop_setting(self) -> None:
        loops = (
            QMediaPlayer.Loops.Infinite
            if self._settings.video_loop
            else QMediaPlayer.Loops.Once
        )
        self._player.setLoops(loops)

    def on_loop_changed(self) -> None:
        self._apply_loop_setting()

    def _update_time_label(self, position: int, duration: int) -> None:
        self._time_label().setText(f"{format_time(position)} / {format_time(duration)}")

    def _set_seek_slider(self, value: int) -> None:
        slider = self._seek_slider()
        slider.blockSignals(True)
        slider.setValue(value)
        slider.blockSignals(False)

    def _on_position_changed(self, position: int) -> None:
        if self._prime_first_frame:
            self._finish_first_frame_prime()
            position = 0

        if self._seeking:
            if abs(position - self._seek_slider().value()) < SEEK_TOLERANCE_MS:
                self._seeking = False
        else:
            self._set_seek_slider(position)

        self._update_time_label(position, self._player.duration())

    def _on_duration_changed(self, duration: int) -> None:
        self._seek_slider().setRange(0, max(0, duration))
        self._update_time_label(self._player.position(), duration)

    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        if (
            self._prime_first_frame
            and not self._first_frame_prime_started
            and status
            in {
                QMediaPlayer.MediaStatus.LoadedMedia,
                QMediaPlayer.MediaStatus.BufferedMedia,
            }
        ):
            self._first_frame_prime_started = True
            self._player.play()
            QTimer.singleShot(250, self._finish_first_frame_prime)
            return

        if status != QMediaPlayer.MediaStatus.EndOfMedia:
            return
        if self._settings.video_loop:
            return
        self._video_at_end = True
        self._player.pause()

    def _finish_first_frame_prime(self) -> None:
        if not self._prime_first_frame:
            return
        self._prime_first_frame = False
        self._player.pause()
        self._player.setPosition(0)
        self._set_seek_slider(0)
        self._update_time_label(0, self._player.duration())

    def _is_at_end(self) -> bool:
        if self._video_at_end:
            return True
        duration = self._player.duration()
        if duration <= 0:
            return False
        return self._player.position() >= duration - SEEK_TOLERANCE_MS

    def _restart(self) -> None:
        self._video_at_end = False
        self._seek_to(0)

    def _on_seek_pressed(self) -> None:
        self._seeking = True

    def _on_seek_moved(self, position: int) -> None:
        self._update_time_label(position, self._player.duration())

    def _seek_to(self, value: int) -> None:
        self._seeking = True
        self._set_seek_slider(value)
        self._player.setPosition(value)
        self._update_time_label(value, self._player.duration())
        duration = self._player.duration()
        if duration > 0 and value < duration - SEEK_TOLERANCE_MS:
            self._video_at_end = False

    def toggle_playback(self) -> None:
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            return

        if not self._settings.video_loop and self._is_at_end():
            self._restart()

        self._player.play()

    def load(self, path: Path) -> None:
        self._video_at_end = False
        self._prime_first_frame = not self._settings.video_autoplay
        self._first_frame_prime_started = False
        self._apply_loop_setting()
        self._player.setVideoOutput(self._panel.video)
        self._set_seek_slider(0)
        self._time_label().setText("0:00 / 0:00")
        self._player.setSource(QUrl.fromLocalFile(str(path.resolve())))

        if self._settings.video_autoplay:
            self._player.play()

    def release(self) -> None:
        """Stop playback and release file handles so files can be renamed."""
        self._prime_first_frame = False
        self._first_frame_prime_started = False
        self._player.pause()
        self._player.stop()
        self._player.setSource(QUrl())
        self._player.setVideoOutput(None)
        self._seek_slider().setRange(0, 0)
        self._set_seek_slider(0)
        self._time_label().setText("0:00 / 0:00")
        QApplication.processEvents()
        QApplication.processEvents()
