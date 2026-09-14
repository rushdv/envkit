#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_distro

log "[4/7] Installing Student, Research & Academic Toolkit"

# --- PDF / Document Viewer ---
info "Installing PDF / Document reader..."
pkg_install okular okular okular okular || pkg_install evince evince evince evince || true

# --- Ensure Flatpak for cross-distro sandboxed student applications ---
ensure_flatpak

STUDENT_APPS=(
  md.obsidian.Obsidian             # Markdown note-taking / Knowledge base
  org.zotero.Zotero                 # Research paper, citation and bibliography manager
  org.libreoffice.LibreOffice       # Full office suite (Docs, Sheets, Slides)
  com.github.xournalpp.xournalpp    # Handwritten notes, PDF annotation, sketching
  com.jgraph.drawio.desktop         # Diagrams, flowcharts, architecture maps
)

for app in "${STUDENT_APPS[@]}"; do
  info "Installing $app via Flatpak..."
  flatpak install -y flathub "$app" || warn "Could not install $app — skipping"
done

ok "Student & Academic suite installed successfully"
