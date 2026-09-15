#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_distro

log "[6/7] Installing GUI Desktop Applications & IDEs"

ensure_flatpak

INSTALLED_DESKTOPS=()

# Helper to install flatpak app and track desktop file
install_flatpak_app() {
  local app_id="$1"
  local app_name="$2"
  local desktop_file="${3:-$app_id.desktop}"

  info "Installing $app_name ($app_id)..."
  if flatpak install -y flathub "$app_id"; then
    ok "$app_name installed successfully"
    INSTALLED_DESKTOPS+=("$desktop_file")
  else
    warn "Could not install $app_name ($app_id) — skipping"
  fi
}

# --- Specialized App Installers ---
install_antigravity_desktop() {
  info "Checking Antigravity IDE desktop integration..."
  mkdir -p "$HOME/.local/share/applications"
  if [[ ! -f "$HOME/.local/share/applications/antigravity.desktop" && ! -f "/usr/share/applications/antigravity.desktop" ]]; then
    cat << 'EOF' > "$HOME/.local/share/applications/antigravity.desktop"
[Desktop Entry]
Name=Antigravity
Comment=Experience liftoff
GenericName=Agentic Platform
Exec=antigravity %U
Icon=antigravity
Type=Application
StartupNotify=false
StartupWMClass=Antigravity
Categories=Development;Utility;
EOF
    chmod +x "$HOME/.local/share/applications/antigravity.desktop"
    ok "Created Antigravity desktop launcher"
  else
    ok "Antigravity desktop launcher verified"
  fi
  INSTALLED_DESKTOPS+=("antigravity.desktop")
}

install_kiro_dev() {
  info "Installing Kiro (AI-Powered IDE & CLI from kiro.dev)..."
  if ! command -v kiro &>/dev/null; then
    curl -fsSL https://cli.kiro.dev/install | bash || warn "Could not run automated Kiro CLI installer"
  fi
  mkdir -p "$HOME/.local/share/applications"
  cat << 'EOF' > "$HOME/.local/share/applications/kiro.desktop"
[Desktop Entry]
Name=Kiro
Comment=AI-Powered Development Environment & Agentic IDE
Exec=kiro %U
Icon=utilities-terminal
Type=Application
Terminal=false
StartupNotify=true
Categories=Development;IDE;
EOF
  chmod +x "$HOME/.local/share/applications/kiro.desktop"
  ok "Kiro Dev desktop launcher registered"
  INSTALLED_DESKTOPS+=("kiro.desktop")
}

install_virtualbox() {
  info "Installing VirtualBox..."
  if ! command -v virtualbox &>/dev/null; then
    pkg_install virtualbox virtualbox virtualbox virtualbox || warn "VirtualBox package manager install skipped or failed"
  fi
  INSTALLED_DESKTOPS+=("virtualbox.desktop")
}

# --- Application Categories ---
install_browsers() {
  log "Installing Modern Web Browsers..."
  install_flatpak_app com.brave.Browser "Brave Browser" "com.brave.Browser.desktop"
  install_flatpak_app app.zen_browser.zen "Zen Browser" "app.zen_browser.zen.desktop"
  install_flatpak_app com.github.micahflee.torbrowser-launcher "Tor Browser Launcher" "com.github.micahflee.torbrowser-launcher.desktop"
  install_flatpak_app org.mozilla.firefox "Mozilla Firefox" "org.mozilla.firefox.desktop"
}

install_media() {
  log "Installing Media & Creative Tools..."
  install_flatpak_app com.obsproject.Studio "OBS Studio" "com.obsproject.Studio.desktop"
  install_flatpak_app org.shotcut.Shotcut "Shotcut Video Editor" "org.shotcut.Shotcut.desktop"
  install_flatpak_app com.spotify.Client "Spotify" "com.spotify.Client.desktop"
  install_flatpak_app org.videolan.VLC "VLC Media Player" "org.videolan.VLC.desktop"
  install_flatpak_app org.gimp.GIMP "GIMP Image Editor" "org.gimp.GIMP.desktop"
}

install_productivity() {
  log "Installing Productivity & Everyday Tools..."
  install_flatpak_app org.qbittorrent.qBittorrent "qBittorrent" "org.qbittorrent.qBittorrent.desktop"
  install_flatpak_app md.obsidian.Obsidian "Obsidian" "md.obsidian.Obsidian.desktop"
  install_flatpak_app com.bitwarden.desktop "Bitwarden" "com.bitwarden.desktop.desktop"
  install_flatpak_app org.telegram.desktop "Telegram Desktop" "org.telegram.desktop.desktop"
  install_flatpak_app com.discordapp.Discord "Discord" "com.discordapp.Discord.desktop"
  install_flatpak_app com.anydesk.Anydesk "AnyDesk Remote Desktop" "com.anydesk.Anydesk.desktop"
  install_flatpak_app com.github.tchx84.Flatseal "Flatseal (Flatpak Permissions Manager)" "com.github.tchx84.Flatseal.desktop"
}

install_ides() {
  log "Installing IDEs & Developer GUI Tools..."
  install_flatpak_app com.visualstudio.code "Visual Studio Code" "com.visualstudio.code.desktop"
  install_flatpak_app com.google.AndroidStudio "Android Studio" "com.google.AndroidStudio.desktop"
  install_virtualbox
  install_antigravity_desktop
  install_kiro_dev
}

# --- Interactive Category Selection ---
echo
echo "Select application categories to install (default: all):"
echo "  [1] All Applications (Browsers, Media, Productivity, IDEs)"
echo "  [2] Browsers (Brave, Zen Browser, Tor Browser, Firefox)"
echo "  [3] Media & Editing (OBS Studio, Shotcut Video Editor, Spotify, VLC, GIMP)"
echo "  [4] Productivity & Utilities (qBittorrent, Obsidian, Bitwarden, Telegram, AnyDesk, Discord)"
echo "  [5] IDEs & Developer GUI (VS Code, Android Studio, VirtualBox, Antigravity, Kiro Dev)"
echo
read -rp "Your choice [1-5 or space-separated, Enter for All]: " app_choice
app_choice="${app_choice:-1}"

DO_ALL=false
DO_BROWSERS=false
DO_MEDIA=false
DO_PROD=false
DO_IDES=false

for opt in $app_choice; do
  case "$opt" in
    1) DO_ALL=true ;;
    2) DO_BROWSERS=true ;;
    3) DO_MEDIA=true ;;
    4) DO_PROD=true ;;
    5) DO_IDES=true ;;
  esac
done

if [[ "$DO_ALL" == true ]]; then
  install_browsers
  install_media
  install_productivity
  install_ides
else
  [[ "$DO_BROWSERS" == true ]] && install_browsers
  [[ "$DO_MEDIA" == true ]] && install_media
  [[ "$DO_PROD" == true ]] && install_productivity
  [[ "$DO_IDES" == true ]] && install_ides
fi

ok "Applications installation phase completed"

# --- Taskbar Pinning Permission Guard ---
echo
info "=========================================================="
info "             Taskbar / Favorites Management               "
info "=========================================================="
echo "Newly installed applications are now available in your system's"
echo "Application Menu / App Launcher."
echo
if confirm_no "Would you like to pin the newly installed applications to your desktop taskbar / favorites?"; then
  info "Pinning selected applications to your taskbar / favorites..."
  for dt in "${INSTALLED_DESKTOPS[@]}"; do
    pin_to_desktop_taskbar "$dt"
  done
  ok "Applications have been pinned to your taskbar / favorites!"
else
  info "Skipped pinning to taskbar. Your taskbar remains untouched."
fi

ok "Desktop applications setup complete!"
