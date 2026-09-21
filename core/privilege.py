"""
core/privilege.py — Privilege and safety validation for envkit
"""

import os
import shutil
import subprocess
from typing import List


def is_root() -> bool:
    """Check if the current process is running with root privileges (EUID == 0)."""
    return os.geteuid() == 0


def has_sudo() -> bool:
    """Check if sudo command exists on the host."""
    return shutil.which("sudo") is not None


def check_sudo_cached() -> bool:
    """Check if sudo credentials are currently cached (non-interactive sudo -n)."""
    if not has_sudo():
        return False
    try:
        res = subprocess.run(
            ["sudo", "-n", "true"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3
        )
        return res.returncode == 0
    except (subprocess.SubprocessError, OSError):
        return False


def wrap_sudo(cmd: List[str], requires_sudo: bool = True) -> List[str]:
    """Wrap command with sudo if required and not already running as root."""
    if not requires_sudo or is_root():
        return list(cmd)
    if cmd and cmd[0] == "sudo":
        return list(cmd)
    return ["sudo"] + list(cmd)
