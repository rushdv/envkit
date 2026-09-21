"""
core/distro.py — Distribution & Desktop Environment detection
"""

import os
import platform
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DistroInfo:
    id: str
    name: str
    pretty_name: str
    version_id: str
    family: str  # fedora | arch | debian | opensuse | unknown
    package_manager: str  # dnf | pacman | apt | zypper | unknown
    aur_helper: Optional[str] = None  # yay | paru
    dnf_version: Optional[str] = None  # dnf | dnf5
    desktop: str = "Unknown"  # GNOME, KDE Plasma, XFCE, etc.
    arch: str = "x86_64"
    shell: str = "/bin/bash"


def parse_os_release(os_release_path: Optional[str] = None) -> Dict[str, str]:
    """Parse key-value pairs from an os-release file."""
    path = Path(os_release_path) if os_release_path else Path("/etc/os-release")
    if not path.exists():
        # Fallback to /usr/lib/os-release
        path = Path("/usr/lib/os-release")
        if not path.exists():
            return {}

    data: Dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip('\"\'')
                    data[key.strip()] = val
    except OSError:
        pass
    return data


def detect_desktop() -> str:
    """Detect the current desktop environment."""
    raw = (
        os.environ.get("XDG_CURRENT_DESKTOP")
        or os.environ.get("DESKTOP_SESSION")
        or os.environ.get("GDMSESSION")
        or ""
    ).upper()

    if "KDE" in raw or "PLASMA" in raw:
        return "KDE Plasma"
    if "GNOME" in raw:
        return "GNOME"
    if "XFCE" in raw:
        return "XFCE"
    if "CINNAMON" in raw:
        return "Cinnamon"
    if "MATE" in raw:
        return "MATE"
    if "LXQT" in raw:
        return "LXQt"
    if "SWAY" in raw:
        return "Sway"
    if "HYPRLAND" in raw:
        return "Hyprland"
    if "I3" in raw:
        return "i3"
    return raw if raw else "Headless / Unknown"


def detect_distro(os_release_path: Optional[str] = None) -> DistroInfo:
    """Detect distribution details from os-release and system utilities."""
    data = parse_os_release(os_release_path)
    distro_id = data.get("ID", "unknown").lower()
    id_like = data.get("ID_LIKE", "").lower()
    name = data.get("NAME", distro_id.capitalize())
    pretty_name = data.get("PRETTY_NAME", name)
    version_id = data.get("VERSION_ID", "")

    family = "unknown"
    pkg_manager = "unknown"

    # Match ID first
    fedora_ids = {"fedora", "rhel", "rocky", "almalinux", "centos", "nobara"}
    arch_ids = {"arch", "cachyos", "endeavouros", "manjaro", "garuda", "arcolinux", "blackarch", "artix"}
    debian_ids = {"debian", "ubuntu", "pop", "mint", "linuxmint", "kali", "parrot", "zorin", "elementary", "neon"}
    suse_ids = {"opensuse", "opensuse-tumbleweed", "opensuse-leap", "suse", "sles"}

    if distro_id in fedora_ids:
        family = "fedora"
        pkg_manager = "dnf"
    elif distro_id in arch_ids:
        family = "arch"
        pkg_manager = "pacman"
    elif distro_id in debian_ids:
        family = "debian"
        pkg_manager = "apt"
    elif any(distro_id.startswith(s) for s in ["opensuse", "suse", "sles"]):
        family = "opensuse"
        pkg_manager = "zypper"
    else:
        # Fall back to ID_LIKE
        if "arch" in id_like:
            family = "arch"
            pkg_manager = "pacman"
        elif "fedora" in id_like or "rhel" in id_like:
            family = "fedora"
            pkg_manager = "dnf"
        elif "debian" in id_like or "ubuntu" in id_like:
            family = "debian"
            pkg_manager = "apt"
        elif "suse" in id_like:
            family = "opensuse"
            pkg_manager = "zypper"

    # Refine dnf version if dnf5 exists
    dnf_version = None
    if family == "fedora":
        if shutil.which("dnf5"):
            dnf_version = "dnf5"
        elif shutil.which("dnf"):
            dnf_version = "dnf"

    # Check AUR helpers on Arch
    aur_helper = None
    if family == "arch":
        if shutil.which("yay"):
            aur_helper = "yay"
        elif shutil.which("paru"):
            aur_helper = "paru"

    desktop = detect_desktop()
    arch = platform.machine()
    shell = os.environ.get("SHELL", "/bin/bash")

    return DistroInfo(
        id=distro_id,
        name=name,
        pretty_name=pretty_name,
        version_id=version_id,
        family=family,
        package_manager=pkg_manager,
        aur_helper=aur_helper,
        dnf_version=dnf_version,
        desktop=desktop,
        arch=arch,
        shell=shell
    )
