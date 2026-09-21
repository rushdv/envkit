"""
core/config.py — Configuration management (Git, SSH, Shell, Dotfiles, VS Code extensions, Taskbar)
"""

import os
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from core.distro import detect_desktop
from core.logger import get_logger

logger = get_logger()


def pin_to_desktop_taskbar(desktop_file: str) -> bool:
    """
    Pin .desktop file to GNOME Dash or KDE Plasma Task Manager safely and idempotently.
    Requires explicit user consent before calling.
    """
    if not desktop_file:
        return False

    if not desktop_file.endswith(".desktop"):
        desktop_file += ".desktop"

    de = detect_desktop().upper()

    # 1. GNOME / Ubuntu Dash
    if "GNOME" in de and shutil.which("gsettings"):
        try:
            res = subprocess.run(
                ["gsettings", "get", "org.gnome.shell", "favorite-apps"],
                capture_output=True,
                text=True,
                check=True
            )
            favs_str = res.stdout.strip()
            if desktop_file not in favs_str:
                if favs_str in ("[]", "@as []", ""):
                    new_favs = f"['{desktop_file}']"
                else:
                    new_favs = favs_str[:-1] + f", '{desktop_file}']"
                subprocess.run(
                    ["gsettings", "set", "org.gnome.shell", "favorite-apps", new_favs],
                    check=True
                )
                logger.info(f"Pinned {desktop_file} to GNOME Dash")
                return True
            return True
        except Exception as e:
            logger.warning(f"Could not pin to GNOME Dash: {e}")
            return False

    # 2. KDE Plasma
    if "KDE" in de or "PLASMA" in de:
        cfg = Path.home() / ".config" / "plasma-org.kde.plasma.desktop-appletsrc"
        if cfg.exists():
            try:
                content = cfg.read_text(encoding="utf-8")
                if desktop_file not in content:
                    lines = content.splitlines()
                    new_lines = []
                    modified = False
                    for line in lines:
                        if line.startswith("launchers="):
                            line = f"{line},applications:{desktop_file}"
                            modified = True
                        new_lines.append(line)
                    if modified:
                        cfg.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
                        logger.info(f"Pinned {desktop_file} to KDE Plasma Taskbar")
                        return True
            except Exception as e:
                logger.warning(f"Could not pin to KDE Plasma: {e}")
                return False

    return False


def configure_git_identity(name: str, email: str, default_branch: str = "main") -> bool:
    """Configure global Git identity."""
    try:
        subprocess.run(["git", "config", "--global", "user.name", name], check=True)
        subprocess.run(["git", "config", "--global", "user.email", email], check=True)
        subprocess.run(["git", "config", "--global", "init.defaultBranch", default_branch], check=True)
        logger.info(f"Git identity configured for {name} <{email}>")
        return True
    except Exception as e:
        logger.error(f"Failed to configure Git identity: {e}")
        return False


def generate_ssh_key(email: str, key_type: str = "ed25519") -> Tuple[bool, str]:
    """Generate an SSH key pair (default Ed25519) and return public key."""
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(mode=0o700, exist_ok=True)
    key_path = ssh_dir / f"id_{key_type}"

    if key_path.exists():
        pub_path = key_path.with_suffix(".pub")
        if pub_path.exists():
            return True, pub_path.read_text().strip()
        return True, f"Key already exists at {key_path}"

    try:
        subprocess.run(
            ["ssh-keygen", "-t", key_type, "-C", email, "-f", str(key_path), "-N", ""],
            check=True,
            capture_output=True,
            text=True
        )
        pub_path = key_path.with_suffix(".pub")
        pub_content = pub_path.read_text().strip()
        return True, pub_content
    except Exception as e:
        logger.error(f"Failed to generate SSH key: {e}")
        return False, str(e)


def symlink_dotfiles(config_dir: Optional[str] = None) -> List[Tuple[str, bool, str]]:
    """
    Symlink dotfiles (zshrc, starship.toml, kitty.conf, gitconfig) into user's HOME.
    Returns list of (file_name, success, message).
    """
    src_dir = Path(config_dir) if config_dir else Path(__file__).resolve().parent.parent / "config"
    results = []
    if not src_dir.exists():
        return [("config", False, f"Config directory {src_dir} not found")]

    links = {
        "zshrc": Path.home() / ".zshrc",
        "starship.toml": Path.home() / ".config" / "starship.toml",
        "kitty.conf": Path.home() / ".config" / "kitty" / "kitty.conf",
        "gitconfig": Path.home() / ".gitconfig",
    }

    for name, dest in links.items():
        src = src_dir / name
        if not src.exists():
            continue
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() or dest.is_symlink():
                results.append((name, True, f"Already exists at {dest}"))
            else:
                dest.symlink_to(src)
                results.append((name, True, f"Symlinked {src} -> {dest}"))
        except Exception as e:
            results.append((name, False, str(e)))

    return results


def install_nerd_fonts() -> bool:
    """Download and install JetBrains Mono Nerd Font to ~/.local/share/fonts."""
    font_dir = Path.home() / ".local" / "share" / "fonts" / "JetBrainsMonoNerd"
    if font_dir.exists() and any(font_dir.iterdir()):
        logger.info("JetBrains Mono Nerd Font already installed.")
        return True

    font_dir.mkdir(parents=True, exist_ok=True)
    url = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.zip"
    zip_path = Path("/tmp") / "JetBrainsMono.zip"

    try:
        logger.info(f"Downloading JetBrains Mono Nerd Font from {url}...")
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(font_dir)
        zip_path.unlink(missing_ok=True)

        if shutil.which("fc-cache"):
            subprocess.run(["fc-cache", "-f", str(font_dir.parent)], check=False)
        logger.info("JetBrains Mono Nerd Font installed successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to install Nerd Font: {e}")
        zip_path.unlink(missing_ok=True)
        return False


def install_vscode_extensions(ext_file: Optional[str] = None) -> List[Tuple[str, bool]]:
    """Install VS Code extensions listed in extensions/vscode-extensions.txt."""
    if not shutil.which("code"):
        return [("code", False)]

    file_path = Path(ext_file) if ext_file else Path(__file__).resolve().parent.parent / "extensions" / "vscode-extensions.txt"
    if not file_path.exists():
        return []

    results = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                ext = line.strip()
                if not ext or ext.startswith("#"):
                    continue
                res = subprocess.run(
                    ["code", "--install-extension", ext, "--force"],
                    capture_output=True,
                    text=True
                )
                results.append((ext, res.returncode == 0))
    except Exception as e:
        logger.error(f"Error installing VS Code extensions: {e}")

    return results
