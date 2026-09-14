#!/usr/bin/env bash
# ==========================================================
# distro/opensuse.sh — openSUSE prerequisites
# ==========================================================
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

log "Configuring openSUSE repositories"

sudo zypper --non-interactive refresh
sudo zypper --non-interactive install --no-recommends -y curl wget git ca-certificates

ok "openSUSE base ready"
