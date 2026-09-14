#!/usr/bin/env bash
# ==========================================================
# lib/common.sh — shared helpers used by every script
# ==========================================================

# ---- colors / logging ----
GREEN='\033[1;32m'; YELLOW='\033[1;33m'; RED='\033[1;31m'; NC='\033[0m'

log()   { echo -e "\n${GREEN}==> $1${NC}\n"; }
warn()  { echo -e "${YELLOW}[!] $1${NC}"; }
error() { echo -e "${RED}[x] $1${NC}"; }
ok()    { echo -e "${GREEN}✓${NC} $1"; }

# ---- distro detection ----
# Sets: DISTRO_ID (fedora|arch|debian|ubuntu|...), PKG_MANAGER (dnf|pacman|apt)
detect_distro() {
  if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    source /etc/os-release
    DISTRO_ID="$ID"
    DISTRO_ID_LIKE="${ID_LIKE:-}"
  else
    error "Cannot detect distro (/etc/os-release missing)."
    exit 1
  fi

  case "$DISTRO_ID" in
    fedora)
      PKG_MANAGER="dnf" ;;
    arch|cachyos|endeavouros|manjaro)
      PKG_MANAGER="pacman" ;;
    debian|ubuntu|pop)
      PKG_MANAGER="apt" ;;
    *)
      # fall back on ID_LIKE (e.g. some arch-based distros report differently)
      if [[ "$DISTRO_ID_LIKE" == *arch* ]]; then
        PKG_MANAGER="pacman"
      elif [[ "$DISTRO_ID_LIKE" == *fedora* ]]; then
        PKG_MANAGER="dnf"
      elif [[ "$DISTRO_ID_LIKE" == *debian* ]]; then
        PKG_MANAGER="apt"
      else
        error "Unsupported distro: $DISTRO_ID. Add a case for it in lib/common.sh."
        exit 1
      fi
      ;;
  esac

  export DISTRO_ID PKG_MANAGER
  ok "Detected distro: $DISTRO_ID (package manager: $PKG_MANAGER)"
}

# ---- package manager abstraction ----
# Usage: pkg_install <fedora-name> <arch-name> <debian-name>
# Pass "-" for a name if the package doesn't exist / isn't needed on that distro.
pkg_install() {
  local fedora_pkg="$1" arch_pkg="$2" debian_pkg="$3"
  local pkg=""

  case "$PKG_MANAGER" in
    dnf)    pkg="$fedora_pkg" ;;
    pacman) pkg="$arch_pkg" ;;
    apt)    pkg="$debian_pkg" ;;
  esac

  if [[ "$pkg" == "-" || -z "$pkg" ]]; then
    warn "Skipping (not applicable on $DISTRO_ID)"
    return 0
  fi

  case "$PKG_MANAGER" in
    dnf)    sudo dnf install -y $pkg ;;
    pacman) sudo pacman -S --noconfirm --needed $pkg ;;
    apt)    sudo apt-get install -y $pkg ;;
  esac
}

# Update system package index / upgrade
pkg_update() {
  case "$PKG_MANAGER" in
    dnf)    sudo dnf upgrade --refresh -y ;;
    pacman) sudo pacman -Syu --noconfirm ;;
    apt)    sudo apt-get update -y && sudo apt-get upgrade -y ;;
  esac
}

# Flatpak is cross-distro, so it's handled separately (see scripts/05-apps.sh)
ensure_flatpak() {
  if ! command -v flatpak &>/dev/null; then
    pkg_install flatpak flatpak flatpak
  fi
  flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
}

# Ask yes/no, default yes. Usage: confirm "Install Docker?" && do_thing
confirm() {
  local prompt="${1:-Continue?} [Y/n] "
  local reply
  read -rp "$prompt" reply
  reply=${reply:-Y}
  [[ "$reply" =~ ^[Yy]$ ]]
}
