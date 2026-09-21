"""
envkit core module
"""

from core.distro import DistroInfo, detect_distro, detect_desktop
from core.package_manager import PackageManager, get_native_manager
from core.catalog import Catalog, AppEntry, InstallAction
from core.detector import Detector
from core.installer import InstallRunner, AppStatus, InstallResult
from core.profiles import Profile, ProfileManager
from core.logger import setup_logger, get_logger

__all__ = [
    "DistroInfo",
    "detect_distro",
    "detect_desktop",
    "PackageManager",
    "get_native_manager",
    "Catalog",
    "AppEntry",
    "InstallAction",
    "Detector",
    "InstallRunner",
    "AppStatus",
    "InstallResult",
    "Profile",
    "ProfileManager",
    "setup_logger",
    "get_logger",
]
