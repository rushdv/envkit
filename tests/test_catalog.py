"""
tests/test_catalog.py — Unit tests for application catalog loading, schema validation, and search
"""

import unittest
from core.catalog import Catalog
from core.distro import DistroInfo


class TestCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = Catalog()

    def test_catalog_loaded_all_apps(self):
        self.assertGreaterEqual(len(self.catalog.apps), 50)
        # Check essential apps exist
        essential = ["vscode", "git", "docker", "firefox", "nodejs", "python", "zsh", "nmap", "obsidian", "vlc"]
        for aid in essential:
            self.assertIn(aid, self.catalog.apps, f"Expected {aid} to be in catalog")

    def test_catalog_categories(self):
        cats = self.catalog.get_categories()
        expected = {"browsers", "development", "terminal", "security", "student", "media", "utilities", "communication"}
        for exp in expected:
            self.assertIn(exp, cats)

    def test_schema_validity(self):
        for aid, app in self.catalog.apps.items():
            self.assertTrue(app.id, f"App {aid} has empty ID")
            self.assertTrue(app.name, f"App {aid} has empty name")
            self.assertTrue(app.description, f"App {aid} has empty description")
            self.assertTrue(app.category, f"App {aid} has empty category")
            self.assertIsInstance(app.tags, list)

    def test_search(self):
        # Exact ID search
        res = self.catalog.search("docker")
        self.assertTrue(any(a.id == "docker" for a in res))

        # Tag search
        res = self.catalog.search("browser")
        self.assertTrue(any(a.id == "firefox" for a in res))

        # Partial description match
        res = self.catalog.search("decompil")
        self.assertTrue(any(a.id in ("ghidra", "jadx") for a in res))

    def test_resolve_install_action(self):
        fedora_info = DistroInfo("fedora", "Fedora", "Fedora 43", "43", "fedora", "dnf")
        arch_info = DistroInfo("arch", "Arch", "Arch Linux", "", "arch", "pacman")

        # VS Code on Fedora
        action = self.catalog.resolve_install_action("vscode", fedora_info)
        self.assertTrue(action.available)
        self.assertEqual(action.manager_name, "dnf")

        # Git on Arch
        action = self.catalog.resolve_install_action("git", arch_info)
        self.assertTrue(action.available)
        self.assertEqual(action.manager_name, "pacman")

        # Invalid app
        action = self.catalog.resolve_install_action("nonexistent-tool-xyz", fedora_info)
        self.assertFalse(action.available)

    def test_flatpak_fallback(self):
        fedora_info = DistroInfo("fedora", "Fedora", "Fedora 43", "43", "fedora", "dnf")
        # Obsidian is packaged primarily via Flatpak
        action = self.catalog.resolve_install_action("obsidian", fedora_info)
        self.assertTrue(action.available)
        self.assertEqual(action.manager_name, "flatpak")


if __name__ == "__main__":
    unittest.main()
