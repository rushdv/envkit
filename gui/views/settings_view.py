"""
gui/views/settings_view.py — Preferences and inline system diagnostic check
"""

import shutil
import socket
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from core.distro import DistroInfo
from core.logger import get_log_dir
from core.privilege import has_sudo, is_root


class SettingsView(QWidget):
    def __init__(self, distro_info: DistroInfo, parent=None):
        super().__init__(parent)
        self.distro_info = distro_info
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(20)

        # Title
        title_box = QVBoxLayout()
        title = QLabel("Settings & Diagnostics")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f0f2f5;")
        subtitle = QLabel("Configure installer preferences and run system diagnostic checks.")
        subtitle.setStyleSheet("font-size: 13px; color: #9ba3af;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        main_layout.addLayout(title_box)

        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        # 1. Package Source Preference Card
        source_card = QFrame()
        source_card.setStyleSheet("background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 8px; padding: 16px;")
        s_layout = QVBoxLayout(source_card)
        s_layout.setSpacing(10)

        s_title = QLabel("Package Source Priority")
        s_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #f0f2f5;")
        s_layout.addWidget(s_title)

        s_desc = QLabel("Select whether to prioritize native distribution packages or sandboxed Flatpaks:")
        s_desc.setStyleSheet("color: #9ba3af; font-size: 12px;")
        s_layout.addWidget(s_desc)

        self.native_first_rb = QRadioButton("Prioritize Native Distro Packages (apt / dnf / pacman / zypper)")
        self.native_first_rb.setChecked(True)
        self.flatpak_first_rb = QRadioButton("Prioritize Flatpak Sandboxed Applications (Flathub)")

        s_layout.addWidget(self.native_first_rb)
        s_layout.addWidget(self.flatpak_first_rb)
        layout.addWidget(source_card)

        # 2. Storage & Logs Card
        log_card = QFrame()
        log_card.setStyleSheet("background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 8px; padding: 16px;")
        l_layout = QVBoxLayout(log_card)
        l_layout.setSpacing(10)

        l_title = QLabel("Log Directory")
        l_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #f0f2f5;")
        l_layout.addWidget(l_title)

        log_path = str(get_log_dir())
        l_desc = QLabel(f"Installation and operation logs are stored at:\n<b>{log_path}</b>")
        l_desc.setStyleSheet("color: #9ba3af; font-size: 12px;")
        l_layout.addWidget(l_desc)

        btn_row = QHBoxLayout()
        copy_path_btn = QPushButton("Copy Log Path")
        copy_path_btn.setFixedHeight(30)
        copy_path_btn.clicked.connect(lambda: QApplication.clipboard().setText(log_path))
        btn_row.addWidget(copy_path_btn)
        btn_row.addStretch()
        l_layout.addLayout(btn_row)

        layout.addWidget(log_card)

        # 3. System Diagnostic (Doctor) Card
        doc_card = QFrame()
        doc_card.setStyleSheet("background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 8px; padding: 16px;")
        d_layout = QVBoxLayout(doc_card)
        d_layout.setSpacing(12)

        doc_header = QHBoxLayout()
        d_title = QLabel("System Environment Doctor")
        d_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #f0f2f5;")
        doc_header.addWidget(d_title)
        doc_header.addStretch()

        self.rerun_doc_btn = QPushButton("Re-run Checks")
        self.rerun_doc_btn.setFixedHeight(28)
        self.rerun_doc_btn.clicked.connect(self._run_diagnostics)
        doc_header.addWidget(self.rerun_doc_btn)
        d_layout.addLayout(doc_header)

        self.doc_results_layout = QVBoxLayout()
        self.doc_results_layout.setSpacing(6)
        d_layout.addLayout(self.doc_results_layout)

        layout.addWidget(doc_card)

        layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        self._run_diagnostics()

    def _run_diagnostics(self):
        # Clear previous
        for i in reversed(range(self.doc_results_layout.count())):
            item = self.doc_results_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        distro = self.distro_info

        # Checks:
        # 1. Distro
        self._add_doc_item(True, f"Distribution: {distro.pretty_name} ({distro.family})")
        # 2. Package manager
        pm_ok = distro.package_manager != "unknown" and bool(shutil.which(distro.package_manager))
        self._add_doc_item(pm_ok, f"Native package manager: {distro.package_manager}")
        # 3. Sudo
        self._add_doc_item(has_sudo(), "Sudo privilege escalation available")
        # 4. Internet
        net_ok = False
        try:
            socket.create_connection(("1.1.1.1", 53), timeout=2)
            net_ok = True
        except OSError:
            pass
        self._add_doc_item(net_ok, "Internet connectivity", is_warn=True)
        # 5. Flatpak
        fp_ok = bool(shutil.which("flatpak"))
        self._add_doc_item(fp_ok, "Flatpak application runtime available", is_warn=True)
        # 6. Desktop
        self._add_doc_item(True, f"Desktop environment: {distro.desktop}")
        # 7. Architecture
        self._add_doc_item(True, f"CPU architecture: {distro.arch}")

    def _add_doc_item(self, ok: bool, text: str, is_warn: bool = False):
        row = QHBoxLayout()
        row.setSpacing(8)

        if ok:
            icon = QLabel("✓")
            icon.setStyleSheet("color: #10b981; font-weight: bold; font-size: 13px;")
        elif is_warn:
            icon = QLabel("!")
            icon.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 13px;")
        else:
            icon = QLabel("✕")
            icon.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 13px;")

        lbl = QLabel(text)
        lbl.setStyleSheet("color: #f0f2f5; font-size: 12px;")

        row.addWidget(icon)
        row.addWidget(lbl)
        row.addStretch()

        w = QWidget()
        w.setLayout(row)
        self.doc_results_layout.addWidget(w)
