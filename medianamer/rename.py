"""File rename workflow and validation."""

from __future__ import annotations

import os
import re
from pathlib import Path

from medianamer.name_utils import find_files_needing_rename

INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]')


class RenameError(Exception):
    """Raised when a rename cannot be performed."""


def validate_new_name(stem: str) -> str | None:
    """Return an error message, or None if the name is valid."""
    if not stem or not stem.strip():
        return "Enter a new name or press Skip to move on."

    if INVALID_FILENAME_CHARS.search(stem):
        return 'The name cannot contain any of these characters:\n< > : " / \\ | ? *'

    return None


class RenameSession:
    """Tracks the queue of files to rename in a folder."""

    def __init__(self) -> None:
        self._folder: Path | None = None
        self._queue: list[Path] = []
        self._index = 0

    @property
    def folder(self) -> Path | None:
        return self._folder

    @property
    def index(self) -> int:
        return self._index

    @property
    def count(self) -> int:
        return len(self._queue)

    @property
    def remaining(self) -> int:
        return max(0, len(self._queue) - self._index)

    def load(self, folder: Path) -> int:
        self._folder = folder
        self._queue = find_files_needing_rename(folder)
        self._index = 0
        return len(self._queue)

    def current(self) -> Path | None:
        if 0 <= self._index < len(self._queue):
            return self._queue[self._index]
        return None

    def is_done(self) -> bool:
        return self._index >= len(self._queue)

    def skip(self) -> None:
        self._index += 1

    def validate_rename(self, new_stem: str) -> Path:
        path = self.current()
        if path is None:
            raise RenameError("No file selected.")

        error = validate_new_name(new_stem)
        if error:
            raise RenameError(error)

        new_name = new_stem.strip() + path.suffix
        new_path = path.parent / new_name

        if new_path.exists() and new_path != path:
            raise RenameError(f'A file named "{new_name}" already exists in this folder.')

        return new_path

    def rename(self, new_stem: str) -> Path:
        path = self.current()
        if path is None:
            raise RenameError("No file selected.")

        new_path = self.validate_rename(new_stem)

        try:
            os.rename(path, new_path)
        except OSError as exc:
            raise RenameError(str(exc)) from exc

        self._index += 1
        return new_path
