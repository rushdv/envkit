#!/usr/bin/env bash
# ==========================================================
#   Linux Setup Assistant
#   Cross-distro post-install automation
#   Supports: Fedora, Arch-based (CachyOS/EndeavourOS/Manjaro), Debian/Ubuntu
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
=================================
      Linux Setup Assistant
=================================
EOF

detect_distro
echo

# ---- module selection ----
declare -A MODULES=(
  [system]="System update + repo setup (RPM Fusion / yay / apt sources)"
  [dev]="Development tools (git, gh, Node via nvm, Python, PostgreSQL, Docker, VS Code)"
  [terminal]="Terminal environment (zsh, oh-my-zsh, starship, kitty, neovim, tmux, cli utils)"
  [security]="Security tools (nmap, wireshark, VirtualBox, AUR pentest tools where available)"
  [apps]="Daily-use apps via Flatpak (Firefox, Discord, Telegram, VLC, Spotify, etc.)"
  [config]="Final config (git identity, SSH key, wrap-up)"
)
ORDER=(system dev terminal security apps config)

echo "Select what to install (default: all). Enter numbers separated by space, or press Enter for everything."
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

echo
echo "Will install: ${SELECTED[*]}"
confirm "Continue?" || { echo "Aborted."; exit 0; }

for mod in "${SELECTED[@]}"; do
  case "$mod" in
    system)   bash "$SCRIPT_DIR/scripts/01-system.sh" ;;
    dev)      bash "$SCRIPT_DIR/scripts/02-dev.sh" ;;
    terminal) bash "$SCRIPT_DIR/scripts/03-terminal.sh" ;;
    security) bash "$SCRIPT_DIR/scripts/04-security.sh" ;;
    apps)     bash "$SCRIPT_DIR/scripts/05-apps.sh" ;;
    config)   bash "$SCRIPT_DIR/scripts/06-config.sh" ;;
  esac
done

echo
log "All selected modules finished. Reboot recommended."
