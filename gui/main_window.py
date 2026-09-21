"""
gui/main_window.py — Main window orchestrating sidebar navigation and views
"""

from typing import List
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from core.catalog import Catalog
from core.detector import Detector
from core.distro import DistroInfo, detect_distro
from gui.views.about_view import AboutView
from gui.views.catalog_view import CatalogView
from gui.views.home_view import HomeView
from gui.views.install_view import InstallView
from gui.views.installed_view import InstalledView
from gui.views.profiles_view import ProfilesView
from gui.views.review_view import ReviewView
from gui.views.settings_view import SettingsView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("envkit — Workstation Setup")
        self.resize(1080, 720)
        self.setMinimumSize(900, 600)

        # Core engine state
        self.distro_info: DistroInfo = detect_distro()
        self.catalog = Catalog()
        self.detector = Detector(self.distro_info)

        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(4)

        title = QLabel("envkit")
        title.setObjectName("sidebarTitle")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #3b82f6; padding-left: 8px;")

        sub = QLabel("Workstation Builder")
        sub.setObjectName("sidebarSubtitle")
        sub.setStyleSheet("font-size: 11px; color: #646d7d; padding-left: 8px; margin-bottom: 12px;")

        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(sub)

        self.nav_list = QListWidget()
        self.nav_list.setObjectName("navList")
        self.nav_list.setFocusPolicy(Qt.NoFocus)

        nav_items = [
            ("🏠  Home", 0),
            ("📦  Applications", 1),
            ("📋  Profiles", 4),
            ("✓  Installed", 5),
            ("⚙️  Settings", 6),
            ("ℹ️  About", 7),
        ]

        for text, page_idx in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, page_idx)
            self.nav_list.addItem(item)

        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch()

        # Distro badge in sidebar footer
        footer_badge = QLabel(f"🐧 {self.distro_info.pretty_name.split()[0]}")
        footer_badge.setStyleSheet("color: #646d7d; font-size: 11px; padding: 8px;")
        sidebar_layout.addWidget(footer_badge)

        main_layout.addWidget(sidebar)

        # 2. Right Content Stack
        self.stack = QStackedWidget()

        # Instantiate Views
        self.home_view = HomeView(self.distro_info, self.catalog, self.detector)
        self.catalog_view = CatalogView(self.catalog, self.detector)
        self.review_view = ReviewView(self.distro_info, self.catalog, self.detector)
        self.install_view = InstallView(self.distro_info, self.catalog, self.detector)
        self.profiles_view = ProfilesView()
        self.installed_view = InstalledView(self.catalog, self.detector)
        self.settings_view = SettingsView(self.distro_info)
        self.about_view = AboutView(self.distro_info)

        # Wire View Signals
        self.home_view.navigate_requested.connect(self._handle_home_navigation)
        self.catalog_view.review_requested.connect(self._handle_catalog_review)
        self.review_view.back_requested.connect(lambda: self.switch_to_page(1))
        self.review_view.install_confirmed.connect(self._handle_install_confirmed)
        self.install_view.done_requested.connect(self._handle_install_done)
        self.profiles_view.profile_selected.connect(self._handle_profile_selected)

        # Add to stack in index order
        self.stack.addWidget(self.home_view)       # 0
        self.stack.addWidget(self.catalog_view)    # 1
        self.stack.addWidget(self.review_view)     # 2
        self.stack.addWidget(self.install_view)    # 3
        self.stack.addWidget(self.profiles_view)   # 4
        self.stack.addWidget(self.installed_view)  # 5
        self.stack.addWidget(self.settings_view)   # 6
        self.stack.addWidget(self.about_view)      # 7

        main_layout.addWidget(self.stack, stretch=1)

        # Select Home by default
        self.nav_list.setCurrentRow(0)

    def _on_nav_changed(self, row: int):
        item = self.nav_list.item(row)
        if item:
            page_idx = item.data(Qt.UserRole)
            self.stack.setCurrentIndex(page_idx)
            if page_idx == 5:
                self.installed_view.refresh()

    def switch_to_page(self, page_idx: int):
        self.stack.setCurrentIndex(page_idx)
        # Highlight corresponding sidebar item if applicable
        for i in range(self.nav_list.count()):
            item = self.nav_list.item(i)
            if item.data(Qt.UserRole) == page_idx:
                self.nav_list.setCurrentRow(i)
                break

    def _handle_home_navigation(self, target: str, param: str):
        if target == "catalog":
            self.switch_to_page(1)
            if param:
                self.catalog_view.set_category(param)
        elif target == "profiles":
            self.switch_to_page(4)
        elif target == "installed":
            self.switch_to_page(5)

    def _handle_catalog_review(self, app_ids: List[str]):
        self.review_view.set_selected_apps(app_ids)
        self.switch_to_page(2)

    def _handle_install_confirmed(self, app_ids: List[str], pin_taskbar: bool):
        self.install_view.start_installation(app_ids, pin_taskbar=pin_taskbar)
        self.switch_to_page(3)

    def _handle_install_done(self):
        self.detector.clear_cache()
        self.catalog_view.clear_selection()
        self.switch_to_page(0)

    def _handle_profile_selected(self, app_ids: List[str]):
        self.catalog_view.select_apps(app_ids)
        self.switch_to_page(1)
