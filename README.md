# envkit — Universal Linux Post-Install & Setup Engine

A modular, cross-distro automation suite designed to set up a complete workstation on a fresh Linux install in minutes. It provides tailored toolsets for **Developers, Students, Programmers, Security Researchers, and Tech Enthusiasts**.

---

## Supported Linux Distributions

Tested and compatible across all major Linux distribution families:

- **Debian Family (`apt`)**: Debian, Ubuntu, Linux Mint, Pop!_OS, Kali Linux, Parrot OS, Zorin OS, Elementary OS.
- **Arch Family (`pacman` / `yay`)**: Arch Linux, EndeavourOS, CachyOS, Manjaro, Garuda, BlackArch.
- **Fedora & Enterprise Family (`dnf` / `dnf5`)**: Fedora, Nobara, RHEL, Rocky Linux, AlmaLinux, CentOS Stream.
- **openSUSE Family (`zypper`)**: openSUSE Tumbleweed, openSUSE Leap.

> **100% Cross-Distro Reliability**: For tools that differ widely between distros (e.g. JetBrains Mono Nerd Font, Rustup, Node.js NVM, Starship, Flatpak apps), `envkit` uses official, distro-agnostic installers to ensure flawless execution everywhere.

---

## Quick Start

```bash
git clone https://github.com/rushdv/linux-setup.git
cd linux-setup
chmod +x setup.sh
./setup.sh
```

You will get an interactive menu where you can install everything or select specific roles/modules:

```
==========================================================
              Linux Setup Assistant (envkit)
        Universal Cross-Distro Post-Install Engine
==========================================================
✓ Detected distro: arch (package manager: pacman)

Select modules to install (default: all).
Enter numbers separated by space (e.g. '1 2 3 7' or '1 2 4 6 7'), or press Enter for everything.

  [1] system   — System update + repo setup (RPM Fusion / yay / apt sources / zypper)
  [2] terminal — Terminal Powerhouse (Zsh, Starship, Nerd Fonts, Kitty, fzf, bat, eza, zoxide)
  [3] dev      — Programmer Suite (C/C++, Rust, Go, Python, Node, Java, Docker, SQLite, Postgres, VS Code)
  [4] student  — Student & Academic Suite (Obsidian, Zotero, LibreOffice, Xournal++, Draw.io)
  [5] security — Security Researcher Suite (Nmap, Wireshark, Burp Suite, ZAP, Ghidra, KVM/VirtualBox)
  [6] apps     — Everyday Desktop Apps via Flatpak (Firefox, Discord, Telegram, VLC, Spotify, GIMP, OBS)
  [7] config   — Final Configuration (Git identity, SSH keygen, aliases, wrap-up)

Your choice:
```

---

## Modules Overview

### 1. `system` (Base & Package Repositories)
- Full system package updates.
- Repository configuration: RPM Fusion (Fedora), AUR helper `yay` (Arch), APT prerequisites (Debian/Ubuntu), Packman/repos (openSUSE).

### 2. `terminal` (Power User & Enthusiast Terminal)
- **Nerd Fonts**: Automatically downloads and installs **JetBrains Mono Nerd Font** to `~/.local/share/fonts/` (enabling crisp glyphs and powerline icons).
- **Shell & Prompt**: Zsh, Oh My Zsh, Starship prompt.
- **Terminal Emulator**: Kitty.
- **Modern CLI Utilities**: `fzf`, `bat`, `eza` (modern ls), `zoxide` (smart cd), `ripgrep`, `fd`, `btop`, `htop`, `fastfetch`, `jq`, `tmux`, `tree`.
- **Pre-configured Dotfiles**: Symlinked cleanly to `$HOME`.

### 3. `dev` (Programmers & Developers)
- **Languages & Runtimes**:
  - C/C++ compiler suite (`gcc`, `g++`, `clang`, `cmake`, `make`, `gdb`)
  - Rust via official `rustup` (`cargo`, `rustc`)
  - Go runtime (`golang`)
  - Python 3 + `pip` + `venv`
  - Node.js via `nvm` (LTS) + `pnpm`, `typescript`, `prisma`
  - Java (OpenJDK LTS)
- **Databases**: PostgreSQL + client, SQLite3, Redis CLI.
- **Containers**: Docker CE + Docker Compose + non-root user group.
- **GUI Tools**: Visual Studio Code (with language extension pack), Lazygit, Bruno API client, DBeaver.

### 4. `student` (Students & Researchers)
- **Knowledge & Notes**: Obsidian (Markdown notes & second brain).
- **Academic Research**: Zotero (research papers, bibliographies, citations).
- **Office Suite**: LibreOffice (Writer, Calc, Impress).
- **Diagrams & Math**: Draw.io (flowcharts & architecture), Xournal++ (handwritten notes & PDF annotation).
- **Documents**: Okular / Evince PDF viewer.

### 5. `security` (Security Researchers & Pentesters)
- **Network Recon & Traffic**: `nmap`, `wireshark` (with non-root capture permissions), `tcpdump`, `socat`, `whois`, `mtr`, `ncat`.
- **Web App Security**: OWASP ZAP, Burp Suite Community.
- **Reverse Engineering**: NSA Ghidra, JADX.
- **Auditing**: Hashcat, John the Ripper.
- **Virtualization**: Native QEMU / KVM / virt-manager (recommended) or VirtualBox (automated non-interactive setup).

### 6. `apps` (Everyday Desktop Apps via Flatpak)
- Mozilla Firefox, Discord, Telegram Desktop, VLC Media Player, Spotify, OBS Studio, GIMP, Flatseal.

### 7. `config` (Final Configuration & Wrap-up)
- Git global user identity (`user.name`, `user.email`, `init.defaultBranch`).
- Modern Ed25519 SSH key generation and GitHub key instructions.
- Clear post-install checklist.

---

## Directory Structure

```
envkit/
├── setup.sh                 # Main entry point & interactive role selector
├── lib/
│   └── common.sh            # Distro detection, pkg_install abstraction, Nerd Font installer
├── distro/
│   ├── arch.sh              # Arch/AUR setup
│   ├── debian.sh            # Debian/Ubuntu APT setup
│   ├── fedora.sh            # Fedora/RHEL RPM Fusion setup
│   └── opensuse.sh          # openSUSE setup
├── scripts/
│   ├── 01-system.sh         # System updates
│   ├── 02-terminal.sh       # Terminal environment & Nerd Fonts
│   ├── 03-dev.sh            # Multi-language programming suite
│   ├── 04-student.sh        # Student & academic suite
│   ├── 05-security.sh       # Security & pentesting suite
│   ├── 06-apps.sh           # Daily Flatpak apps
│   └── 07-config.sh         # Git, SSH, and wrap-up
├── config/                  # Dotfiles symlinked into $HOME
│   ├── gitconfig
│   ├── kitty.conf
│   ├── starship.toml
│   └── zshrc
└── extensions/
    └── vscode-extensions.txt
```

---

## License

MIT — use, fork, and adapt freely.
