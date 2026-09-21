"""
gui/widgets/app_card.py — Interactive application card widget for catalog
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from core.catalog import AppEntry


class AppCard(QFrame):
    selection_toggled = Signal(str, bool)  # (app_id, is_selected)

    def __init__(self, app: AppEntry, is_installed: bool, is_selected: bool = False, parent=None):
        super().__init__(parent)
        self.app = app
        self.is_installed = is_installed
        self.is_selected = is_selected

        self.setObjectName("appCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(115)
        self.setMaximumHeight(140)

        self._setup_ui()
        self._update_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header: Name + Category badge
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.name_label = QLabel(self.app.name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.cat_badge = QLabel(self.app.category.capitalize())
        self.cat_badge.setProperty("class", "badge")
        self.cat_badge.setStyleSheet(
            "background-color: #232732; color: #9ba3af; border-radius: 4px; padding: 2px 6px; font-size: 11px;"
        )

        header_layout.addWidget(self.name_label)
        header_layout.addStretch()
        header_layout.addWidget(self.cat_badge)
        layout.addLayout(header_layout)

        # Description
        self.desc_label = QLabel(self.app.description)
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #9ba3af; font-size: 12px;")
        layout.addWidget(self.desc_label)

        layout.addStretch()

        # Footer: Status Badge + Action Button
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(8)

        if self.is_installed:
            self.status_label = QLabel("✓ Installed")
            self.status_label.setStyleSheet(
                "background-color: #064e3b; color: #10b981; border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold;"
            )
        else:
            self.status_label = QLabel("Available")
            self.status_label.setStyleSheet(
                "background-color: #1a1d24; color: #646d7d; border-radius: 4px; padding: 2px 6px; font-size: 11px;"
            )
        footer_layout.addWidget(self.status_label)

        footer_layout.addStretch()

        self.select_btn = QPushButton()
        self.select_btn.setFixedHeight(28)
        self.select_btn.clicked.connect(self.toggle_selection)
        footer_layout.addWidget(self.select_btn)

        layout.addLayout(footer_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_selection()
        super().mousePressEvent(event)

    def toggle_selection(self):
        self.is_selected = not self.is_selected
        self._update_style()
        self.selection_toggled.emit(self.app.id, self.is_selected)

    def set_selected(self, selected: bool):
        if self.is_selected != selected:
            self.is_selected = selected
            self._update_style()

    def _update_style(self):
        if self.is_selected:
            self.setStyleSheet(
                "#appCard { background-color: #1a1d24; border: 1.5px solid #3b82f6; border-radius: 8px; }"
            )
            self.select_btn.setText("✓ Selected")
            self.select_btn.setStyleSheet(
                "background-color: #3b82f6; color: #ffffff; border: none; font-weight: bold; border-radius: 5px; padding: 4px 12px;"
            )
        else:
            self.setStyleSheet(
                "#appCard { background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 8px; }"
                "#appCard:hover { border: 1px solid #646d7d; background-color: #1e222a; }"
            )
            self.select_btn.setText("+ Select")
            self.select_btn.setStyleSheet(
                "background-color: #232732; color: #f0f2f5; border: 1px solid #2e3444; border-radius: 5px; padding: 4px 12px;"
            )
