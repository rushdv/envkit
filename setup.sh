#!/usr/bin/env bash
# ==========================================================
#   Linux Setup Assistant (envkit)
#   Universal cross-distro post-install automation
#   Supports: Debian/Ubuntu/Mint/Pop/Kali, Arch/EndeavourOS/CachyOS/Manjaro,
#             Fedora/RHEL/Rocky/Alma, openSUSE Tumbleweed/Leap
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
              Linux Setup Assistant (envkit)
        Universal Cross-Distro Post-Install Engine
==========================================================
EOF

detect_distro
echo

# ---- Module Definitions ----
declare -A MODULES=(
  [system]="System update + repo setup (RPM Fusion / yay / apt sources / zypper)"
  [terminal]="Terminal Powerhouse (Zsh, Starship, Nerd Fonts, Kitty, fzf, bat, eza, zoxide)"
  [dev]="Programmer Suite (C/C++, Rust, Go, Python, Node, Java, Docker, SQLite, Postgres, VS Code)"
  [student]="Student & Academic Suite (Obsidian, Zotero, LibreOffice, Xournal++, Draw.io)"
  [security]="Security Researcher Suite (Nmap, Wireshark, Burp Suite, ZAP, Ghidra, KVM/VirtualBox)"
  [apps]="Everyday Desktop Apps via Flatpak (Firefox, Discord, Telegram, VLC, Spotify, GIMP, OBS)"
  [config]="Final Configuration (Git identity, SSH keygen, aliases, wrap-up)"
)
ORDER=(system terminal dev student security apps config)

echo "Select modules to install (default: all)."
echo "Enter numbers separated by space (e.g. '1 2 3 7' or '1 2 4 6 7'), or press Enter for everything."
echo
i=1
declare -A NUM_TO_KEY
for key in "${ORDER[@]}"; do
  echo "  [$i] $key — ${MODULES[$key]}"
  NUM_TO_KEY[$i]="$key"
  ((i++))
done
echo
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

if [[ ${#SELECTED[@]} -eq 0 ]]; then
  warn "No valid modules selected. Exiting."
  exit 0
fi

echo
echo "Will install modules: ${SELECTED[*]}"
confirm "Continue with installation?" || { echo "Aborted."; exit 0; }

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

echo
log "All selected modules finished successfully! Reboot recommended."
