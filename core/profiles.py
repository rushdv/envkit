"""
core/profiles.py — Predefined & Custom workstation profiles with YAML export/import
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from core.logger import get_logger

logger = get_logger()


@dataclass
class Profile:
    id: str
    name: str
    description: str
    apps: List[str]
    config: Dict[str, Any] = field(default_factory=dict)
    is_custom: bool = False
    file_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "apps": self.apps,
            "config": self.config
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], is_custom: bool = False, file_path: Optional[str] = None) -> "Profile":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", data.get("id", "")),
            description=data.get("description", ""),
            apps=data.get("apps", []),
            config=data.get("config", {}),
            is_custom=is_custom,
            file_path=file_path
        )


def get_custom_profiles_dir() -> Path:
    """Return ~/.config/envkit/profiles/"""
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        base = Path(config_home) / "envkit" / "profiles"
    else:
        base = Path.home() / ".config" / "envkit" / "profiles"
    try:
        base.mkdir(parents=True, exist_ok=True)
    except OSError:
        base = Path("/tmp/envkit/profiles")
        try:
            base.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
    return base


def get_predefined_profiles_dir() -> Path:
    """Return root/profiles/"""
    return Path(__file__).resolve().parent.parent / "profiles"


class ProfileManager:
    def __init__(self, predefined_dir: Optional[str] = None, custom_dir: Optional[str] = None):
        self.predefined_dir = Path(predefined_dir) if predefined_dir else get_predefined_profiles_dir()
        self.custom_dir = Path(custom_dir) if custom_dir else get_custom_profiles_dir()

    def list_all(self) -> List[Profile]:
        """Return all predefined and custom profiles."""
        profiles = []
        # Predefined
        if self.predefined_dir.exists():
            for p in sorted(self.predefined_dir.glob("*.yaml")):
                prof = self._load_file(p, is_custom=False)
                if prof:
                    profiles.append(prof)

        # Custom
        if self.custom_dir.exists():
            for p in sorted(self.custom_dir.glob("*.yaml")):
                prof = self._load_file(p, is_custom=True)
                if prof:
                    profiles.append(prof)

        return profiles

    def get_profile(self, name_or_id_or_path: str) -> Optional[Profile]:
        """Find profile by ID, name, or direct YAML file path."""
        # 1. Direct file path
        path = Path(name_or_id_or_path)
        if path.exists() and path.is_file():
            return self._load_file(path, is_custom=True)

        target = name_or_id_or_path.lower().strip()
        # 2. Check in all profiles
        for p in self.list_all():
            if p.id.lower() == target or p.name.lower() == target:
                return p
        return None

    def save_custom_profile(self, profile: Profile) -> Path:
        """Save custom profile to ~/.config/envkit/profiles/<id>.yaml."""
        clean_id = profile.id.lower().replace(" ", "-")
        target = self.custom_dir / f"{clean_id}.yaml"
        profile.id = clean_id
        profile.is_custom = True
        profile.file_path = str(target)

        with open(target, "w", encoding="utf-8") as f:
            yaml.safe_dump(profile.to_dict(), f, sort_keys=False)
        logger.info(f"Custom profile saved to {target}")
        return target

    def delete_custom_profile(self, profile_id: str) -> bool:
        clean_id = profile_id.lower().replace(" ", "-")
        target = self.custom_dir / f"{clean_id}.yaml"
        if target.exists():
            target.unlink()
            logger.info(f"Custom profile deleted: {target}")
            return True
        return False

    def export_profile(self, profile: Profile, target_file: str) -> Path:
        """Export profile to an external YAML file."""
        target = Path(target_file).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            yaml.safe_dump(profile.to_dict(), f, sort_keys=False)
        logger.info(f"Exported profile to {target}")
        return target

    def import_profile(self, source_file: str) -> Profile:
        """Import a YAML profile file into custom profiles."""
        src = Path(source_file).resolve()
        if not src.exists():
            raise FileNotFoundError(f"File not found: {source_file}")

        profile = self._load_file(src, is_custom=True)
        if not profile:
            raise ValueError(f"Invalid profile YAML in {source_file}")

        self.save_custom_profile(profile)
        return profile

    def _load_file(self, path: Path, is_custom: bool) -> Optional[Profile]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict):
                return None
            if not data.get("id"):
                data["id"] = path.stem
            return Profile.from_dict(data, is_custom=is_custom, file_path=str(path))
        except Exception as e:
            logger.warning(f"Failed to load profile from {path}: {e}")
            return None
