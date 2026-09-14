#!/usr/bin/env bash
# ==========================================================
# distro/debian.sh — Debian/Ubuntu-family prerequisites
# ==========================================================
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

log "Configuring Debian/Ubuntu repository prerequisites"

sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  software-properties-common apt-transport-https ca-certificates curl gnupg lsb-release

ok "Debian/Ubuntu base ready"
