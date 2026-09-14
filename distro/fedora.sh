#!/usr/bin/env bash
# ==========================================================
# distro/fedora.sh — Fedora-only prerequisites
# ==========================================================
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

log "Enabling RPM Fusion (free + non-free)"
sudo dnf install -y \
  "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm" \
  "https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm"

sudo dnf group upgrade -y core
ok "RPM Fusion ready"
