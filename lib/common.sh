#!/usr/bin/env bash
# ==========================================================
# lib/common.sh — shared helpers used by every script
# ==========================================================

# ---- colors / logging ----
GREEN='\033[1;32m'; YELLOW='\033[1;33m'; RED='\033[1;31m'; BLUE='\033[1;34m'; NC='\033[0m'

log()   { echo -e "\n${GREEN}==> $1${NC}\n"; }
info()  { echo -e "${BLUE}[*] $1${NC}"; }
warn()  { echo -e "${YELLOW}[!] $1${NC}"; }
error() { echo -e "${RED}[x] $1${NC}"; }
ok()    { echo -e "${GREEN}✓${NC} $1"; }

# ---- distro detection ----
# Sets: DISTRO_ID, PKG_MANAGER (dnf|pacman|apt|zypper)
detect_distro() {
  if [[ -n "${DISTRO_ID:-}" && -n "${PKG_MANAGER:-}" ]]; then
    return 0
  fi

  if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    DISTRO_ID="${ID:-unknown}"
    DISTRO_ID_LIKE="${ID_LIKE:-}"
  else
    error "Cannot detect distro (/etc/os-release missing)."
    exit 1
  fi

  case "$DISTRO_ID" in
    fedora|rhel|rocky|almalinux|centos|nobara)
      PKG_MANAGER="dnf" ;;
    arch|cachyos|endeavouros|manjaro|garuda|arcolinux|blackarch)
      PKG_MANAGER="pacman" ;;
    debian|ubuntu|pop|mint|linuxmint|kali|parrot|zorin|elementary|neon)
      PKG_MANAGER="apt" ;;
    opensuse*|suse|sles)
      PKG_MANAGER="zypper" ;;
    *)
      # Fall back on ID_LIKE
      if [[ "$DISTRO_ID_LIKE" == *arch* ]]; then
        PKG_MANAGER="pacman"
      elif [[ "$DISTRO_ID_LIKE" == *fedora* || "$DISTRO_ID_LIKE" == *rhel* ]]; then
        PKG_MANAGER="dnf"
      elif [[ "$DISTRO_ID_LIKE" == *debian* || "$DISTRO_ID_LIKE" == *ubuntu* ]]; then
        PKG_MANAGER="apt"
      elif [[ "$DISTRO_ID_LIKE" == *suse* ]]; then
        PKG_MANAGER="zypper"
      else
        error "Unsupported distro: $DISTRO_ID (ID_LIKE: $DISTRO_ID_LIKE)."
        warn "You can still run individual scripts manually or install packages with your package manager."
        exit 1
      fi
      ;;
  esac

  export DISTRO_ID PKG_MANAGER
  ok "Detected distro: $DISTRO_ID (package manager: $PKG_MANAGER)"
}

# ---- package manager abstraction ----
# Usage: pkg_install <fedora-pkg> <arch-pkg> <debian-pkg> <opensuse-pkg>
# Pass "-" for a name if the package doesn't exist / isn't needed on that distro.
pkg_install() {
  local fedora_pkg="${1:-}"
  local arch_pkg="${2:-}"
  local debian_pkg="${3:-}"
  local opensuse_pkg="${4:-}"
  local pkg=""

  case "$PKG_MANAGER" in
    dnf)    pkg="$fedora_pkg" ;;
    pacman) pkg="$arch_pkg" ;;
    apt)    pkg="$debian_pkg" ;;
    zypper) pkg="$opensuse_pkg" ;;
  esac

  if [[ "$pkg" == "-" || -z "$pkg" ]]; then
    return 0
  fi

  info "Installing $pkg ($PKG_MANAGER)..."
  case "$PKG_MANAGER" in
    dnf)
      sudo dnf install -y $pkg ;;
    pacman)
      sudo pacman -S --noconfirm --needed $pkg ;;
    apt)
      sudo DEBIAN_FRONTEND=noninteractive apt-get install -y $pkg ;;
    zypper)
      sudo zypper --non-interactive install --no-recommends $pkg ;;
  esac
}

# Update system package index / upgrade
pkg_update() {
  info "Updating package lists and upgrading system packages..."
  case "$PKG_MANAGER" in
    dnf)
      sudo dnf upgrade --refresh -y ;;
    pacman)
      sudo pacman -Syu --noconfirm ;;
    apt)
      sudo DEBIAN_FRONTEND=noninteractive apt-get update -y && \
      sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y ;;
    zypper)
      sudo zypper --non-interactive refresh && \
      sudo zypper --non-interactive update -y ;;
  esac
}

# Flatpak is cross-distro, guaranteed on every modern Linux desktop
ensure_flatpak() {
  if ! command -v flatpak &>/dev/null; then
    info "Installing Flatpak..."
    pkg_install flatpak flatpak flatpak flatpak
  fi
  if command -v flatpak &>/dev/null; then
    flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo 2>/dev/null || true
    ok "Flatpak & Flathub ready"
  else
    warn "Flatpak could not be initialized."
  fi
}

# Universal JetBrains Mono Nerd Font installer (distro-agnostic)
install_nerd_font() {
  local font_dir="$HOME/.local/share/fonts/JetBrainsMonoNerd"
  if [[ -d "$font_dir" && $(ls -1 "$font_dir" 2>/dev/null | wc -l) -gt 0 ]]; then
    ok "JetBrains Mono Nerd Font is already installed"
    return 0
  fi

  log "Installing JetBrains Mono Nerd Font (for icons & powerline prompts)"
  mkdir -p "$font_dir"
  local tmp_zip
  tmp_zip=$(mktemp --suffix=.zip)
  local font_url="https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.zip"

  if curl -fLo "$tmp_zip" "$font_url"; then
    if command -v unzip &>/dev/null; then
      unzip -q -o "$tmp_zip" -d "$font_dir"
    else
      warn "unzip command missing, attempting package install..."
      pkg_install unzip unzip unzip unzip
      unzip -q -o "$tmp_zip" -d "$font_dir"
    fi
    rm -f "$tmp_zip"
    if command -v fc-cache &>/dev/null; then
      fc-cache -f "$HOME/.local/share/fonts" 2>/dev/null || true
    fi
    ok "JetBrains Mono Nerd Font installed"
  else
    rm -f "$tmp_zip"
    warn "Failed to download Nerd Font from GitHub. You can install it manually."
  fi
}

# Symlink compatibility for Debian tools (e.g. fdfind -> fd, batcat -> bat)
fix_debian_symlinks() {
  if [[ "$PKG_MANAGER" == "apt" ]]; then
    mkdir -p "$HOME/.local/bin"
    if command -v fdfind &>/dev/null && ! command -v fd &>/dev/null; then
      ln -sf "$(command -v fdfind)" "$HOME/.local/bin/fd"
      ok "Symlinked fdfind -> ~/.local/bin/fd"
    fi
    if command -v batcat &>/dev/null && ! command -v bat &>/dev/null; then
      ln -sf "$(command -v batcat)" "$HOME/.local/bin/bat"
      ok "Symlinked batcat -> ~/.local/bin/bat"
    fi
  fi
}

# Ask yes/no, default yes. Usage: confirm "Install Docker?" && do_thing
confirm() {
  local prompt="${1:-Continue?} [Y/n] "
  local reply
  read -rp "$prompt" reply
  reply=${reply:-Y}
  [[ "$reply" =~ ^[Yy]$ ]]
}

# Ask yes/no, default no. Usage: confirm_no "Pin to taskbar?" && do_thing
confirm_no() {
  local prompt="${1:-Continue?} [y/N] "
  local reply
  read -rp "$prompt" reply
  reply=${reply:-N}
  [[ "$reply" =~ ^[Yy]$ ]]
}

# Pin an application (.desktop file ID or name) to the user's desktop taskbar/dock
# Supports GNOME Shell and KDE Plasma; safe and idempotent.
pin_to_desktop_taskbar() {
  local app_desktop="$1"
  [[ -z "$app_desktop" ]] && return 0

  # Ensure .desktop extension
  [[ "$app_desktop" != *.desktop ]] && app_desktop="${app_desktop}.desktop"

  local desktop="${XDG_CURRENT_DESKTOP:-${DESKTOP_SESSION:-}}"

  # 1. GNOME / Ubuntu Dash
  if [[ "$desktop" =~ (GNOME|Ubuntu) ]] && command -v gsettings &>/dev/null; then
    local current_favs
    current_favs=$(gsettings get org.gnome.shell favorite-apps 2>/dev/null || echo "[]")
    if [[ "$current_favs" != *"$app_desktop"* ]]; then
      if [[ "$current_favs" == "[]" || "$current_favs" == "@as []" ]]; then
        gsettings set org.gnome.shell favorite-apps "['$app_desktop']" 2>/dev/null || true
      else
        local updated_favs="${current_favs%]}, '$app_desktop']"
        gsettings set org.gnome.shell favorite-apps "$updated_favs" 2>/dev/null || true
      fi
      ok "Pinned $app_desktop to GNOME Dash"
    fi
    return 0
  fi

  # 2. KDE Plasma Task Manager
  if [[ "$desktop" =~ (KDE|plasma) ]]; then
    local plasma_cfg="$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc"
    if [[ -f "$plasma_cfg" ]]; then
      if ! grep -q "$app_desktop" "$plasma_cfg" 2>/dev/null; then
        sed -i "/^launchers=/ s/$/,applications:${app_desktop}/" "$plasma_cfg" 2>/dev/null || true
        ok "Pinned $app_desktop to KDE Plasma Taskbar"
      fi
    fi
    return 0
  fi

  info "Application $app_desktop is ready in your Application Menu."
}
