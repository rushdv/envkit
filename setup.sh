#!/usr/bin/env bash
# ==========================================================
#   envkit — Universal Linux Software Installer & Workstation Setup
#   Supports: Fedora/RHEL, Arch/Endeavour, Debian/Ubuntu, openSUSE
# ==========================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

if [[ $EUID -eq 0 ]]; then
  error "Run this as a normal user (it will sudo when needed), not as root."
  exit 1
fi

clear
cat << "EOF"
==========================================================
               envkit — Workstation Builder
           Modular Linux Software Installer
==========================================================
EOF

detect_distro
echo

# 1. Ensure Python 3 & pip/yaml are available
info "Checking runtime dependencies..."
if ! command -v python3 &>/dev/null; then
  warn "Python 3 is required. Installing python3..."
  pkg_install python3 python python3 python3
fi

if ! python3 -c "import yaml" &>/dev/null; then
  info "Installing PyYAML..."
  pkg_install python3-pyyaml python-yaml python3-yaml python3-PyYAML || python3 -m pip install --user pyyaml || true
fi

# 2. Check PySide6 for GUI
HAS_PYSIDE=false
if python3 -c "import PySide6" &>/dev/null; then
  HAS_PYSIDE=true
  ok "PySide6 Qt6 GUI framework ready"
else
  warn "PySide6 is not yet installed. Would you like to install it for the graphical interface?"
  if confirm "Install PySide6 GUI packages now?"; then
    case "$PKG_MANAGER" in
      dnf)    sudo dnf install -y python3-pyside6 || python3 -m pip install --user pyside6 || true ;;
      pacman) sudo pacman -S --noconfirm --needed pyside6 || python3 -m pip install --user pyside6 || true ;;
      apt)    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pyside6 || python3 -m pip install --user pyside6 || true ;;
      zypper) sudo zypper --non-interactive install -y python3-pyside6 || python3 -m pip install --user pyside6 || true ;;
    esac
    if python3 -c "import PySide6" &>/dev/null; then
      HAS_PYSIDE=true
      ok "PySide6 installed successfully"
    fi
  fi
fi

# 3. Ensure local symlink in ~/.local/bin
mkdir -p "$HOME/.local/bin"
if [[ ! -f "$HOME/.local/bin/envkit" ]]; then
  ln -sf "$SCRIPT_DIR/bin/envkit" "$HOME/.local/bin/envkit"
  ok "Registered 'envkit' command in ~/.local/bin"
fi

# Ensure bin/envkit is executable
chmod +x "$SCRIPT_DIR/bin/envkit"

echo
echo "Select setup action (default: 1):"
echo "  [1] Launch envkit (Modular App Installer & Workstation Setup)"
echo "  [2] Run envkit Doctor (System Health & Environment Diagnostics)"
echo "  [3] Run Classic Full Automation Scripts (Legacy 7-Module Run)"
echo "  [4] Exit"
echo
read -rp "Your choice [1-4, Enter for 1]: " action_choice
action_choice="${action_choice:-1}"

case "$action_choice" in
  1)
    echo
    "$SCRIPT_DIR/bin/envkit"
    ;;
  2)
    echo
    "$SCRIPT_DIR/bin/envkit" doctor
    ;;
  3)
    echo
    log "Running classic modular post-install sequence..."
    declare -A MODULES=(
      [system]="System update + repo setup (RPM Fusion / yay / apt sources / zypper)"
      [terminal]="Terminal Powerhouse (Zsh, Starship, Nerd Fonts, Kitty, fzf, bat, eza, zoxide)"
      [dev]="Programmer Suite (C/C++, Rust, Go, Python, Node, Java, Docker, SQLite, Postgres, VS Code)"
      [student]="Student & Academic Suite (Obsidian, Zotero, LibreOffice, Xournal++, Draw.io)"
      [security]="Security Researcher Suite (Nmap, Wireshark, Burp Suite, ZAP, Ghidra, KVM/VirtualBox)"
      [apps]="GUI Desktop Apps & IDEs (Brave, Zen, OBS, Shotcut, qBittorrent, Spotify, AnyDesk, VS Code)"
      [config]="Final Configuration (Git identity, SSH keygen, aliases, wrap-up)"
    )
    ORDER=(system terminal dev student security apps config)

    echo "Select modules to install (default: all):"
    i=1
    declare -A NUM_TO_KEY
    for key in "${ORDER[@]}"; do
      echo "  [$i] $key — ${MODULES[$key]}"
      NUM_TO_KEY[$i]="$key"
      ((i++))
    done
    read -rp "Your choice: " selection

    SELECTED=()
    if [[ -z "$selection" ]]; then
      SELECTED=("${ORDER[@]}")
    else
      for num in $selection; do
        key="${NUM_TO_KEY[$num]:-}"
        [[ -n "$key" ]] && SELECTED+=("$key")
      done
    fi

    for mod in "${SELECTED[@]}"; do
      case "$mod" in
        system)   bash "$SCRIPT_DIR/scripts/01-system.sh" ;;
        terminal) bash "$SCRIPT_DIR/scripts/02-terminal.sh" ;;
        dev)      bash "$SCRIPT_DIR/scripts/03-dev.sh" ;;
        student)  bash "$SCRIPT_DIR/scripts/04-student.sh" ;;
        security) bash "$SCRIPT_DIR/scripts/05-security.sh" ;;
        apps)     bash "$SCRIPT_DIR/scripts/06-apps.sh" ;;
        config)   bash "$SCRIPT_DIR/scripts/07-config.sh" ;;
      esac
    done
    ok "Classic module setup completed!"
    ;;
  *)
    echo "Setup finished. You can run 'envkit' anytime from your terminal."
    ;;
esac
