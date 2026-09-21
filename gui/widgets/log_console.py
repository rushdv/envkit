"""
gui/widgets/log_console.py — Real-time streaming log console widget
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class LogConsole(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Header bar
        header = QHBoxLayout()
        title = QLabel("Installation Logs")
        title.setStyleSheet("font-weight: bold; font-size: 12px; color: #9ba3af;")
        header.addWidget(title)

        header.addStretch()

        self.copy_btn = QPushButton("Copy Logs")
        self.copy_btn.setFixedHeight(26)
        self.copy_btn.setStyleSheet("font-size: 11px; padding: 2px 8px;")
        self.copy_btn.clicked.connect(self.copy_logs)
        header.addWidget(self.copy_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedHeight(26)
        self.clear_btn.setStyleSheet("font-size: 11px; padding: 2px 8px;")
        self.clear_btn.clicked.connect(self.clear)
        header.addWidget(self.clear_btn)

        layout.addLayout(header)

        # Text area
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet(
            "background-color: #0b0d11; color: #d1d5db; font-family: monospace; font-size: 11px; border: 1px solid #2e3444; border-radius: 6px; padding: 6px;"
        )
        layout.addWidget(self.text_area)

    def append_line(self, line: str):
        self.text_area.append(line)
        self.text_area.verticalScrollBar().setValue(
            self.text_area.verticalScrollBar().maximum()
        )

    def clear(self):
        self.text_area.clear()

    def copy_logs(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_area.toPlainText())
        orig = self.copy_btn.text()
        self.copy_btn.setText("✓ Copied!")
        self.copy_btn.setEnabled(False)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: (self.copy_btn.setText(orig), self.copy_btn.setEnabled(True)))
