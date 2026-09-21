"""
gui/views/about_view.py — About dialog / view for envkit
"""

import platform
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from core.distro import DistroInfo


class AboutView(QWidget):
    def __init__(self, distro_info: DistroInfo, parent=None):
        super().__init__(parent)
        self.distro_info = distro_info
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 36, 40, 36)
        main_layout.setSpacing(20)

        card = QFrame()
        card.setStyleSheet("background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 12px; padding: 28px;")
        card_l = QVBoxLayout(card)
        card_l.setSpacing(16)

        # Header
        title = QLabel("envkit")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #3b82f6;")
        card_l.addWidget(title)

        tagline = QLabel("Modular Linux Software Installer & Workstation Setup Tool")
        tagline.setStyleSheet("font-size: 15px; font-weight: 500; color: #f0f2f5;")
        card_l.addWidget(tagline)

        desc = QLabel(
            "Install exactly what you need. envkit abstracts package management across "
            "Debian/Ubuntu, Arch, Fedora, and openSUSE, unifying native packages and Flatpak "
            "with a modern Qt6 interface and scriptable CLI."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #9ba3af; font-size: 13px; line-height: 1.5;")
        card_l.addWidget(desc)

        # System Info Box
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #232732; border-radius: 8px; padding: 14px;")
        info_l = QVBoxLayout(info_frame)
        info_l.setSpacing(6)

        try:
            import PySide6
            pyside_ver = PySide6.__version__
        except ImportError:
            pyside_ver = "Unknown"

        details = [
            ("Version:", "2.0.0"),
            ("Distribution:", self.distro_info.pretty_name),
            ("Package Manager:", self.distro_info.package_manager),
            ("Desktop Environment:", self.distro_info.desktop),
            ("Architecture:", self.distro_info.arch),
            ("Python Version:", platform.python_version()),
            ("Qt Framework:", f"PySide6 {pyside_ver}"),
            ("License:", "MIT License"),
            ("Repository:", "https://github.com/rushdv/envkit"),
        ]

        for k, v in details:
            row = QHBoxLayout()
            lbl_k = QLabel(k)
            lbl_k.setStyleSheet("color: #9ba3af; font-weight: bold; font-size: 12px; min-width: 140px;")
            lbl_v = QLabel(v)
            lbl_v.setStyleSheet("color: #f0f2f5; font-size: 12px;")
            row.addWidget(lbl_k)
            row.addWidget(lbl_v)
            row.addStretch()
            info_l.addLayout(row)

        card_l.addWidget(info_frame)
        card_l.addStretch()

        main_layout.addWidget(card)
        main_layout.addStretch()
