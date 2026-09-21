"""
core/detector.py — Detection engine for already-installed applications
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from core.catalog import AppEntry
from core.distro import DistroInfo


class Detector:
    def __init__(self, distro_info: DistroInfo):
        self.distro_info = distro_info
        self._cache: Dict[str, Tuple[str, str]] = {}
        self._flatpak_installed_apps: Optional[set] = None

    def clear_cache(self) -> None:
        self._cache.clear()
        self._flatpak_installed_apps = None

    def _get_installed_flatpaks(self) -> set:
        """Cache list of installed flatpaks by scanning standard flatpak directories."""
        if self._flatpak_installed_apps is not None:
            return self._flatpak_installed_apps

        apps = set()
        system_flatpak = Path("/var/lib/flatpak/app")
        if system_flatpak.exists():
            try:
                for p in system_flatpak.iterdir():
                    if p.is_dir():
                        apps.add(p.name)
            except OSError:
                pass

        user_flatpak = Path.home() / ".local" / "share" / "flatpak" / "app"
        if user_flatpak.exists():
            try:
                for p in user_flatpak.iterdir():
                    if p.is_dir():
                        apps.add(p.name)
            except OSError:
                pass

        self._flatpak_installed_apps = apps
        return apps

    def is_installed(self, app: AppEntry) -> Tuple[str, str]:
        """
        Check if application is already installed.
        Returns (status, detail) where status is 'installed', 'not_installed', or 'unknown'.
        """
        if app.id in self._cache:
            return self._cache[app.id]

        detection = app.detection or {}

        # 1. Path detection (e.g. nvm, fonts, etc.)
        paths = detection.get("paths", [])
        if isinstance(paths, str):
            paths = [paths]
        for p_str in paths:
            expanded = Path(os.path.expanduser(p_str))
            if expanded.exists():
                res = ("installed", f"path: {expanded}")
                self._cache[app.id] = res
                return res

        # 2. Binary command detection
        commands = detection.get("commands", [])
        if isinstance(commands, str):
            commands = [commands]
        if not commands and detection.get("command"):
            commands = [detection["command"]]

        for cmd in commands:
            # First check PATH
            if shutil.which(cmd):
                res = ("installed", f"command: {cmd}")
                self._cache[app.id] = res
                return res
            # Also check ~/.local/bin, ~/.cargo/bin, ~/go/bin
            for extra in [
                Path.home() / ".local" / "bin" / cmd,
                Path.home() / ".cargo" / "bin" / cmd,
                Path.home() / "go" / "bin" / cmd,
            ]:
                if extra.exists() and os.access(extra, os.X_OK):
                    res = ("installed", f"command: {extra}")
                    self._cache[app.id] = res
                    return res

        # 3. Flatpak detection
        fp_id = detection.get("flatpak")
        if not fp_id and "flatpak" in app.packages:
            fp_raw = app.packages["flatpak"]
            fp_id = fp_raw.get("id") if isinstance(fp_raw, dict) else fp_raw

        if fp_id:
            if fp_id in self._get_installed_flatpaks():
                res = ("installed", f"flatpak: {fp_id}")
                self._cache[app.id] = res
                return res

        # 4. Native package query (if command detection wasn't decisive)
        packages_dict = detection.get("packages", {})
        if isinstance(packages_dict, dict) and self.distro_info.family in packages_dict:
            pkg_name = packages_dict[self.distro_info.family]
            if pkg_name and self._check_native_pkg(pkg_name):
                res = ("installed", f"package: {pkg_name}")
                self._cache[app.id] = res
                return res

        res = ("not_installed", "Not found")
        self._cache[app.id] = res
        return res

    def _check_native_pkg(self, pkg_name: str) -> bool:
        family = self.distro_info.family
        try:
            if family in ("fedora", "opensuse"):
                res = subprocess.run(
                    ["rpm", "-q", pkg_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=2
                )
                return res.returncode == 0
            elif family == "arch":
                res = subprocess.run(
                    ["pacman", "-Q", pkg_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=2
                )
                return res.returncode == 0
            elif family == "debian":
                res = subprocess.run(
                    ["dpkg-query", "-W", "-f=${Status}", pkg_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    timeout=2,
                    text=True
                )
                return "install ok installed" in res.stdout
        except (subprocess.SubprocessError, OSError):
            pass
        return False
