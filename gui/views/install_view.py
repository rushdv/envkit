"""
gui/views/install_view.py — Real-time asynchronous installation progress view
"""

from typing import Dict, List, Optional
from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from core.catalog import Catalog
from core.config import pin_to_desktop_taskbar
from core.detector import Detector
from core.distro import DistroInfo
from core.installer import AppStatus, InstallResult, InstallRunner
from gui.widgets.log_console import LogConsole


class InstallWorker(QObject):
    app_started = Signal(str, int, int)  # (app_id, index, total)
    output_line = Signal(str, str)       # (app_id, line)
    app_status = Signal(str, str, str)   # (app_id, status_str, message)
    progress = Signal(int, int)          # (completed, total)
    finished = Signal(dict)              # (results_dict)

    def __init__(self, distro_info: DistroInfo, catalog: Catalog, detector: Detector, app_ids: List[str]):
        super().__init__()
        self.distro_info = distro_info
        self.catalog = catalog
        self.detector = detector
        self.app_ids = app_ids
        self.runner = InstallRunner(distro_info, catalog, detector)

    def run(self):
        # Wire runner callbacks to Qt Signals
        self.runner.on_app_start = lambda aid, idx, tot: self.app_started.emit(aid, idx, tot)
        self.runner.on_output_line = lambda aid, line: self.output_line.emit(aid, line)
        self.runner.on_app_status = lambda aid, st, msg: self.app_status.emit(aid, st.value, msg)
        self.runner.on_progress = lambda comp, tot: self.progress.emit(comp, tot)

        results = self.runner.run_queue(self.app_ids, skip_installed=True)
        self.finished.emit(results)

    def cancel(self):
        self.runner.cancel()


class InstallView(QWidget):
    done_requested = Signal()

    def __init__(self, distro_info: DistroInfo, catalog: Catalog, detector: Detector, parent=None):
        super().__init__(parent)
        self.distro_info = distro_info
        self.catalog = catalog
        self.detector = detector

        self.app_ids: List[str] = []
        self.pin_taskbar = False
        self.status_rows: Dict[str, Dict[str, QLabel]] = {}
        self.failed_app_ids: List[str] = []

        self.thread: Optional[QThread] = None
        self.worker: Optional[InstallWorker] = None

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(16)

        # Header Title
        self.title_label = QLabel("Installing Applications...")
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #f0f2f5;")
        main_layout.addWidget(self.title_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        self.progress_text = QLabel("Preparing queue...")
        self.progress_text.setStyleSheet("color: #9ba3af; font-size: 12px;")
        main_layout.addWidget(self.progress_text)

        # App rows container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(220)
        scroll.setStyleSheet("QScrollArea { border: 1px solid #2e3444; border-radius: 6px; background-color: #1a1d24; }")

        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(12, 10, 12, 10)
        self.rows_layout.setSpacing(6)

        scroll.setWidget(self.rows_container)
        main_layout.addWidget(scroll)

        # Live Console
        self.console = LogConsole()
        main_layout.addWidget(self.console, stretch=1)

        # Bottom Button Bar
        self.bottom_bar = QHBoxLayout()

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        self.bottom_bar.addWidget(self.summary_label)

        self.bottom_bar.addStretch()

        self.retry_btn = QPushButton("Retry Failed")
        self.retry_btn.setFixedHeight(36)
        self.retry_btn.setVisible(False)
        self.retry_btn.setStyleSheet("background-color: #f59e0b; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 6px 16px;")
        self.retry_btn.clicked.connect(self._on_retry_clicked)
        self.bottom_bar.addWidget(self.retry_btn)

        self.done_btn = QPushButton("Done")
        self.done_btn.setFixedHeight(36)
        self.done_btn.setEnabled(False)
        self.done_btn.setStyleSheet(
            "QPushButton { background-color: #10b981; color: #ffffff; font-weight: bold; border-radius: 6px; padding: 6px 20px; }"
            "QPushButton:disabled { background-color: #232732; color: #646d7d; }"
        )
        self.done_btn.clicked.connect(self.done_requested.emit)
        self.bottom_bar.addWidget(self.done_btn)

        main_layout.addLayout(self.bottom_bar)

    def start_installation(self, app_ids: List[str], pin_taskbar: bool = False):
        self.app_ids = app_ids
        self.pin_taskbar = pin_taskbar
        self.failed_app_ids.clear()
        self.console.clear()
        self.retry_btn.setVisible(False)
        self.done_btn.setEnabled(False)
        self.title_label.setText("Installing Applications...")
        self.summary_label.setText("")

        # Clear and build status rows
        for i in reversed(range(self.rows_layout.count())):
            item = self.rows_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        self.status_rows.clear()
        for aid in self.app_ids:
            app = self.catalog.get(aid)
            name = app.name if app else aid

            row = QFrame()
            row.setStyleSheet("background-color: #232732; border-radius: 4px; padding: 4px 8px;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(6, 4, 6, 4)

            icon_lbl = QLabel("○")
            icon_lbl.setStyleSheet("color: #9ba3af; font-weight: bold; width: 20px;")

            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("font-weight: bold; font-size: 12px; color: #f0f2f5;")

            msg_lbl = QLabel("Waiting")
            msg_lbl.setStyleSheet("color: #646d7d; font-size: 11px;")

            rl.addWidget(icon_lbl)
            rl.addWidget(name_lbl)
            rl.addStretch()
            rl.addWidget(msg_lbl)

            self.rows_layout.addWidget(row)
            self.status_rows[aid] = {
                "icon": icon_lbl,
                "msg": msg_lbl,
                "row": row
            }

        self.rows_layout.addStretch()

        # Launch QThread worker
        self.thread = QThread()
        self.worker = InstallWorker(self.distro_info, self.catalog, self.detector, self.app_ids)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.app_started.connect(self._on_app_started)
        self.worker.output_line.connect(self._on_output_line)
        self.worker.app_status.connect(self._on_app_status)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def _on_app_started(self, app_id: str, index: int, total: int):
        self.progress_text.setText(f"Processing {index} of {total}...")

    def _on_output_line(self, app_id: str, line: str):
        self.console.append_line(f"[{app_id}] {line}")

    def _on_app_status(self, app_id: str, status_str: str, message: str):
        row_data = self.status_rows.get(app_id)
        if not row_data:
            return

        icon_lbl = row_data["icon"]
        msg_lbl = row_data["msg"]

        if status_str == AppStatus.INSTALLING.value:
            icon_lbl.setText("⟳")
            icon_lbl.setStyleSheet("color: #3b82f6; font-weight: bold;")
            msg_lbl.setText("Installing...")
            msg_lbl.setStyleSheet("color: #3b82f6;")
        elif status_str == AppStatus.SUCCESS.value:
            icon_lbl.setText("✓")
            icon_lbl.setStyleSheet("color: #10b981; font-weight: bold;")
            msg_lbl.setText("Installed")
            msg_lbl.setStyleSheet("color: #10b981;")
        elif status_str == AppStatus.ALREADY_INSTALLED.value:
            icon_lbl.setText("✓")
            icon_lbl.setStyleSheet("color: #10b981; font-weight: bold;")
            msg_lbl.setText("Already Installed")
            msg_lbl.setStyleSheet("color: #10b981;")
        elif status_str == AppStatus.FAILED.value:
            icon_lbl.setText("✕")
            icon_lbl.setStyleSheet("color: #ef4444; font-weight: bold;")
            msg_lbl.setText(f"Failed: {message}")
            msg_lbl.setStyleSheet("color: #ef4444;")
            self.failed_app_ids.append(app_id)
        elif status_str == AppStatus.UNAVAILABLE.value:
            icon_lbl.setText("!")
            icon_lbl.setStyleSheet("color: #f59e0b; font-weight: bold;")
            msg_lbl.setText("Unavailable on this distro")
            msg_lbl.setStyleSheet("color: #f59e0b;")

    def _on_progress(self, completed: int, total: int):
        percent = int((completed / total) * 100) if total > 0 else 100
        self.progress_bar.setValue(percent)
        self.progress_text.setText(f"Completed {completed} of {total} applications")

    def _on_finished(self, results: Dict[str, InstallResult]):
        self.title_label.setText("Installation Finished")
        successes = sum(1 for r in results.values() if r.status in (AppStatus.SUCCESS, AppStatus.ALREADY_INSTALLED))
        failures = sum(1 for r in results.values() if r.status == AppStatus.FAILED)

        if failures == 0:
            self.summary_label.setText(f"✓ All {successes} applications completed successfully!")
            self.summary_label.setStyleSheet("color: #10b981; font-weight: bold; font-size: 13px;")
        else:
            self.summary_label.setText(f"Completed with issues: {successes} succeeded, {failures} failed.")
            self.summary_label.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 13px;")
            self.retry_btn.setVisible(True)

        self.done_btn.setEnabled(True)

        # Pin to taskbar if user explicitly opted in
        if self.pin_taskbar:
            for aid, res in results.items():
                if res.status == AppStatus.SUCCESS:
                    app = self.catalog.get(aid)
                    if app and app.desktop_file:
                        pin_to_desktop_taskbar(app.desktop_file)

    def _on_retry_clicked(self):
        if self.failed_app_ids:
            to_retry = list(self.failed_app_ids)
            self.start_installation(to_retry, self.pin_taskbar)
