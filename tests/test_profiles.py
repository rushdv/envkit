"""
tests/test_profiles.py — Unit tests for profile management, export, and import
"""

import tempfile
import unittest
from pathlib import Path
from core.profiles import Profile, ProfileManager


class TestProfiles(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.pm = ProfileManager(custom_dir=self.tmp_dir.name)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_predefined_profiles_loaded(self):
        profiles = self.pm.list_all()
        ids = [p.id for p in profiles]
        self.assertIn("developer", ids)
        self.assertIn("minimal", ids)
        self.assertIn("student", ids)
        self.assertIn("security", ids)
        self.assertIn("creator", ids)
        self.assertIn("workstation", ids)

    def test_custom_profile_lifecycle(self):
        prof = Profile(
            id="test-custom",
            name="Test Custom Setup",
            description="A custom profile for testing",
            apps=["git", "firefox", "vscode"],
            is_custom=True
        )

        # Save
        saved_path = self.pm.save_custom_profile(prof)
        self.assertTrue(saved_path.exists())

        # Retrieve
        loaded = self.pm.get_profile("test-custom")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.name, "Test Custom Setup")
        self.assertEqual(loaded.apps, ["git", "firefox", "vscode"])

        # Delete
        del_res = self.pm.delete_custom_profile("test-custom")
        self.assertTrue(del_res)
        self.assertIsNone(self.pm.get_profile("test-custom"))

    def test_export_and_import(self):
        prof = Profile(
            id="export-test",
            name="Export Test",
            description="Testing export",
            apps=["git", "curl"]
        )

        export_file = Path(self.tmp_dir.name) / "exported.yaml"
        self.pm.export_profile(prof, str(export_file))
        self.assertTrue(export_file.exists())

        # Import into custom profiles
        imported = self.pm.import_profile(str(export_file))
        self.assertEqual(imported.name, "Export Test")
        self.assertEqual(imported.apps, ["git", "curl"])


if __name__ == "__main__":
    unittest.main()
