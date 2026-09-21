"""
core/package_manager.py — Package manager abstraction layer
"""

import shutil
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from core.distro import DistroInfo


class PackageManager(ABC):
    name: str = "base"
    requires_sudo: bool = True

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this package manager is present on the system."""
        pass

    @abstractmethod
    def install_command(self, packages: List[str]) -> List[str]:
        """Construct command to install packages non-interactively."""
        pass

    @abstractmethod
    def update_command(self) -> List[str]:
        """Construct command to update package index / system."""
        pass

    @abstractmethod
    def query_installed_command(self, package: str) -> List[str]:
        """Construct command to check if a package is installed."""
        pass

    def get_env(self) -> Dict[str, str]:
        """Return environment variables required for execution."""
        return {}


class DnfManager(PackageManager):
    name = "dnf"
    requires_sudo = True

    def __init__(self, use_dnf5: Optional[bool] = None, binary: Optional[str] = None):
        if binary:
            self.bin = binary
        elif use_dnf5 is True:
            self.bin = "dnf5"
        elif use_dnf5 is False:
            self.bin = "dnf"
        else:
            self.bin = "dnf5" if shutil.which("dnf5") else "dnf"

    def is_available(self) -> bool:
        return shutil.which(self.bin) is not None

    def install_command(self, packages: List[str]) -> List[str]:
        return [self.bin, "install", "-y"] + packages

    def update_command(self) -> List[str]:
        return [self.bin, "upgrade", "--refresh", "-y"]

    def query_installed_command(self, package: str) -> List[str]:
        return ["rpm", "-q", package]


class PacmanManager(PackageManager):
    name = "pacman"
    requires_sudo = True

    def is_available(self) -> bool:
        return shutil.which("pacman") is not None

    def install_command(self, packages: List[str]) -> List[str]:
        return ["pacman", "-S", "--noconfirm", "--needed"] + packages

    def update_command(self) -> List[str]:
        return ["pacman", "-Syu", "--noconfirm"]

    def query_installed_command(self, package: str) -> List[str]:
        return ["pacman", "-Q", package]


class YayManager(PackageManager):
    """Arch User Repository (AUR) helper."""
    name = "yay"
    requires_sudo = False  # yay invokes sudo internally when needed, should never run as sudo

    def is_available(self) -> bool:
        return shutil.which("yay") is not None or shutil.which("paru") is not None

    def _bin(self) -> str:
        return "yay" if shutil.which("yay") else "paru"

    def install_command(self, packages: List[str]) -> List[str]:
        return [self._bin(), "-S", "--noconfirm", "--needed"] + packages

    def update_command(self) -> List[str]:
        return [self._bin(), "-Syu", "--noconfirm"]

    def query_installed_command(self, package: str) -> List[str]:
        return ["pacman", "-Q", package]


class AptManager(PackageManager):
    name = "apt"
    requires_sudo = True

    def is_available(self) -> bool:
        return shutil.which("apt-get") is not None

    def install_command(self, packages: List[str]) -> List[str]:
        return ["apt-get", "install", "-y"] + packages

    def update_command(self) -> List[str]:
        return ["apt-get", "update", "-y"]

    def query_installed_command(self, package: str) -> List[str]:
        return ["dpkg-query", "-W", "-f=${Status}", package]

    def get_env(self) -> Dict[str, str]:
        return {"DEBIAN_FRONTEND": "noninteractive"}


class ZypperManager(PackageManager):
    name = "zypper"
    requires_sudo = True

    def is_available(self) -> bool:
        return shutil.which("zypper") is not None

    def install_command(self, packages: List[str]) -> List[str]:
        return ["zypper", "--non-interactive", "install", "--no-recommends", "-y"] + packages

    def update_command(self) -> List[str]:
        return ["zypper", "--non-interactive", "refresh"]

    def query_installed_command(self, package: str) -> List[str]:
        return ["rpm", "-q", package]


class FlatpakManager(PackageManager):
    name = "flatpak"
    requires_sudo = False

    def is_available(self) -> bool:
        return shutil.which("flatpak") is not None

    def install_command(self, packages: List[str]) -> List[str]:
        return ["flatpak", "install", "-y", "flathub"] + packages

    def update_command(self) -> List[str]:
        return ["flatpak", "update", "-y"]

    def query_installed_command(self, package: str) -> List[str]:
        return ["flatpak", "info", package]


def get_native_manager(distro_info: DistroInfo) -> Optional[PackageManager]:
    """Return the native package manager instance based on detected distro."""
    family = distro_info.family
    if family == "fedora":
        use_dnf5 = (distro_info.dnf_version == "dnf5")
        return DnfManager(use_dnf5=use_dnf5)
    elif family == "arch":
        return PacmanManager()
    elif family == "debian":
        return AptManager()
    elif family == "opensuse":
        return ZypperManager()
    return None
