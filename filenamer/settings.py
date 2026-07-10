"""Application settings persisted between sessions."""

from __future__ import annotations

from PyQt6.QtCore import QSettings


def _read_bool(settings: QSettings, key: str, default: bool) -> bool:
    value = settings.value(key, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes")
    return bool(value)


class AppSettings:
    def __init__(self) -> None:
        self._settings = QSettings()

    @property
    def video_autoplay(self) -> bool:
        return _read_bool(self._settings, "video/autoplay", True)

    @video_autoplay.setter
    def video_autoplay(self, value: bool) -> None:
        self._settings.setValue("video/autoplay", value)
        self._settings.sync()

    @property
    def video_loop(self) -> bool:
        return _read_bool(self._settings, "video/loop", False)

    @video_loop.setter
    def video_loop(self, value: bool) -> None:
        self._settings.setValue("video/loop", value)
        self._settings.sync()
