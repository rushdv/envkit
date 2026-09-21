"""
core/installer.py — Asynchronous installation runner, progress tracking, and error handling
"""

import os
import shutil
import subprocess
import tempfile
import threading
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
from core.catalog import AppEntry, Catalog, InstallAction
from core.detector import Detector
from core.distro import DistroInfo
from core.logger import get_logger
from core.package_manager import (
    AptManager,
    DnfManager,
    FlatpakManager,
    PacmanManager,
    PackageManager,
    YayManager,
    ZypperManager,
)
from core.privilege import wrap_sudo

logger = get_logger()


class AppStatus(Enum):
    QUEUED = "queued"
    ALREADY_INSTALLED = "already_installed"
    INSTALLING = "installing"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    UNAVAILABLE = "unavailable"


@dataclass
class InstallResult:
    app_id: str
    app_name: str
    status: AppStatus
    message: str = ""
    logs: List[str] = field(default_factory=list)
    exit_code: int = 0


class InstallRunner:
    def __init__(
        self,
        distro_info: DistroInfo,
        catalog: Catalog,
        detector: Optional[Detector] = None,
        dry_run: bool = False
    ):
        self.distro_info = distro_info
        self.catalog = catalog
        self.detector = detector or Detector(distro_info)
        self.dry_run = dry_run
        self.results: Dict[str, InstallResult] = {}
        self._cancel_requested = False

        # Callbacks
        self.on_app_start: Optional[Callable[[str, int, int], None]] = None  # (app_id, index, total)
        self.on_output_line: Optional[Callable[[str, str], None]] = None  # (app_id, line)
        self.on_app_status: Optional[Callable[[str, AppStatus, str], None]] = None  # (app_id, status, msg)
        self.on_progress: Optional[Callable[[int, int], None]] = None  # (completed, total)

    def cancel(self) -> None:
        self._cancel_requested = True

    def run_queue(
        self,
        app_ids: List[str],
        skip_installed: bool = True,
        prefer_source: Optional[str] = None
    ) -> Dict[str, InstallResult]:
        """Execute installation queue synchronously (suitable for running inside a thread or CLI)."""
        self._cancel_requested = False
        self.results.clear()
        total = len(app_ids)

        for idx, app_id in enumerate(app_ids, start=1):
            if self._cancel_requested:
                logger.info("Installation queue was cancelled by user.")
                self.results[app_id] = InstallResult(
                    app_id=app_id,
                    app_name=app_id,
                    status=AppStatus.SKIPPED,
                    message="Cancelled by user"
                )
                if self.on_app_status:
                    self.on_app_status(app_id, AppStatus.SKIPPED, "Cancelled")
                continue

            app = self.catalog.get(app_id)
            app_name = app.name if app else app_id

            if self.on_app_start:
                self.on_app_start(app_id, idx, total)

            # Check if already installed
            if skip_installed and app:
                inst_status, detail = self.detector.is_installed(app)
                if inst_status == "installed":
                    res = InstallResult(
                        app_id=app_id,
                        app_name=app_name,
                        status=AppStatus.ALREADY_INSTALLED,
                        message=f"Already installed ({detail})"
                    )
                    self.results[app_id] = res
                    if self.on_app_status:
                        self.on_app_status(app_id, AppStatus.ALREADY_INSTALLED, res.message)
                    if self.on_progress:
                        self.on_progress(idx, total)
                    continue

            # Resolve install action
            action = self.catalog.resolve_install_action(app_id, self.distro_info, prefer_source=prefer_source)
            if not action.available:
                res = InstallResult(
                    app_id=app_id,
                    app_name=app_name,
                    status=AppStatus.UNAVAILABLE,
                    message=action.reason or "Unavailable on this distribution"
                )
                self.results[app_id] = res
                if self.on_app_status:
                    self.on_app_status(app_id, AppStatus.UNAVAILABLE, res.message)
                if self.on_progress:
                    self.on_progress(idx, total)
                continue

            # Perform installation
            res = self._execute_action(action)
            self.results[app_id] = res

            if self.on_app_status:
                self.on_app_status(app_id, res.status, res.message)

            if self.on_progress:
                self.on_progress(idx, total)

        return self.results

    def _execute_action(self, action: InstallAction) -> InstallResult:
        app_id = action.app_id
        app_name = action.app_name

        if self.on_app_status:
            self.on_app_status(app_id, AppStatus.INSTALLING, "Installing...")

        if self.dry_run:
            msg = f"[Dry Run] Would install {action.packages or action.manager_name}"
            logger.info(f"DRY RUN: {msg}")
            if self.on_output_line:
                self.on_output_line(app_id, msg)
            return InstallResult(app_id=app_id, app_name=app_name, status=AppStatus.SUCCESS, message=msg)

        logs: List[str] = []

        # Determine command
        cmd: List[str] = []
        env = os.environ.copy()
        env.update(action.env)

        if action.manager_name == "flatpak":
            # Ensure flatpak is available
            if not shutil.which("flatpak"):
                return InstallResult(
                    app_id=app_id,
                    app_name=app_name,
                    status=AppStatus.FAILED,
                    message="Flatpak is not installed on this system. Install Flatpak first."
                )
            cmd = ["flatpak", "install", "-y", "flathub"] + action.packages

        elif action.manager_name in ("dnf", "dnf5"):
            manager_bin = "dnf5" if (action.manager_name == "dnf5" or shutil.which("dnf5")) else "dnf"
            raw_cmd = [manager_bin, "install", "-y"] + action.packages
            cmd = wrap_sudo(raw_cmd, requires_sudo=True)

        elif action.manager_name == "pacman":
            raw_cmd = ["pacman", "-S", "--noconfirm", "--needed"] + action.packages
            cmd = wrap_sudo(raw_cmd, requires_sudo=True)

        elif action.manager_name == "yay":
            aur_bin = "yay" if shutil.which("yay") else "paru"
            cmd = [aur_bin, "-S", "--noconfirm", "--needed"] + action.packages

        elif action.manager_name == "apt":
            env["DEBIAN_FRONTEND"] = "noninteractive"
            raw_cmd = ["apt-get", "install", "-y"] + action.packages
            cmd = wrap_sudo(raw_cmd, requires_sudo=True)

        elif action.manager_name == "zypper":
            raw_cmd = ["zypper", "--non-interactive", "install", "--no-recommends", "-y"] + action.packages
            cmd = wrap_sudo(raw_cmd, requires_sudo=True)

        elif action.manager_name == "script" and action.script_content:
            # Write script content to a safe temp script file and execute with bash
            with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as tf:
                tf.write(action.script_content)
                temp_script = tf.name
            os.chmod(temp_script, 0o700)
            raw_cmd = ["/bin/bash", temp_script]
            cmd = wrap_sudo(raw_cmd, requires_sudo=action.requires_sudo)

        else:
            return InstallResult(
                app_id=app_id,
                app_name=app_name,
                status=AppStatus.FAILED,
                message=f"Unsupported manager '{action.manager_name}'"
            )

        # Execute subprocess and stream output
        logger.info(f"Executing for {app_id}: {' '.join(cmd)}")
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                bufsize=1
            )

            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    clean_line = line.rstrip()
                    logs.append(clean_line)
                    logger.debug(f"[{app_id}] {clean_line}")
                    if self.on_output_line:
                        self.on_output_line(app_id, clean_line)
                process.stdout.close()

            returncode = process.wait()

            # Clean up temp script if used
            if action.manager_name == "script" and 'temp_script' in locals():
                try:
                    os.unlink(temp_script)
                except OSError:
                    pass

            if returncode == 0:
                # Handle post-install actions
                self._run_post_install(action)
                return InstallResult(
                    app_id=app_id,
                    app_name=app_name,
                    status=AppStatus.SUCCESS,
                    message="Installed successfully",
                    logs=logs,
                    exit_code=0
                )
            else:
                err_msg = self._diagnose_failure(action, returncode, logs)
                logger.error(f"Failed to install {app_id} (code {returncode}): {err_msg}")
                return InstallResult(
                    app_id=app_id,
                    app_name=app_name,
                    status=AppStatus.FAILED,
                    message=err_msg,
                    logs=logs,
                    exit_code=returncode
                )

        except Exception as e:
            logger.exception(f"Exception during installation of {app_id}")
            return InstallResult(
                app_id=app_id,
                app_name=app_name,
                status=AppStatus.FAILED,
                message=str(e),
                logs=logs,
                exit_code=1
            )

    def _run_post_install(self, action: InstallAction) -> None:
        """Run post-install tasks like adding user to groups or enabling systemd services."""
        user = os.environ.get("USER", "")
        for item in action.post_install_actions:
            if not isinstance(item, dict):
                continue

            # Group membership
            group = item.get("group")
            if group and user and shutil.which("usermod"):
                try:
                    subprocess.run(
                        wrap_sudo(["usermod", "-aG", group, user], requires_sudo=True),
                        check=False,
                        capture_output=True
                    )
                    logger.info(f"Added {user} to group {group}")
                except Exception as e:
                    logger.warning(f"Failed to add user to group {group}: {e}")

            # Systemd service
            service = item.get("service")
            if service and shutil.which("systemctl"):
                try:
                    subprocess.run(
                        wrap_sudo(["systemctl", "enable", "--now", service], requires_sudo=True),
                        check=False,
                        capture_output=True
                    )
                    logger.info(f"Enabled and started systemd service {service}")
                except Exception as e:
                    logger.warning(f"Failed to enable systemd service {service}: {e}")

    def _diagnose_failure(self, action: InstallAction, code: int, logs: List[str]) -> str:
        """Provide helpful error explanation rather than raw exit codes."""
        tail = "\n".join(logs[-6:]) if logs else "No output"
        if "Nothing to do" in tail or "already installed" in tail:
            return "Package is already present or nothing to do."
        if "Unable to locate package" in tail or "No match for argument" in tail or "target not found" in tail:
            return f"Package not found in active repositories for {self.distro_info.name}. Consider enabling extra repositories (e.g. RPM Fusion, EPEL, Flathub) or using Flatpak."
        if "Permission denied" in tail or "are you root" in tail or code in (126, 127):
            return "Privilege error: sudo authentication failed or required permissions were missing."
        if "Could not resolve host" in tail or "Network is unreachable" in tail:
            return "Network error: unable to reach package servers. Please verify your internet connection."
        return f"Installation exited with code {code}.\nTail logs:\n{tail}"
