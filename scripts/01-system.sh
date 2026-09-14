#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_distro

log "[1/7] Updating system packages & repositories"
pkg_update

case "$PKG_MANAGER" in
  dnf)    bash "$SCRIPT_DIR/../distro/fedora.sh" ;;
  pacman) bash "$SCRIPT_DIR/../distro/arch.sh" ;;
  apt)    bash "$SCRIPT_DIR/../distro/debian.sh" ;;
  zypper) bash "$SCRIPT_DIR/../distro/opensuse.sh" ;;
esac

ok "System base & repositories ready"
