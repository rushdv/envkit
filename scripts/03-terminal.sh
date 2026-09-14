#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

log "[3/6] Installing terminal environment"

pkg_install zsh zsh zsh
pkg_install kitty kitty kitty
pkg_install neovim neovim neovim
pkg_install tmux tmux tmux
pkg_install htop htop htop
pkg_install btop btop btop
pkg_install ripgrep ripgrep ripgrep
pkg_install fd-find fd fd-find
pkg_install tree tree tree
pkg_install wget wget wget

# Starship prompt (same installer works everywhere)
if ! command -v starship &>/dev/null; then
  curl -sS https://starship.rs/install.sh | sh -s -- -y
  ok "Starship installed"
fi

# Oh My Zsh
if [[ ! -d "$HOME/.oh-my-zsh" ]]; then
  RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
  ok "Oh My Zsh installed"
fi

# Set zsh as default shell
if [[ "$SHELL" != *"zsh"* ]]; then
  chsh -s "$(command -v zsh)"
  ok "Default shell set to zsh (takes effect on next login)"
fi

# Symlink dotfiles from config/ (only if not already present, so it won't clobber your edits)
CONFIG_DIR="$SCRIPT_DIR/../config"
link_if_missing() {
  local src="$1" dest="$2"
  if [[ -f "$src" && ! -e "$dest" ]]; then
    ln -s "$src" "$dest"
    ok "Linked $(basename "$dest")"
  fi
}
mkdir -p "$HOME/.config/kitty"
link_if_missing "$CONFIG_DIR/zshrc"        "$HOME/.zshrc"
link_if_missing "$CONFIG_DIR/starship.toml" "$HOME/.config/starship.toml"
link_if_missing "$CONFIG_DIR/kitty.conf"    "$HOME/.config/kitty/kitty.conf"
link_if_missing "$CONFIG_DIR/gitconfig"     "$HOME/.gitconfig"
