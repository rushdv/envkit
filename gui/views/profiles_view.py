"""
gui/views/profiles_view.py — Workstation profiles manager view
"""

from typing import List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from core.profiles import Profile, ProfileManager


class ProfilesView(QWidget):
    profile_selected = Signal(list)  # list of app_ids

    def __init__(self, parent=None):
        super().__init__(parent)
        self.profile_mgr = ProfileManager()
        self._setup_ui()
        self.reload_profiles()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(20)

        # Title & Toolbar
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Workstation Profiles")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #f0f2f5;")
        subtitle = QLabel("Choose a curated environment setup, or create, import, and export custom profiles.")
        subtitle.setStyleSheet("font-size: 13px; color: #9ba3af;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)

        header.addStretch()

        self.import_btn = QPushButton("Import Profile (YAML)")
        self.import_btn.setFixedHeight(34)
        self.import_btn.clicked.connect(self._on_import_clicked)
        header.addWidget(self.import_btn)

        main_layout.addLayout(header)

        # Scroll Area for Profiles
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(24)

        # Predefined Profiles Section
        pre_title = QLabel("Built-in Profiles")
        pre_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #3b82f6;")
        self.content_layout.addWidget(pre_title)

        self.predefined_grid = QGridLayout()
        self.predefined_grid.setSpacing(14)
        self.content_layout.addLayout(self.predefined_grid)

        # Custom Profiles Section
        custom_title = QLabel("Custom Profiles")
        custom_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #10b981; margin-top: 10px;")
        self.content_layout.addWidget(custom_title)

        self.custom_grid = QGridLayout()
        self.custom_grid.setSpacing(14)
        self.content_layout.addLayout(self.custom_grid)

        self.content_layout.addStretch()

        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll, stretch=1)

    def reload_profiles(self):
        # Clear existing
        for grid in (self.predefined_grid, self.custom_grid):
            for i in reversed(range(grid.count())):
                item = grid.itemAt(i)
                if item.widget():
                    item.widget().setParent(None)

        profiles = self.profile_mgr.list_all()

        p_row, p_col = 0, 0
        c_row, c_col = 0, 0

        for p in profiles:
            card = self._create_profile_card(p)
            if p.is_custom:
                self.custom_grid.addWidget(card, c_row, c_col)
                c_col += 1
                if c_col > 1:
                    c_col = 0
                    c_row += 1
            else:
                self.predefined_grid.addWidget(card, p_row, p_col)
                p_col += 1
                if p_col > 1:
                    p_col = 0
                    p_row += 1

        if c_row == 0 and c_col == 0:
            no_custom = QLabel("No custom profiles created yet. Save your current selection as a custom profile!")
            no_custom.setStyleSheet("color: #646d7d; font-style: italic; padding: 8px 0;")
            self.custom_grid.addWidget(no_custom, 0, 0)

    def _create_profile_card(self, profile: Profile) -> QWidget:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: #1a1d24; border: 1px solid #2e3444; border-radius: 8px; padding: 14px; }"
            "QFrame:hover { border-color: #3b82f6; }"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header
        header = QHBoxLayout()
        t = QLabel(profile.name)
        t.setStyleSheet("font-size: 15px; font-weight: bold; color: #f0f2f5;")
        header.addWidget(t)
        header.addStretch()

        badge = QLabel(f"{len(profile.apps)} apps")
        badge.setStyleSheet("background-color: #232732; color: #9ba3af; border-radius: 4px; padding: 2px 6px; font-size: 11px;")
        header.addWidget(badge)
        layout.addLayout(header)

        # Description
        desc = QLabel(profile.description)
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #9ba3af; font-size: 12px;")
        layout.addWidget(desc)

        # Apps preview pills
        preview_text = ", ".join(profile.apps[:6])
        if len(profile.apps) > 6:
            preview_text += f", +{len(profile.apps) - 6} more"
        apps_lbl = QLabel(f"Includes: {preview_text}")
        apps_lbl.setWordWrap(True)
        apps_lbl.setStyleSheet("color: #646d7d; font-size: 11px;")
        layout.addWidget(apps_lbl)

        layout.addStretch()

        # Action buttons
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(8)

        sel_btn = QPushButton("Select Profile")
        sel_btn.setFixedHeight(30)
        sel_btn.setStyleSheet("background-color: #3b82f6; color: #ffffff; font-weight: bold; border-radius: 5px; padding: 4px 12px;")
        sel_btn.clicked.connect(lambda _, p=profile: self.profile_selected.emit(p.apps))
        btn_bar.addWidget(sel_btn)

        exp_btn = QPushButton("Export")
        exp_btn.setFixedHeight(30)
        exp_btn.setStyleSheet("background-color: #232732; color: #f0f2f5; border: 1px solid #2e3444; border-radius: 5px; padding: 4px 8px;")
        exp_btn.clicked.connect(lambda _, p=profile: self._on_export_clicked(p))
        btn_bar.addWidget(exp_btn)

        if profile.is_custom:
            del_btn = QPushButton("Delete")
            del_btn.setFixedHeight(30)
            del_btn.setStyleSheet("background-color: #232732; color: #ef4444; border: 1px solid #2e3444; border-radius: 5px; padding: 4px 8px;")
            del_btn.clicked.connect(lambda _, p=profile: self._on_delete_clicked(p))
            btn_bar.addWidget(del_btn)

        layout.addLayout(btn_bar)
        return card

    def _on_export_clicked(self, profile: Profile):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Profile", f"{profile.id}.yaml", "YAML files (*.yaml *.yml)"
        )
        if path:
            try:
                self.profile_mgr.export_profile(profile, path)
                QMessageBox.information(self, "Export Successful", f"Profile exported to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Could not export profile: {e}")

    def _on_import_clicked(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Profile", "", "YAML files (*.yaml *.yml)"
        )
        if path:
            try:
                prof = self.profile_mgr.import_profile(path)
                QMessageBox.information(self, "Import Successful", f"Profile '{prof.name}' imported successfully!")
                self.reload_profiles()
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", f"Could not import profile: {e}")

    def _on_delete_clicked(self, profile: Profile):
        reply = QMessageBox.question(
            self, "Delete Profile", f"Are you sure you want to delete custom profile '{profile.name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.profile_mgr.delete_custom_profile(profile.id)
            self.reload_profiles()

    def create_custom_profile_from_selection(self, app_ids: List[str]):
        """Create a new custom profile from currently selected app IDs."""
        name, ok1 = QInputDialog.getText(self, "Save Custom Profile", "Profile Name:")
        if not ok1 or not name.strip():
            return

        desc, ok2 = QInputDialog.getText(self, "Save Custom Profile", "Profile Description:")
        if not ok2:
            desc = ""

        profile_id = name.strip().lower().replace(" ", "-")
        new_prof = Profile(
            id=profile_id,
            name=name.strip(),
            description=desc.strip(),
            apps=app_ids,
            is_custom=True
        )
        self.profile_mgr.save_custom_profile(new_prof)
        QMessageBox.information(self, "Profile Saved", f"Custom profile '{new_prof.name}' saved successfully!")
        self.reload_profiles()
