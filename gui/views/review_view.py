"""
gui/views/review_view.py — Pre-installation confirmation and diff summary screen
"""

from typing import List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from core.catalog import Catalog
from core.detector import Detector
from core.distro import DistroInfo


class ReviewView(QWidget):
    back_requested = Signal()
    install_confirmed = Signal(list, bool)  # (app_ids_to_install, pin_taskbar)

    def __init__(self, distro_info: DistroInfo, catalog: Catalog, detector: Detector, parent=None):
        super().__init__(parent)
        self.distro_info = distro_info
        self.catalog = catalog
        self.detector = detector
        self.selected_app_ids: List[str] = []

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(20)

        # Title
        title_box = QVBoxLayout()
        title = QLabel("Installation Summary & Review")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f0f2f5;")
        subtitle = QLabel("Review selected applications and estimated changes before proceeding.")
        subtitle.setStyleSheet("font-size: 13px; color: #9ba3af;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        main_layout.addLayout(title_box)

        # Distro Banner
        distro_card = QFrame()
        distro_card.setStyleSheet("background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 8px; padding: 12px;")
        distro_card_l = QHBoxLayout(distro_card)
        self.distro_label = QLabel()
        self.distro_label.setStyleSheet("font-size: 13px; color: #f0f2f5;")
        distro_card_l.addWidget(self.distro_label)
        main_layout.addWidget(distro_card)

        # Scroll area for review lists
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)

        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll, stretch=1)

        # Options Box (Taskbar pinning)
        opts_box = QFrame()
        opts_box.setStyleSheet("background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 8px; padding: 12px;")
        opts_layout = QVBoxLayout(opts_box)
        opts_layout.setSpacing(6)

        self.pin_taskbar_cb = QCheckBox("Pin newly installed applications to desktop taskbar / favorites")
        self.pin_taskbar_cb.setChecked(False)  # Explicitly default unchecked as required by prompt
        opts_note = QLabel("Note: envkit will never modify your desktop favorites without your explicit consent.")
        opts_note.setStyleSheet("color: #646d7d; font-size: 11px; padding-left: 22px;")

        opts_layout.addWidget(self.pin_taskbar_cb)
        opts_layout.addWidget(opts_note)
        main_layout.addWidget(opts_box)

        # Bottom Button Bar
        btn_bar = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Catalog")
        self.back_btn.setFixedHeight(40)
        self.back_btn.setStyleSheet("background-color: #232732; color: #f0f2f5; border: 1px solid #2e3444; border-radius: 6px; padding: 8px 18px;")
        self.back_btn.clicked.connect(self.back_requested.emit)
        btn_bar.addWidget(self.back_btn)

        btn_bar.addStretch()

        self.install_btn = QPushButton("Install Now →")
        self.install_btn.setFixedHeight(40)
        self.install_btn.setStyleSheet("background-color: #3b82f6; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 8px 24px;")
        self.install_btn.clicked.connect(self._on_install_clicked)
        btn_bar.addWidget(self.install_btn)

        main_layout.addLayout(btn_bar)

    def set_selected_apps(self, app_ids: List[str]):
        self.selected_app_ids = app_ids
        self._refresh_summary()

    def _refresh_summary(self):
        # Update distro label
        self.distro_label.setText(
            f"Target: <b>{self.distro_info.pretty_name}</b>  •  Package Manager: <b>{self.distro_info.package_manager}</b>  •  Desktop: <b>{self.distro_info.desktop}</b>"
        )

        # Clear previous layout
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        already_installed = []
        will_install = []

        for aid in self.selected_app_ids:
            app = self.catalog.get(aid)
            if not app:
                continue
            status, detail = self.detector.is_installed(app)
            if status == "installed":
                already_installed.append((app, detail))
            else:
                action = self.catalog.resolve_install_action(app.id, self.distro_info)
                will_install.append((app, action))

        # 1. Section: Will Install
        will_card = QFrame()
        will_card.setStyleSheet("background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 8px; padding: 16px;")
        wl = QVBoxLayout(will_card)
        wl.setSpacing(10)

        will_title = QLabel(f"📦 Will Install ({len(will_install)} applications)")
        will_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #3b82f6;")
        wl.addWidget(will_title)

        if will_install:
            for app, action in will_install:
                row = QHBoxLayout()
                row.setSpacing(8)
                name = QLabel(f"<b>{app.name}</b> ({app.id})")
                name.setStyleSheet("font-size: 13px; color: #f0f2f5;")
                desc = QLabel(f"— via {action.manager_name} ({' '.join(action.packages) if action.packages else 'script'})")
                desc.setStyleSheet("color: #9ba3af; font-size: 12px;")
                row.addWidget(name)
                row.addWidget(desc)
                row.addStretch()
                wl.addLayout(row)
        else:
            no_apps = QLabel("No new applications to install (all selected apps are already installed).")
            no_apps.setStyleSheet("color: #10b981; font-style: italic;")
            wl.addWidget(no_apps)

        self.content_layout.addWidget(will_card)

        # 2. Section: Already Installed (Will Skip)
        if already_installed:
            inst_card = QFrame()
            inst_card.setStyleSheet("background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 8px; padding: 16px;")
            il = QVBoxLayout(inst_card)
            il.setSpacing(8)

            inst_title = QLabel(f"✓ Already Installed ({len(already_installed)} applications — will skip)")
            inst_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #10b981;")
            il.addWidget(inst_title)

            for app, detail in already_installed:
                row = QHBoxLayout()
                row.setSpacing(8)
                name = QLabel(f"✓ {app.name}")
                name.setStyleSheet("color: #f0f2f5; font-size: 12px;")
                det = QLabel(f"({detail})")
                det.setStyleSheet("color: #646d7d; font-size: 11px;")
                row.addWidget(name)
                row.addWidget(det)
                row.addStretch()
                il.addLayout(row)

            self.content_layout.addWidget(inst_card)

        self.content_layout.addStretch()

        # Update button state
        self.install_btn.setEnabled(len(will_install) > 0)
        if len(will_install) == 0:
            self.install_btn.setText("Everything Already Installed")
        else:
            self.install_btn.setText(f"Install {len(will_install)} Applications →")

    def _on_install_clicked(self):
        self.install_confirmed.emit(self.selected_app_ids, self.pin_taskbar_cb.isChecked())
