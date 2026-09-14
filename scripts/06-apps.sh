#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_distro

log "[6/7] Installing daily-use applications (via Flatpak)"

ensure_flatpak

FLATPAK_APPS=(
  org.mozilla.firefox
  com.discordapp.Discord
  org.telegram.desktop
  org.videolan.VLC
  com.spotify.Client
  com.obsproject.Studio
  org.gimp.GIMP
  com.github.tchx84.Flatseal
)

for app in "${FLATPAK_APPS[@]}"; do
  info "Installing $app..."
  flatpak install -y flathub "$app" || warn "Could not install $app — skipping"
done

ok "Daily-use apps installed"
