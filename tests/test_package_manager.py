"""
tests/test_package_manager.py — Unit tests for package manager abstraction
"""

import unittest
from core.distro import DistroInfo
from core.package_manager import (
    AptManager,
    DnfManager,
    FlatpakManager,
    PacmanManager,
    YayManager,
    ZypperManager,
    get_native_manager,
)


class TestPackageManager(unittest.TestCase):
    def test_dnf_commands(self):
        mgr = DnfManager(use_dnf5=False)
        cmd = mgr.install_command(["git", "curl"])
        self.assertEqual(cmd, ["dnf", "install", "-y", "git", "curl"])
        self.assertTrue(mgr.requires_sudo)
        query = mgr.query_installed_command("git")
        self.assertEqual(query, ["rpm", "-q", "git"])

    def test_pacman_commands(self):
        mgr = PacmanManager()
        cmd = mgr.install_command(["git", "curl"])
        self.assertEqual(cmd, ["pacman", "-S", "--noconfirm", "--needed", "git", "curl"])
        self.assertTrue(mgr.requires_sudo)

    def test_yay_commands(self):
        mgr = YayManager()
        cmd = mgr.install_command(["brave-bin"])
        self.assertEqual(cmd[-1], "brave-bin")
        self.assertFalse(mgr.requires_sudo)

    def test_apt_commands(self):
        mgr = AptManager()
        cmd = mgr.install_command(["git"])
        self.assertEqual(cmd, ["apt-get", "install", "-y", "git"])
        self.assertEqual(mgr.get_env(), {"DEBIAN_FRONTEND": "noninteractive"})
        self.assertTrue(mgr.requires_sudo)

    def test_zypper_commands(self):
        mgr = ZypperManager()
        cmd = mgr.install_command(["git"])
        self.assertEqual(cmd, ["zypper", "--non-interactive", "install", "--no-recommends", "-y", "git"])
        self.assertTrue(mgr.requires_sudo)

    def test_flatpak_commands(self):
        mgr = FlatpakManager()
        cmd = mgr.install_command(["com.visualstudio.code"])
        self.assertEqual(cmd, ["flatpak", "install", "-y", "flathub", "com.visualstudio.code"])
        self.assertFalse(mgr.requires_sudo)

    def test_native_manager_resolution(self):
        fedora_info = DistroInfo("fedora", "Fedora", "Fedora 43", "43", "fedora", "dnf")
        mgr = get_native_manager(fedora_info)
        self.assertIsInstance(mgr, DnfManager)

        arch_info = DistroInfo("arch", "Arch", "Arch Linux", "", "arch", "pacman")
        mgr = get_native_manager(arch_info)
        self.assertIsInstance(mgr, PacmanManager)


if __name__ == "__main__":
    unittest.main()
