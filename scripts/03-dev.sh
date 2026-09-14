#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_distro

log "[3/7] Installing developer & programmer tools"

# --- Build essentials & C/C++ compiler suite ---
info "Installing core build tools (C/C++, Make, CMake, GDB)..."
pkg_install "@development-tools" "base-devel" "build-essential" "devel_basis" || true
pkg_install "gcc-c++ clang cmake make gdb" "clang cmake make gdb" "clang cmake make gdb" "clang cmake make gdb" || true

# --- Git & GitHub CLI ---
pkg_install git git git git
if ! command -v gh &>/dev/null; then
  case "$PKG_MANAGER" in
    dnf)    sudo dnf install -y gh || true ;;
    pacman) sudo pacman -S --noconfirm --needed github-cli || true ;;
    zypper) sudo zypper --non-interactive install -y gh || true ;;
    apt)
      curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /usr/share/keyrings/githubcli-archive-keyring.gpg >/dev/null
      sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
      sudo apt-get update -y && sudo apt-get install -y gh || true
      ;;
  esac
fi
ok "Git & GitHub CLI installed"

# --- Lazygit (Terminal Git UI) ---
pkg_install lazygit lazygit lazygit lazygit || true

# --- Rust (via official rustup — distro agnostic) ---
if ! command -v rustc &>/dev/null; then
  if confirm "Install Rust toolchain (rustc, cargo via rustup)?"; then
    log "Installing Rust (rustup)"
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    # shellcheck disable=SC1091
    [[ -f "$HOME/.cargo/env" ]] && source "$HOME/.cargo/env"
    ok "Rust installed"
  fi
fi

# --- Go runtime ---
if confirm "Install Go (Golang)?"; then
  pkg_install golang go golang go
  ok "Go installed"
fi

# --- Python 3 & virtualenv ---
info "Setting up Python environment..."
pkg_install python3 python python3 python3
pkg_install python3-pip python-pip python3-pip python3-pip || true
pkg_install python3-virtualenv "-" python3-venv python3-virtualenv || true
ok "Python environment ready"

# --- Node.js via nvm (LTS) & Package Managers ---
if [[ ! -d "$HOME/.nvm" ]]; then
  log "Installing nvm + Node.js LTS"
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  # shellcheck disable=SC1091
  [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh"
  nvm install --lts || true
fi

if [[ -s "$HOME/.nvm/nvm.sh" ]]; then
  export NVM_DIR="$HOME/.nvm"
  # shellcheck disable=SC1091
  source "$NVM_DIR/nvm.sh"
  npm install -g pnpm typescript prisma || true
  ok "Node.js (NVM LTS) & global packages (pnpm, typescript, prisma) ready"
fi

# --- Java (OpenJDK LTS) ---
if confirm "Install Java (OpenJDK LTS)?"; then
  pkg_install java-latest-openjdk-devel jdk-openjdk default-jdk java-17-openjdk-devel || true
  ok "Java ready"
fi

# --- Databases (PostgreSQL, SQLite, Redis tools) ---
info "Installing databases & client tools..."
pkg_install postgresql postgresql postgresql postgresql
pkg_install postgresql-server "-" postgresql-contrib postgresql-server || true
pkg_install sqlite sqlite sqlite3 sqlite3
pkg_install redis redis redis-tools redis || true
ok "Databases & CLI clients installed"

# --- Docker & Docker Compose ---
if confirm "Install Docker & Docker Compose?"; then
  case "$PKG_MANAGER" in
    dnf)
      if command -v dnf5 &>/dev/null; then
        sudo dnf config-manager addrepo --from-repofile=https://download.docker.com/linux/fedora/docker-ce.repo || true
      else
        sudo dnf install -y dnf-plugins-core
        sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo || true
      fi
      sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin || true
      ;;
    pacman)
      sudo pacman -S --noconfirm --needed docker docker-compose
      ;;
    apt)
      curl -fsSL https://get.docker.com | sh || true
      ;;
    zypper)
      sudo zypper --non-interactive install -y docker docker-compose || true
      ;;
  esac
  sudo systemctl enable --now docker 2>/dev/null || true
  sudo usermod -aG docker "$USER" 2>/dev/null || true
  ok "Docker installed and enabled (log out/in for group permissions)"
fi

# --- VS Code ---
if confirm "Install Visual Studio Code?"; then
  case "$PKG_MANAGER" in
    dnf)
      sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc || true
      sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/vscode.repo'
      sudo dnf install -y code || true
      ;;
    pacman)
      if command -v yay &>/dev/null; then
        yay -S --noconfirm visual-studio-code-bin || sudo pacman -S --noconfirm --needed code
      else
        sudo pacman -S --noconfirm --needed code
      fi
      ;;
    apt)
      curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/packages.microsoft.gpg
      sudo install -D -o root -g root -m 644 /tmp/packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
      rm -f /tmp/packages.microsoft.gpg
      sudo apt-get update -y && sudo apt-get install -y code || true
      ;;
    zypper)
      sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc || true
      sudo sh -c 'echo -e "[code]\nname=Visual Studio Code\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\nenabled=1\ntype=rpm-md\ngpgcheck=1\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/zypp/repos.d/vscode.repo'
      sudo zypper --non-interactive refresh
      sudo zypper --non-interactive install -y code || true
      ;;
  esac
  ok "Visual Studio Code installed"

  # Install VS Code extensions
  ext_file="$SCRIPT_DIR/../extensions/vscode-extensions.txt"
  if command -v code &>/dev/null && [[ -f "$ext_file" ]]; then
    info "Installing VS Code extensions..."
    while read -r ext; do
      [[ -z "$ext" || "$ext" == \#* ]] && continue
      code --install-extension "$ext" --force || true
    done < "$ext_file"
    ok "VS Code extensions installed"
  fi
fi

# --- API Testing Client (Bruno) & Database GUI (DBeaver) via Flatpak ---
if confirm "Install API & Database GUI tools (Bruno, DBeaver via Flatpak)?"; then
  ensure_flatpak
  flatpak install -y flathub use.bruno.Bruno || true
  flatpak install -y flathub io.dbeaver.DBeaverCommunity || true
  ok "Bruno and DBeaver installed"
fi

ok "Developer & programmer tools setup complete"
