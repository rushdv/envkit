#!/usr/bin/env bash
# ==========================================================
# distro/fedora.sh — Fedora/RHEL-specific prerequisites
# ==========================================================
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

log "Configuring Fedora / RPM Fusion repositories"

if [[ -f /etc/fedora-release ]]; then
  fedora_ver=$(rpm -E %fedora)
  if ! rpm -q rpmfusion-free-release &>/dev/null; then
    sudo dnf install -y \
      "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-${fedora_ver}.noarch.rpm" \
      "https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-${fedora_ver}.noarch.rpm" || true
  fi
  ok "RPM Fusion configured"
elif [[ -f /etc/redhat-release ]]; then
  info "Enterprise Linux / RHEL derivative detected, enabling EPEL..."
  sudo dnf install -y epel-release || true
fi

ok "Fedora/RHEL base ready"
