#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_distro

log "[2/7] Installing terminal environment & power tools"

# --- Core terminal & multiplexer ---
pkg_install zsh zsh zsh zsh
pkg_install kitty kitty kitty kitty
pkg_install neovim neovim neovim neovim
pkg_install tmux tmux tmux tmux

# --- Essential & modern CLI utilities ---
pkg_install curl curl curl curl
pkg_install wget wget wget wget
pkg_install unzip unzip unzip unzip
pkg_install tree tree tree tree
pkg_install jq jq jq jq
pkg_install htop htop htop htop
pkg_install btop btop btop btop
pkg_install ripgrep ripgrep ripgrep ripgrep
pkg_install fd-find fd fd-find fd
pkg_install bat bat bat bat
pkg_install fzf fzf fzf fzf
pkg_install zoxide zoxide zoxide zoxide || true
pkg_install eza eza eza eza || true
pkg_install fastfetch fastfetch fastfetch fastfetch || true

# --- Symlink compatibility for Debian/Ubuntu (fdfind -> fd, batcat -> bat) ---
fix_debian_symlinks

# --- JetBrains Mono Nerd Font (guarantees crisp icons in Starship & Kitty) ---
install_nerd_font

# --- Starship prompt ---
if ! command -v starship &>/dev/null; then
  log "Installing Starship prompt"
  curl -sS https://starship.rs/install.sh | sh -s -- -y
  ok "Starship installed"
fi

# --- Oh My Zsh ---
if [[ ! -d "$HOME/.oh-my-zsh" ]]; then
  log "Installing Oh My Zsh"
  RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" || true
  ok "Oh My Zsh installed"
fi

# --- Set default shell to Zsh ---
if [[ "${SHELL:-}" != *"zsh"* ]] && command -v zsh &>/dev/null; then
  if confirm "Set Zsh as your default shell?"; then
    chsh -s "$(command -v zsh)" "$USER" 2>/dev/null || chsh -s "$(command -v zsh)" 2>/dev/null || true
    ok "Default shell set to zsh"
  fi
fi

# --- Symlink dotfiles ---
CONFIG_DIR="$SCRIPT_DIR/../config"
link_if_missing() {
  local src="$1" dest="$2"
  if [[ -f "$src" && ! -e "$dest" ]]; then
    mkdir -p "$(dirname "$dest")"
    ln -s "$src" "$dest"
    ok "Linked $(basename "$dest")"
  fi
}

mkdir -p "$HOME/.config/kitty"
link_if_missing "$CONFIG_DIR/zshrc"        "$HOME/.zshrc"
link_if_missing "$CONFIG_DIR/starship.toml" "$HOME/.config/starship.toml"
link_if_missing "$CONFIG_DIR/kitty.conf"    "$HOME/.config/kitty/kitty.conf"
link_if_missing "$CONFIG_DIR/gitconfig"     "$HOME/.gitconfig"

ok "Terminal environment ready"
