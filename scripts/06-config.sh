#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

log "[6/6] Final configuration"

# Git identity (only if not already set)
if [[ -z "$(git config --global user.name 2>/dev/null)" ]]; then
  read -rp "Git user.name: " git_name
  read -rp "Git user.email: " git_email
  git config --global user.name "$git_name"
  git config --global user.email "$git_email"
  ok "Git identity set"
fi

# SSH key
if [[ ! -f "$HOME/.ssh/id_ed25519" ]]; then
  if confirm "No SSH key found. Generate one now?"; then
    read -rp "Email for SSH key comment: " ssh_email
    ssh-keygen -t ed25519 -C "$ssh_email" -f "$HOME/.ssh/id_ed25519"
    eval "$(ssh-agent -s)"
    ssh-add "$HOME/.ssh/id_ed25519"
    echo
    warn "Copy this public key to GitHub (Settings > SSH Keys):"
    cat "$HOME/.ssh/id_ed25519.pub"
  fi
fi

echo
log "Setup complete!"
echo "Manual steps still to do:"
echo "  1. gh auth login                — authenticate GitHub CLI"
echo "  2. Restore your Kali VM into VirtualBox"
echo "  3. Reboot — needed for VirtualBox kernel modules, docker/wireshark groups, and default shell"
echo "  4. Review config/ dotfiles and tweak to taste"
