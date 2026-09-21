"""
gui/app.py — Qt Application initialization and execution loop
"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.theme import STYLESHEET


def run_gui():
    """Start the envkit PySide6 graphical desktop application."""
    # Enable high-DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    app.setApplicationName("envkit")
    app.setApplicationDisplayName("envkit")
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(run_gui())
