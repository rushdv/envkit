#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

log "[2/6] Installing development tools"

# --- build essentials ---
pkg_install "@development-tools" "base-devel" "build-essential"

# --- git + github cli ---
pkg_install git git git
if ! command -v gh &>/dev/null; then
  case "$PKG_MANAGER" in
    dnf)    sudo dnf install -y gh ;;
    pacman) sudo pacman -S --noconfirm --needed github-cli ;;
    apt)
      curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /usr/share/keyrings/githubcli-archive-keyring.gpg >/dev/null
      sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
      sudo apt-get update -y && sudo apt-get install -y gh
      ;;
  esac
fi
ok "git + gh installed"

# --- PostgreSQL ---
pkg_install postgresql postgresql postgresql
pkg_install postgresql-server "-" postgresql-contrib
ok "PostgreSQL installed"

# --- Python ---
pkg_install python3 python python3
pkg_install python3-pip python-pip python3-pip
ok "Python installed"

# --- Node.js via nvm (version-switchable, works identically on every distro) ---
if [[ ! -d "$HOME/.nvm" ]]; then
  log "Installing nvm + Node LTS"
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  # shellcheck disable=SC1091
  source "$NVM_DIR/nvm.sh"
  nvm install --lts
fi

if command -v npm &>/dev/null || [[ -s "$HOME/.nvm/nvm.sh" ]]; then
  export NVM_DIR="$HOME/.nvm"
  # shellcheck disable=SC1091
  [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh"
  npm install -g pnpm typescript prisma
  ok "Node global packages installed (pnpm, typescript, prisma)"
fi

# --- Docker ---
if confirm "Install Docker?"; then
  case "$PKG_MANAGER" in
    dnf)
      sudo dnf install -y dnf-plugins-core
      sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
      sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
      ;;
    pacman)
      sudo pacman -S --noconfirm --needed docker docker-compose
      ;;
    apt)
      curl -fsSL https://get.docker.com | sh
      ;;
  esac
  sudo systemctl enable --now docker
  sudo usermod -aG docker "$USER"
  ok "Docker installed (log out/in for group to apply)"
fi

# --- VS Code ---
if confirm "Install VS Code?"; then
  case "$PKG_MANAGER" in
    dnf)
      sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
      sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'
      sudo dnf install -y code
      ;;
    pacman)
      yay -S --noconfirm visual-studio-code-bin
      ;;
    apt)
      curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
      sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
      echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
      rm -f packages.microsoft.gpg
      sudo apt-get update -y && sudo apt-get install -y code
      ;;
  esac
  ok "VS Code installed"

  # install extension list if VS Code CLI is available
  ext_file="$SCRIPT_DIR/../extensions/vscode-extensions.txt"
  if command -v code &>/dev/null && [[ -f "$ext_file" ]]; then
    while read -r ext; do
      [[ -z "$ext" || "$ext" == \#* ]] && continue
      code --install-extension "$ext" || true
    done < "$ext_file"
    ok "VS Code extensions installed"
  fi
fi
