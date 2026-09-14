#!/usr/bin/env bash
# ==========================================================
# distro/debian.sh — Debian/Ubuntu-only prerequisites
# ==========================================================
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

log "Adding common PPAs / sources"
sudo apt-get update -y
sudo apt-get install -y software-properties-common apt-transport-https ca-certificates curl gnupg
ok "Debian/Ubuntu base ready"
