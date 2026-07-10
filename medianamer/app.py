"""Application entry point."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from medianamer.main_window import MainWindow


def run() -> None:
    app = QApplication(sys.argv)
    app.setOrganizationName("MediaNamer")
    app.setApplicationName("MediaNamer")
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
