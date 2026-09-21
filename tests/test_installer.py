"""
tests/test_installer.py — Unit tests for non-destructive dry-run installation queue
"""

import unittest
from core.catalog import Catalog
from core.distro import DistroInfo
from core.installer import AppStatus, InstallRunner


class TestInstaller(unittest.TestCase):
    def setUp(self):
        self.distro = DistroInfo("fedora", "Fedora", "Fedora 43", "43", "fedora", "dnf")
        self.catalog = Catalog()
        self.runner = InstallRunner(self.distro, self.catalog, dry_run=True)

    def test_dry_run_queue(self):
        started = []
        statuses = {}

        self.runner.on_app_start = lambda aid, idx, tot: started.append(aid)
        self.runner.on_app_status = lambda aid, st, msg: statuses.update({aid: st})

        results = self.runner.run_queue(["git", "vscode"], skip_installed=False)

        self.assertEqual(len(results), 2)
        self.assertIn("git", started)
        self.assertIn("vscode", started)
        self.assertEqual(results["git"].status, AppStatus.SUCCESS)
        self.assertEqual(results["vscode"].status, AppStatus.SUCCESS)

    def test_unavailable_app_in_queue(self):
        results = self.runner.run_queue(["completely-bogus-app-xyz"], skip_installed=False)
        self.assertEqual(results["completely-bogus-app-xyz"].status, AppStatus.UNAVAILABLE)


if __name__ == "__main__":
    unittest.main()
