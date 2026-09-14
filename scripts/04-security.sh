#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

log "[4/6] Installing security / pentest tools"

pkg_install nmap nmap nmap
pkg_install wireshark wireshark wireshark

if [[ "$PKG_MANAGER" == "dnf" || "$PKG_MANAGER" == "apt" ]]; then
  sudo usermod -aG wireshark "$USER" 2>/dev/null || true
fi

# Arch/CachyOS/BlackArch users have far more native security packages available
if [[ "$PKG_MANAGER" == "pacman" ]] && command -v yay &>/dev/null; then
  yay -S --noconfirm --needed ghidra jadx burpsuite metasploit || \
    warn "Some AUR security packages failed — install manually if needed"
else
  warn "Burp Suite / Ghidra / JADX / Metasploit have no native Fedora/Debian package."
  warn "Options: (1) download Burp/Ghidra/JADX manually, (2) run Metasploit inside your Kali VM (recommended)."
fi

# VirtualBox — for the Kali VM workflow
if confirm "Install VirtualBox (for your Kali VM)?"; then
  case "$PKG_MANAGER" in
    dnf)
      sudo dnf install -y @virtualization VirtualBox akmod-VirtualBox
      ;;
    pacman)
      sudo pacman -S --noconfirm --needed virtualbox virtualbox-host-modules-arch
      sudo modprobe vboxdrv || warn "Run 'sudo modprobe vboxdrv' after reboot if this failed"
      ;;
    apt)
      sudo apt-get install -y virtualbox virtualbox-ext-pack
      ;;
  esac
  sudo usermod -aG vboxusers "$USER" 2>/dev/null || sudo usermod -aG vboxsf "$USER" 2>/dev/null || true
  ok "VirtualBox installed"
fi
