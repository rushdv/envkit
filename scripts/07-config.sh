#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

log "[7/7] Final configuration & wrap-up"

# --- Git identity (if not already set) ---
if [[ -z "$(git config --global user.name 2>/dev/null)" ]]; then
  read -rp "Git user.name: " git_name
  read -rp "Git user.email: " git_email
  git config --global user.name "$git_name"
  git config --global user.email "$git_email"
  git config --global init.defaultBranch main
  ok "Git identity configured"
fi

# --- SSH key generation (ed25519) ---
if [[ ! -f "$HOME/.ssh/id_ed25519" ]]; then
  if confirm "No ed25519 SSH key found. Generate one now?"; then
    read -rp "Email for SSH key comment: " ssh_email
    mkdir -p "$HOME/.ssh"
    chmod 700 "$HOME/.ssh"
    ssh-keygen -t ed25519 -C "$ssh_email" -f "$HOME/.ssh/id_ed25519"
    eval "$(ssh-agent -s)" 2>/dev/null || true
    ssh-add "$HOME/.ssh/id_ed25519" 2>/dev/null || true
    echo
    warn "Copy this public key to GitHub/GitLab (Settings > SSH Keys):"
    cat "$HOME/.ssh/id_ed25519.pub"
  fi
fi

echo
log "Setup complete! 🎉"
echo "Recommended post-install actions:"
echo "  1. gh auth login                — Authenticate GitHub CLI"
echo "  2. Restart your session/reboot  — Needed for group permissions (docker, wireshark, libvirt) & default shell"
echo "  3. Open Kitty terminal          — Enjoy JetBrains Mono Nerd Font and Starship prompt"
echo "  4. Check Flatpak permissions    — Run Flatseal to inspect permissions"
