#!/usr/bin/env bash
# ==========================================================
# distro/arch.sh — Arch-based prerequisites (Arch/CachyOS/EndeavourOS/Manjaro)
# ==========================================================
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

log "Configuring Arch base & AUR helper"

sudo pacman -S --noconfirm --needed base-devel git

if ! command -v yay &>/dev/null && ! command -v paru &>/dev/null; then
  log "Installing yay (AUR helper)"
  tmp_dir=$(mktemp -d)
  git clone https://aur.archlinux.org/yay.git "$tmp_dir/yay"
  (cd "$tmp_dir/yay" && makepkg -si --noconfirm)
  rm -rf "$tmp_dir"
fi

ok "Arch base ready (AUR helper configured)"
