"""
tests/test_distro.py — Unit tests for distro and desktop environment detection
"""

import tempfile
import unittest
from pathlib import Path
from core.distro import DistroInfo, detect_desktop, detect_distro, parse_os_release


class TestDistroDetection(unittest.TestCase):
    def _create_temp_os_release(self, content: str) -> str:
        tf = tempfile.NamedTemporaryFile("w", delete=False)
        tf.write(content)
        tf.close()
        return tf.name

    def test_fedora_detection(self):
        content = """NAME="Fedora Linux"
ID=fedora
VERSION_ID=43
PRETTY_NAME="Fedora Linux 43"
"""
        path = self._create_temp_os_release(content)
        try:
            info = detect_distro(path)
            self.assertEqual(info.family, "fedora")
            self.assertEqual(info.package_manager, "dnf")
            self.assertEqual(info.version_id, "43")
        finally:
            Path(path).unlink(missing_ok=True)

    def test_arch_family_detection(self):
        content = """NAME="EndeavourOS"
ID=endeavouros
ID_LIKE=arch
PRETTY_NAME="EndeavourOS Linux"
"""
        path = self._create_temp_os_release(content)
        try:
            info = detect_distro(path)
            self.assertEqual(info.family, "arch")
            self.assertEqual(info.package_manager, "pacman")
        finally:
            Path(path).unlink(missing_ok=True)

    def test_debian_family_detection(self):
        content = """NAME="Ubuntu"
ID=ubuntu
ID_LIKE=debian
VERSION_ID="24.04"
PRETTY_NAME="Ubuntu 24.04 LTS"
"""
        path = self._create_temp_os_release(content)
        try:
            info = detect_distro(path)
            self.assertEqual(info.family, "debian")
            self.assertEqual(info.package_manager, "apt")
        finally:
            Path(path).unlink(missing_ok=True)

    def test_opensuse_detection(self):
        content = """NAME="openSUSE Tumbleweed"
ID="opensuse-tumbleweed"
ID_LIKE="opensuse suse"
PRETTY_NAME="openSUSE Tumbleweed"
"""
        path = self._create_temp_os_release(content)
        try:
            info = detect_distro(path)
            self.assertEqual(info.family, "opensuse")
            self.assertEqual(info.package_manager, "zypper")
        finally:
            Path(path).unlink(missing_ok=True)

    def test_unsupported_distro(self):
        content = """NAME="TempleOS"
ID=templeos
"""
        path = self._create_temp_os_release(content)
        try:
            info = detect_distro(path)
            self.assertEqual(info.family, "unknown")
            self.assertEqual(info.package_manager, "unknown")
        finally:
            Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
