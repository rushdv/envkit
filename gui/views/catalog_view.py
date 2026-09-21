"""
gui/views/catalog_view.py — Searchable and filterable application catalog view
"""

from typing import Dict, List, Optional, Set
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from core.catalog import AppEntry, Catalog
from core.detector import Detector
from gui.widgets.app_card import AppCard


class CatalogView(QWidget):
    review_requested = Signal(list)  # list of app_ids

    def __init__(self, catalog: Catalog, detector: Detector, parent=None):
        super().__init__(parent)
        self.catalog = catalog
        self.detector = detector
        self.selected_app_ids: Set[str] = set()
        self.active_category = "all"
        self.cards: Dict[str, AppCard] = {}

        self._setup_ui()
        self._populate_grid()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 16)
        main_layout.setSpacing(14)

        # Top Bar: Search input + Checkbox filters
        top_bar = QHBoxLayout()
        top_bar.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search applications by name, description, tags, or command...")
        self.search_input.setFixedHeight(38)
        self.search_input.textChanged.connect(self._on_search_changed)
        top_bar.addWidget(self.search_input, stretch=3)

        self.hide_installed_cb = QCheckBox("Hide installed")
        self.hide_installed_cb.stateChanged.connect(self._apply_filters)
        top_bar.addWidget(self.hide_installed_cb)

        self.only_selected_cb = QCheckBox("Show only selected")
        self.only_selected_cb.stateChanged.connect(self._apply_filters)
        top_bar.addWidget(self.only_selected_cb)

        main_layout.addLayout(top_bar)

        # Category Filter Pills / Buttons
        self.cat_bar = QHBoxLayout()
        self.cat_bar.setSpacing(6)
        self.cat_btn_group = QButtonGroup(self)
        self.cat_btn_group.setExclusive(True)

        categories = [
            ("all", "All"),
            ("development", "Development"),
            ("terminal", "Terminal"),
            ("browsers", "Browsers"),
            ("security", "Security"),
            ("student", "Student"),
            ("media", "Media"),
            ("communication", "Communication"),
            ("utilities", "Utilities")
        ]

        self.cat_buttons = {}
        for cat_id, title in categories:
            btn = QPushButton(title)
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setStyleSheet(
                "QPushButton { background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 15px; padding: 4px 12px; font-size: 12px; }"
                "QPushButton:checked { background-color: #3b82f6; color: #ffffff; border: none; font-weight: bold; }"
                "QPushButton:hover:!checked { background-color: #232732; }"
            )
            if cat_id == "all":
                btn.setChecked(True)
            btn.clicked.connect(lambda _, c=cat_id: self.set_category(c))
            self.cat_btn_group.addButton(btn)
            self.cat_bar.addWidget(btn)
            self.cat_buttons[cat_id] = btn

        self.cat_bar.addStretch()
        main_layout.addLayout(self.cat_bar)

        # Scroll Area for Application Cards Grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(12)

        self.scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(self.scroll_area, stretch=1)

        # Bottom Review & Action Bar
        self.bottom_bar = QFrame()
        self.bottom_bar.setFixedHeight(54)
        self.bottom_bar.setStyleSheet(
            "QFrame { background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 8px; padding: 8px 16px; }"
        )
        bottom_layout = QHBoxLayout(self.bottom_bar)
        bottom_layout.setContentsMargins(8, 4, 8, 4)

        self.counter_label = QLabel("0 applications selected")
        self.counter_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #f0f2f5;")
        bottom_layout.addWidget(self.counter_label)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedHeight(30)
        self.clear_btn.setStyleSheet("background-color: transparent; border: none; color: #9ba3af; text-decoration: underline;")
        self.clear_btn.clicked.connect(self.clear_selection)
        bottom_layout.addWidget(self.clear_btn)

        bottom_layout.addStretch()

        self.review_btn = QPushButton("Review & Install →")
        self.review_btn.setFixedHeight(36)
        self.review_btn.setEnabled(False)
        self.review_btn.setStyleSheet(
            "QPushButton { background-color: #3b82f6; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 6px 18px; }"
            "QPushButton:disabled { background-color: #232732; color: #646d7d; }"
            "QPushButton:hover:!disabled { background-color: #2563eb; }"
        )
        self.review_btn.clicked.connect(self._on_review_clicked)
        bottom_layout.addWidget(self.review_btn)

        main_layout.addWidget(self.bottom_bar)

    def _populate_grid(self):
        apps = self.catalog.list_all()
        for app in apps:
            is_inst = (self.detector.is_installed(app)[0] == "installed")
            card = AppCard(app, is_installed=is_inst, is_selected=(app.id in self.selected_app_ids))
            card.selection_toggled.connect(self._on_card_selection_toggled)
            self.cards[app.id] = card

        self._relayout_grid(apps)

    def _relayout_grid(self, visible_apps: List[AppEntry]):
        # Clear existing layout items
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        row = 0
        col = 0
        cols_count = 2  # 2 columns of cards for clean readability

        for app in visible_apps:
            card = self.cards.get(app.id)
            if card:
                self.grid_layout.addWidget(card, row, col)
                col += 1
                if col >= cols_count:
                    col = 0
                    row += 1

        self.grid_layout.setRowStretch(row + 1, 1)

    def _on_search_changed(self):
        self._apply_filters()

    def set_category(self, category_id: str):
        self.active_category = category_id
        btn = self.cat_buttons.get(category_id)
        if btn and not btn.isChecked():
            btn.setChecked(True)
        self._apply_filters()

    def _apply_filters(self):
        query = self.search_input.text().strip()
        hide_installed = self.hide_installed_cb.isChecked()
        only_selected = self.only_selected_cb.isChecked()

        # Step 1: Base search or all
        if query:
            base_apps = self.catalog.search(query)
        else:
            base_apps = self.catalog.list_all()

        # Step 2: Category filter
        if self.active_category != "all":
            base_apps = [a for a in base_apps if a.category.lower() == self.active_category.lower()]

        # Step 3: Checkbox filters
        filtered = []
        for app in base_apps:
            is_inst = (self.detector.is_installed(app)[0] == "installed")
            is_sel = (app.id in self.selected_app_ids)

            if hide_installed and is_inst:
                continue
            if only_selected and not is_sel:
                continue
            filtered.append(app)

        self._relayout_grid(filtered)

    def _on_card_selection_toggled(self, app_id: str, is_selected: bool):
        if is_selected:
            self.selected_app_ids.add(app_id)
        else:
            self.selected_app_ids.discard(app_id)
        self._update_counter()

    def select_apps(self, app_ids: List[str]):
        """Programmatically select a list of app IDs (e.g. from profile)."""
        for aid in app_ids:
            if aid in self.catalog.apps:
                self.selected_app_ids.add(aid)
                card = self.cards.get(aid)
                if card:
                    card.set_selected(True)
        self._update_counter()

    def clear_selection(self):
        self.selected_app_ids.clear()
        for card in self.cards.values():
            card.set_selected(False)
        self._update_counter()

    def _update_counter(self):
        count = len(self.selected_app_ids)
        plural = "application" if count == 1 else "applications"
        self.counter_label.setText(f"{count} {plural} selected")
        self.review_btn.setEnabled(count > 0)
        self.clear_btn.setVisible(count > 0)

    def _on_review_clicked(self):
        self.review_requested.emit(list(self.selected_app_ids))
