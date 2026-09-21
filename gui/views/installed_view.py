"""
gui/views/installed_view.py — Overview and filterable list of installed applications
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from core.catalog import Catalog
from core.detector import Detector


class InstalledView(QWidget):
    def __init__(self, catalog: Catalog, detector: Detector, parent=None):
        super().__init__(parent)
        self.catalog = catalog
        self.detector = detector
        self.installed_items = []

        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Installed Applications")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f0f2f5;")
        self.subtitle = QLabel("Scanning installed packages and binaries...")
        self.subtitle.setStyleSheet("font-size: 13px; color: #9ba3af;")
        title_box.addWidget(title)
        title_box.addWidget(self.subtitle)
        header.addLayout(title_box)

        header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter installed...")
        self.search_input.setFixedWidth(240)
        self.search_input.setFixedHeight(34)
        self.search_input.textChanged.connect(self._on_filter_changed)
        header.addWidget(self.search_input)

        main_layout.addLayout(header)

        # Scroll area for items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)

        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll, stretch=1)

    def refresh(self):
        self.detector.clear_cache()
        self.installed_items.clear()

        for app in self.catalog.list_all():
            st, detail = self.detector.is_installed(app)
            if st == "installed":
                self.installed_items.append((app, detail))

        count = len(self.installed_items)
        self.subtitle.setText(f"{count} applications detected on your workstation.")
        self._render_items(self.installed_items)

    def _on_filter_changed(self):
        q = self.search_input.text().strip().lower()
        if not q:
            self._render_items(self.installed_items)
            return

        filtered = [
            item for item in self.installed_items
            if q in item[0].name.lower() or q in item[0].id.lower() or q in item[0].category.lower()
        ]
        self._render_items(filtered)

    def _render_items(self, items):
        # Clear layout
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        if not items:
            empty = QLabel("No installed applications matched.")
            empty.setStyleSheet("color: #646d7d; font-style: italic; padding: 12px 0;")
            self.content_layout.addWidget(empty)
            self.content_layout.addStretch()
            return

        for app, detail in items:
            row = QFrame()
            row.setStyleSheet("background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 6px; padding: 10px;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 6, 12, 6)

            icon_lbl = QLabel("✓")
            icon_lbl.setStyleSheet("color: #10b981; font-weight: bold; font-size: 14px;")
            rl.addWidget(icon_lbl)

            name_lbl = QLabel(f"<b>{app.name}</b> <span style='color: #646d7d;'>({app.id})</span>")
            name_lbl.setStyleSheet("font-size: 13px; color: #f0f2f5;")
            rl.addWidget(name_lbl)

            cat_badge = QLabel(app.category.capitalize())
            cat_badge.setStyleSheet("background-color: #232732; color: #9ba3af; border-radius: 4px; padding: 2px 6px; font-size: 11px;")
            rl.addWidget(cat_badge)

            rl.addStretch()

            detail_lbl = QLabel(detail)
            detail_lbl.setStyleSheet("color: #646d7d; font-size: 11px; font-family: monospace;")
            rl.addWidget(detail_lbl)

            self.content_layout.addWidget(row)

        self.content_layout.addStretch()
