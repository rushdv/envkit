"""
gui/views/home_view.py — Dashboard / Home view for envkit
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
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


class HomeView(QWidget):
    navigate_requested = Signal(str, str)  # (view_name, param)

    def __init__(self, distro_info: DistroInfo, catalog: Catalog, detector: Detector, parent=None):
        super().__init__(parent)
        self.distro_info = distro_info
        self.catalog = catalog
        self.detector = detector

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Welcome Header
        header = QVBoxLayout()
        title = QLabel("Welcome to envkit")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #f0f2f5;")
        subtitle = QLabel("A modular Linux software installer and workstation builder. Install exactly what you need.")
        subtitle.setStyleSheet("font-size: 14px; color: #9ba3af;")
        header.addWidget(title)
        header.addWidget(subtitle)
        layout.addLayout(header)

        # System Banner Card
        banner_card = QFrame()
        banner_card.setStyleSheet(
            "background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 10px; padding: 18px;"
        )
        banner_layout = QHBoxLayout(banner_card)
        banner_layout.setSpacing(20)

        distro_details = QVBoxLayout()
        distro_name = QLabel(f"🐧 {self.distro_info.pretty_name}")
        distro_name.setStyleSheet("font-size: 16px; font-weight: bold; color: #f0f2f5;")
        pkg_desc = QLabel(f"Package Manager: <b>{self.distro_info.package_manager}</b>  •  Desktop: <b>{self.distro_info.desktop}</b>")
        pkg_desc.setStyleSheet("color: #9ba3af; font-size: 13px;")
        distro_details.addWidget(distro_name)
        distro_details.addWidget(pkg_desc)
        banner_layout.addLayout(distro_details)

        banner_layout.addStretch()

        # Stats counters
        total_apps = len(self.catalog.apps)
        installed_count = sum(1 for a in self.catalog.list_all() if self.detector.is_installed(a)[0] == "installed")

        stats_box = QHBoxLayout()
        stats_box.setSpacing(16)

        c1 = self._create_stat_badge(str(total_apps), "Catalog Apps")
        c2 = self._create_stat_badge(str(installed_count), "Installed")

        stats_box.addWidget(c1)
        stats_box.addWidget(c2)
        banner_layout.addLayout(stats_box)

        layout.addWidget(banner_card)

        # Category Browser Section
        cat_section = QVBoxLayout()
        cat_title = QLabel("Browse by Category")
        cat_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f0f2f5;")
        cat_section.addWidget(cat_title)

        cat_grid = QGridLayout()
        cat_grid.setSpacing(12)

        categories = [
            ("development", "💻 Development", "Compilers, runtimes, containers, IDEs, databases"),
            ("terminal", "⚡ Terminal Powerhouse", "Shells, prompts, modern CLI tools, multiplexers"),
            ("browsers", "🌐 Web Browsers", "Firefox, Brave, Chromium, Zen, Tor"),
            ("security", "🛡️ Security & Pentesting", "Nmap, Wireshark, Burp, ZAP, Ghidra, RE tools"),
            ("student", "📚 Student & Academic", "Obsidian, Zotero, LibreOffice, Xournal++, Draw.io"),
            ("media", "🎬 Media & Creative", "OBS Studio, VLC, GIMP, Shotcut, Spotify"),
            ("utilities", "🔧 Utilities & Everyday", "Bitwarden, AnyDesk, Flatseal, qBittorrent"),
            ("communication", "💬 Communication", "Telegram Desktop, Discord"),
        ]

        row = 0
        col = 0
        for cat_id, name, desc in categories:
            card = self._create_category_card(cat_id, name, desc)
            cat_grid.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        cat_section.addLayout(cat_grid)
        layout.addLayout(cat_section)

        # Quick Action Buttons
        actions_title = QLabel("Quick Actions")
        actions_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f0f2f5; margin-top: 8px;")
        layout.addWidget(actions_title)

        actions_bar = QHBoxLayout()
        actions_bar.setSpacing(12)

        btn_all = QPushButton("Browse Full Catalog")
        btn_all.setFixedHeight(40)
        btn_all.setStyleSheet("background-color: #3b82f6; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 8px 18px;")
        btn_all.clicked.connect(lambda: self.navigate_requested.emit("catalog", "all"))
        actions_bar.addWidget(btn_all)

        btn_profiles = QPushButton("Choose Workstation Profile")
        btn_profiles.setFixedHeight(40)
        btn_profiles.setStyleSheet("background-color: #232732; color: #f0f2f5; border: 1px solid #2e3444; border-radius: 6px; padding: 8px 18px;")
        btn_profiles.clicked.connect(lambda: self.navigate_requested.emit("profiles", ""))
        actions_bar.addWidget(btn_profiles)

        btn_installed = QPushButton("View Installed Software")
        btn_installed.setFixedHeight(40)
        btn_installed.setStyleSheet("background-color: #232732; color: #f0f2f5; border: 1px solid #2e3444; border-radius: 6px; padding: 8px 18px;")
        btn_installed.clicked.connect(lambda: self.navigate_requested.emit("installed", ""))
        actions_bar.addWidget(btn_installed)

        actions_bar.addStretch()
        layout.addLayout(actions_bar)

        layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _create_stat_badge(self, number: str, label: str) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(4, 4, 4, 4)
        l.setSpacing(2)
        n = QLabel(number)
        n.setAlignment(Qt.AlignCenter)
        n.setStyleSheet("font-size: 22px; font-weight: bold; color: #3b82f6;")
        txt = QLabel(label)
        txt.setAlignment(Qt.AlignCenter)
        txt.setStyleSheet("font-size: 11px; color: #9ba3af;")
        l.addWidget(n)
        l.addWidget(txt)
        return w

    def _create_category_card(self, cat_id: str, name: str, desc: str) -> QWidget:
        card = QFrame()
        card.setCursor(Qt.PointingHandCursor)
        card.setStyleSheet(
            "QFrame { background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 8px; padding: 12px; }"
            "QFrame:hover { background-color: #232732; border-color: #3b82f6; }"
        )
        l = QVBoxLayout(card)
        l.setContentsMargins(12, 10, 12, 10)
        l.setSpacing(4)

        t = QLabel(name)
        t.setStyleSheet("font-weight: bold; font-size: 14px; color: #f0f2f5;")
        d = QLabel(desc)
        d.setWordWrap(True)
        d.setStyleSheet("color: #9ba3af; font-size: 12px;")

        l.addWidget(t)
        l.addWidget(d)

        card.mousePressEvent = lambda e: self.navigate_requested.emit("catalog", cat_id)
        return card
