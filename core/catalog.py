"""
core/catalog.py — Application catalog loader, schema definition, and search
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml
from core.distro import DistroInfo
from core.logger import get_logger

logger = get_logger()


@dataclass
class InstallAction:
    app_id: str
    app_name: str
    manager_name: str  # dnf | pacman | yay | apt | zypper | flatpak | script
    packages: List[str]
    requires_sudo: bool
    env: Dict[str, str] = field(default_factory=dict)
    script_content: Optional[str] = None
    script_path: Optional[str] = None
    post_install_actions: List[Dict[str, Any]] = field(default_factory=list)
    desktop_file: Optional[str] = None
    available: bool = True
    reason: Optional[str] = None


@dataclass
class AppEntry:
    id: str
    name: str
    description: str
    category: str
    tags: List[str] = field(default_factory=list)
    homepage: str = ""
    icon: str = ""
    source_preference: str = "native"  # native | flatpak | script
    packages: Dict[str, Any] = field(default_factory=dict)
    detection: Dict[str, Any] = field(default_factory=dict)
    requires_sudo: bool = True
    interactive: bool = False
    reboot_recommended: bool = False
    post_install: List[Dict[str, Any]] = field(default_factory=list)
    desktop_file: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppEntry":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category", "utilities"),
            tags=data.get("tags", []),
            homepage=data.get("homepage", ""),
            icon=data.get("icon", ""),
            source_preference=data.get("source_preference", "native"),
            packages=data.get("packages", {}),
            detection=data.get("detection", {}),
            requires_sudo=data.get("requires_sudo", True),
            interactive=data.get("interactive", False),
            reboot_recommended=data.get("reboot_recommended", False),
            post_install=data.get("post_install", []),
            desktop_file=data.get("desktop_file"),
        )


class Catalog:
    def __init__(self, catalog_dir: Optional[str] = None):
        if catalog_dir:
            self.catalog_dir = Path(catalog_dir)
        else:
            # Default to root/catalog
            self.catalog_dir = Path(__file__).resolve().parent.parent / "catalog"
        self.apps: Dict[str, AppEntry] = {}
        self.categories: Set[str] = set()
        self.load()

    def load(self) -> None:
        """Scan catalog directory and load all YAML app files."""
        self.apps.clear()
        self.categories.clear()

        if not self.catalog_dir.exists():
            logger.warning(f"Catalog directory not found at {self.catalog_dir}")
            return

        for yaml_file in sorted(self.catalog_dir.glob("**/*.yaml")):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    continue
                app_id = data.get("id")
                if not app_id:
                    continue
                entry = AppEntry.from_dict(data)
                self.apps[app_id] = entry
                self.categories.add(entry.category)
            except Exception as e:
                logger.error(f"Error parsing catalog file {yaml_file}: {e}")

    def get(self, app_id: str) -> Optional[AppEntry]:
        return self.apps.get(app_id)

    def list_all(self) -> List[AppEntry]:
        return sorted(self.apps.values(), key=lambda a: a.name.lower())

    def get_by_category(self, category: str) -> List[AppEntry]:
        category_lower = category.lower()
        return [
            app for app in self.list_all()
            if app.category.lower() == category_lower
        ]

    def get_categories(self) -> List[str]:
        return sorted(list(self.categories))

    def search(self, query: str) -> List[AppEntry]:
        """Case-insensitive fuzzy match across id, name, description, category, and tags."""
        q = query.strip().lower()
        if not q:
            return self.list_all()

        results = []
        for app in self.list_all():
            score = 0
            if q == app.id.lower():
                score += 100
            elif q in app.id.lower():
                score += 40

            if q == app.name.lower():
                score += 80
            elif q in app.name.lower():
                score += 30

            if any(q == t.lower() for t in app.tags):
                score += 50
            elif any(q in t.lower() for t in app.tags):
                score += 20

            if q in app.category.lower():
                score += 15

            if q in app.description.lower():
                score += 10

            if score > 0:
                results.append((score, app))

        results.sort(key=lambda x: x[0], reverse=True)
        return [app for _, app in results]

    def resolve_install_action(
        self,
        app_id: str,
        distro_info: DistroInfo,
        prefer_source: Optional[str] = None
    ) -> InstallAction:
        """
        Resolve the concrete installation command and strategy for the current distro.
        Respects:
          1. Explicit preference (e.g. 'flatpak' or 'native')
          2. App catalog source_preference
          3. Native distro availability
          4. Fallback to Flatpak
          5. Custom official script (e.g. rustup, starship, nvm)
        """
        app = self.get(app_id)
        if not app:
            return InstallAction(
                app_id=app_id,
                app_name=app_id,
                manager_name="unknown",
                packages=[],
                requires_sudo=False,
                available=False,
                reason=f"Application '{app_id}' not found in catalog."
            )

        family = distro_info.family
        pkg_defs = app.packages
        pref = prefer_source or app.source_preference

        # Flatpak preference if explicitly requested or preferred
        flatpak_info = pkg_defs.get("flatpak")
        if pref == "flatpak" and flatpak_info:
            fp_id = flatpak_info.get("id") if isinstance(flatpak_info, dict) else flatpak_info
            if fp_id:
                return InstallAction(
                    app_id=app.id,
                    app_name=app.name,
                    manager_name="flatpak",
                    packages=[fp_id],
                    requires_sudo=False,
                    desktop_file=app.desktop_file or f"{fp_id}.desktop",
                    post_install_actions=app.post_install,
                    available=True
                )

        # Check native distro packages
        distro_pkg = pkg_defs.get(family)
        if distro_pkg:
            manager_name = distro_info.package_manager
            pkg_name = None
            req_sudo = app.requires_sudo

            if isinstance(distro_pkg, dict):
                manager_name = distro_pkg.get("manager", manager_name)
                pkg_name = distro_pkg.get("package")
                if "requires_sudo" in distro_pkg:
                    req_sudo = distro_pkg["requires_sudo"]
            elif isinstance(distro_pkg, str):
                pkg_name = distro_pkg

            if pkg_name and pkg_name != "-":
                pkgs = pkg_name.split() if " " in pkg_name else [pkg_name]
                # If manager is yay on Arch, sudo is not required
                if manager_name == "yay":
                    req_sudo = False
                return InstallAction(
                    app_id=app.id,
                    app_name=app.name,
                    manager_name=manager_name,
                    packages=pkgs,
                    requires_sudo=req_sudo,
                    desktop_file=app.desktop_file,
                    post_install_actions=app.post_install,
                    available=True
                )

        # Fallback to Flatpak if native package is missing or "-"
        if flatpak_info:
            fp_id = flatpak_info.get("id") if isinstance(flatpak_info, dict) else flatpak_info
            if fp_id:
                return InstallAction(
                    app_id=app.id,
                    app_name=app.name,
                    manager_name="flatpak",
                    packages=[fp_id],
                    requires_sudo=False,
                    desktop_file=app.desktop_file or f"{fp_id}.desktop",
                    post_install_actions=app.post_install,
                    available=True
                )

        # Check official script installer if provided
        script_info = pkg_defs.get("script")
        if script_info:
            content = script_info.get("command") or script_info.get("sh")
            return InstallAction(
                app_id=app.id,
                app_name=app.name,
                manager_name="script",
                packages=[],
                script_content=content,
                requires_sudo=script_info.get("requires_sudo", False),
                desktop_file=app.desktop_file,
                post_install_actions=app.post_install,
                available=True
            )

        return InstallAction(
            app_id=app.id,
            app_name=app.name,
            manager_name="unavailable",
            packages=[],
            requires_sudo=False,
            available=False,
            reason=f"Application '{app.name}' is not packaged for {distro_info.name} and has no Flatpak equivalent."
        )
