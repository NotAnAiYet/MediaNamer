"""Main application window."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from medianamer.media_player import VideoPlayer
from medianamer.name_utils import is_image_file, is_media_file
from medianamer.preview import ImagePreview
from medianamer.rename import RenameError, RenameSession
from medianamer.settings import AppSettings
from medianamer.widgets import PreviewPanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MediaNamer")
        self.setMinimumSize(900, 650)

        self._settings = AppSettings()
        self._session = RenameSession()
        self._preview = PreviewPanel()
        self._image_preview = ImagePreview(self._preview.image_label)
        self._video = VideoPlayer(self._preview.video_panel, self._settings)

        self._build_ui()
        self._build_menu()

    def _build_menu(self) -> None:
        settings_menu = self.menuBar().addMenu("&Settings")

        autoplay = QAction("Video &autoplay", self)
        autoplay.setCheckable(True)
        autoplay.setChecked(self._settings.video_autoplay)
        autoplay.triggered.connect(self._on_autoplay_changed)
        settings_menu.addAction(autoplay)

        loop = QAction("Video &loop", self)
        loop.setCheckable(True)
        loop.setChecked(self._settings.video_loop)
        loop.triggered.connect(self._on_loop_changed)
        settings_menu.addAction(loop)

        settings_menu.addSeparator()

        include_subfolders = QAction("Include &subfolders", self)
        include_subfolders.setCheckable(True)
        include_subfolders.setChecked(self._settings.include_subfolders)
        include_subfolders.triggered.connect(self._on_include_subfolders_changed)
        settings_menu.addAction(include_subfolders)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(12)
        root.setContentsMargins(16, 16, 16, 16)

        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("Folder:"))
        self._folder_input = QLineEdit()
        self._folder_input.setPlaceholderText("Select or paste a folder path…")
        self._folder_input.returnPressed.connect(self._load_folder_from_input)
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse_folder)
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self._load_folder_from_input)
        folder_row.addWidget(self._folder_input, stretch=1)
        folder_row.addWidget(browse_btn)
        folder_row.addWidget(load_btn)
        root.addLayout(folder_row)

        self._status_label = QLabel("Choose a folder to begin.")
        self._status_label.setStyleSheet("color: #666;")
        root.addWidget(self._status_label)

        root.addWidget(self._preview, stretch=1)

        self._current_name_label = QLabel("Current name: —")
        self._current_name_label.setWordWrap(True)
        self._current_name_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        root.addWidget(self._current_name_label)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("New name:"))
        self._new_name_input = QLineEdit()
        self._new_name_input.setPlaceholderText(
            "Enter a descriptive name (extension added automatically)"
        )
        self._new_name_input.returnPressed.connect(self._save_current)
        name_row.addWidget(self._new_name_input, stretch=1)
        root.addLayout(name_row)

        action_row = QHBoxLayout()
        action_row.addStretch()
        self._skip_btn = QPushButton("Skip")
        self._skip_btn.setMinimumWidth(120)
        self._skip_btn.clicked.connect(self._skip_current)
        self._save_btn = QPushButton("Save && Next")
        self._save_btn.setMinimumWidth(140)
        self._save_btn.setDefault(True)
        self._save_btn.clicked.connect(self._save_current)
        action_row.addWidget(self._skip_btn)
        action_row.addWidget(self._save_btn)
        root.addLayout(action_row)

        self._set_workflow_enabled(False)
        self._preview.show_empty()

    def _set_workflow_enabled(self, enabled: bool) -> None:
        self._new_name_input.setEnabled(enabled)
        self._save_btn.setEnabled(enabled)
        self._skip_btn.setEnabled(enabled)

    def _on_autoplay_changed(self, checked: bool) -> None:
        self._settings.video_autoplay = checked

    def _on_loop_changed(self, checked: bool) -> None:
        self._settings.video_loop = checked
        self._video.on_loop_changed()

    def _on_include_subfolders_changed(self, checked: bool) -> None:
        self._settings.include_subfolders = checked
        folder_text = self._folder_input.text().strip().strip('"')
        if folder_text and Path(folder_text).is_dir():
            self._load_folder(Path(folder_text))

    def _browse_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select folder")
        if folder:
            self._folder_input.setText(folder)
            self._load_folder(Path(folder))

    def _load_folder_from_input(self) -> None:
        text = self._folder_input.text().strip().strip('"')
        if not text:
            QMessageBox.information(self, "No folder", "Please enter or browse to a folder.")
            return
        self._load_folder(Path(text))

    def _load_folder(self, folder: Path) -> None:
        if not folder.is_dir():
            QMessageBox.warning(self, "Invalid folder", f"Folder not found:\n{folder}")
            return

        self._video.release()
        self._image_preview.clear()
        self._folder_input.setText(str(folder))
        count = self._session.load(folder, include_subfolders=self._settings.include_subfolders)

        if count == 0:
            self._set_workflow_enabled(False)
            self._preview.show_empty()
            self._current_name_label.setText("Current name: —")
            self._new_name_input.clear()
            self._status_label.setText(
                f"No media files with non-descriptive names found in:\n{folder}"
            )
            return

        self._status_label.setText(f"Found {count} file(s) to rename in {folder}")
        self._set_workflow_enabled(True)
        self._show_current_file()

    def _show_current_file(self) -> None:
        if self._session.is_done():
            self._on_queue_finished()
            return

        path = self._session.current()
        assert path is not None

        self._status_label.setText(
            f"File {self._session.index + 1} of {self._session.count}"
            f"  ·  {self._session.remaining} remaining"
        )
        self._current_name_label.setText(f"Current name: {self._display_path(path)}")
        self._new_name_input.clear()
        self._new_name_input.setFocus()

        if is_image_file(path):
            self._show_image(path)
        elif is_media_file(path):
            self._show_video(path)
        else:
            self._preview.show_empty()

    def _display_path(self, path: Path) -> str:
        folder = self._session.folder
        if folder is not None:
            try:
                return str(path.relative_to(folder))
            except ValueError:
                pass
        return path.name

    def _show_image(self, path: Path) -> None:
        self._video.release()
        self._preview.show_image()
        self._image_preview.show(path, self._preview.size())

    def _show_video(self, path: Path) -> None:
        self._image_preview.clear()
        self._preview.show_video()
        self._video.load(path)

    def _skip_current(self) -> None:
        self._video.release()
        self._session.skip()
        self._show_current_file()

    def _save_current(self) -> None:
        new_stem = self._new_name_input.text().strip()
        try:
            self._session.validate_rename(new_stem)
        except RenameError as exc:
            if "Enter a new name" in str(exc):
                QMessageBox.information(self, "No name entered", str(exc))
            else:
                QMessageBox.warning(self, "Cannot rename", str(exc))
            return

        self._release_before_rename()

        try:
            self._session.rename(new_stem)
        except RenameError as exc:
            QMessageBox.warning(self, "Rename failed", str(exc))
            self._show_current_file()
            return

        self._show_current_file()

    def _release_before_rename(self) -> None:
        path = self._session.current()
        if path and is_image_file(path):
            self._image_preview.clear()
            self._preview.show_empty()
        elif path and not is_image_file(path):
            self._preview.show_empty()
        self._video.release()

    def _on_queue_finished(self) -> None:
        self._set_workflow_enabled(False)
        self._preview.show_empty()
        self._current_name_label.setText("Current name: —")
        self._new_name_input.clear()
        self._status_label.setText("All files processed. Load another folder or rescan.")
        QMessageBox.information(self, "Done", "No more files to rename in this folder.")

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        path = self._session.current()
        if path and is_image_file(path):
            self._show_image(path)

    def closeEvent(self, event) -> None:  # noqa: N802
        self._video.release()
        self._image_preview.clear()
        super().closeEvent(event)
