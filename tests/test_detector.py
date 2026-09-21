"""
tests/test_detector.py — Unit tests for installed application detector
"""

import unittest
from core.catalog import AppEntry
from core.detector import Detector
from core.distro import DistroInfo


class TestDetector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.distro = DistroInfo("fedora", "Fedora", "Fedora 43", "43", "fedora", "dnf")
        cls.detector = Detector(cls.distro)

    def test_detect_python_command(self):
        app = AppEntry(
            id="python-test",
            name="Python Test",
            description="Test",
            category="development",
            detection={"commands": ["python3"]}
        )
        status, detail = self.detector.is_installed(app)
        self.assertEqual(status, "installed")
        self.assertIn("python3", detail)

    def test_detect_nonexistent_command(self):
        app = AppEntry(
            id="fake-app-123",
            name="Fake App",
            description="Test",
            category="utilities",
            detection={"commands": ["nonexistent_binary_xyz_123"]}
        )
        status, _ = self.detector.is_installed(app)
        self.assertEqual(status, "not_installed")

    def test_cache_functionality(self):
        app = AppEntry(
            id="cached-app",
            name="Cached App",
            description="Test",
            category="utilities",
            detection={"commands": ["sh"]}
        )
        status1, _ = self.detector.is_installed(app)
        self.assertEqual(status1, "installed")
        self.assertIn("cached-app", self.detector._cache)


if __name__ == "__main__":
    unittest.main()
