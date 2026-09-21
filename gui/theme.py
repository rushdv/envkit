"""
gui/theme.py — Styling, colors, and Qt stylesheet for envkit
"""

# Color Palette (Modern Slate / Charcoal Dark Theme)
BG_PRIMARY = "#12141a"       # Deep dark background
BG_SECONDARY = "#1a1d24"     # Card and sidebar background
BG_TERTIARY = "#232732"      # Hover / input background
BG_ACCENT = "#2e3444"        # Border / divider color

TEXT_PRIMARY = "#f0f2f5"     # Crisp white/light gray
TEXT_SECONDARY = "#9ba3af"   # Muted gray text
TEXT_MUTED = "#646d7d"       # Dim gray

ACCENT_BLUE = "#3b82f6"      # Primary action blue
ACCENT_BLUE_HOVER = "#2563eb"
ACCENT_GREEN = "#10b981"     # Installed / Success green
ACCENT_GREEN_BG = "#064e3b"
ACCENT_YELLOW = "#f59e0b"    # Warning / Pending amber
ACCENT_RED = "#ef4444"       # Error red
ACCENT_PURPLE = "#8b5cf6"    # Custom / Special

STYLESHEET = f"""
QMainWindow, QDialog {{
    background-color: {BG_PRIMARY};
    color: {TEXT_PRIMARY};
}}

QWidget {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "Ubuntu", sans-serif;
    font-size: 13px;
    color: {TEXT_PRIMARY};
}}

/* Scrollbar */
QScrollBar:vertical {{
    background: {BG_PRIMARY};
    width: 8px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: {BG_ACCENT};
    min-height: 20px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_MUTED};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* Sidebar */
#sidebar {{
    background-color: {BG_SECONDARY};
    border-right: 1px solid {BG_ACCENT};
    min-width: 210px;
    max-width: 210px;
}}

#sidebarTitle {{
    font-size: 18px;
    font-weight: bold;
    color: {TEXT_PRIMARY};
    padding: 16px 12px 4px 12px;
}}

#sidebarSubtitle {{
    font-size: 11px;
    color: {TEXT_MUTED};
    padding: 0px 12px 16px 12px;
}}

QListWidget#navList {{
    background-color: transparent;
    border: none;
    outline: none;
    padding: 8px;
}}

QListWidget#navList::item {{
    height: 38px;
    padding-left: 12px;
    border-radius: 6px;
    color: {TEXT_SECONDARY};
    font-weight: 500;
    margin-bottom: 2px;
}}

QListWidget#navList::item:hover {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
}}

QListWidget#navList::item:selected {{
    background-color: {ACCENT_BLUE};
    color: #ffffff;
    font-weight: bold;
}}

/* Primary Buttons */
QPushButton {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BG_ACCENT};
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {BG_ACCENT};
    border-color: {TEXT_MUTED};
}}

QPushButton:pressed {{
    background-color: {BG_PRIMARY};
}}

QPushButton:disabled {{
    background-color: {BG_SECONDARY};
    color: {TEXT_MUTED};
    border-color: {BG_TERTIARY};
}}

QPushButton.btnPrimary {{
    background-color: {ACCENT_BLUE};
    color: #ffffff;
    border: none;
    font-weight: bold;
}}

QPushButton.btnPrimary:hover {{
    background-color: {ACCENT_BLUE_HOVER};
}}

QPushButton.btnSuccess {{
    background-color: {ACCENT_GREEN};
    color: #ffffff;
    border: none;
}}

QPushButton.btnOutline {{
    background-color: transparent;
    border: 1px solid {BG_ACCENT};
    color: {TEXT_PRIMARY};
}}

QPushButton.btnOutline:hover {{
    background-color: {BG_TERTIARY};
}}

/* Line Edits & Search */
QLineEdit {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BG_ACCENT};
    border-radius: 6px;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT_BLUE};
}}

QLineEdit:focus {{
    border: 1px solid {ACCENT_BLUE};
    background-color: {BG_TERTIARY};
}}

/* Cards */
QFrame.card {{
    background-color: {BG_SECONDARY};
    border: 1px solid {BG_ACCENT};
    border-radius: 8px;
    padding: 12px;
}}

QFrame.card:hover {{
    border-color: {TEXT_MUTED};
}}

QFrame.cardSelected {{
    background-color: {BG_SECONDARY};
    border: 1.5px solid {ACCENT_BLUE};
    border-radius: 8px;
    padding: 12px;
}}

/* Badges */
QLabel.badge {{
    background-color: {BG_TERTIARY};
    color: {TEXT_SECONDARY};
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
}}

QLabel.badgeInstalled {{
    background-color: {ACCENT_GREEN_BG};
    color: {ACCENT_GREEN};
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: bold;
}}

/* Checkboxes */
QCheckBox {{
    color: {TEXT_PRIMARY};
    spacing: 6px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BG_ACCENT};
    border-radius: 4px;
    background: {BG_SECONDARY};
}}

QCheckBox::indicator:checked {{
    background-color: {ACCENT_BLUE};
    border-color: {ACCENT_BLUE};
}}

/* Progress Bar */
QProgressBar {{
    background-color: {BG_TERTIARY};
    border: 1px solid {BG_ACCENT};
    border-radius: 5px;
    text-align: center;
    color: {TEXT_PRIMARY};
    height: 16px;
}}

QProgressBar::chunk {{
    background-color: {ACCENT_GREEN};
    border-radius: 4px;
}}

/* Log Console */
QTextEdit.logConsole {{
    background-color: #0b0d11;
    color: #d1d5db;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 12px;
    border: 1px solid {BG_ACCENT};
    border-radius: 6px;
    padding: 8px;
}}
"""
