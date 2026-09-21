# envkit — Modular Linux Software & Workstation Setup Tool

> **A modular Linux software installer and workstation builder that lets users install exactly what they need.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)](#supported-distributions)
[![Python 3](https://img.shields.io/badge/Python-3.9+-brightgreen.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt6-blueviolet.svg)](https://wiki.qt.io/Qt_for_Python)

---

## 1. Overview

`envkit` transforms workstation setup on Linux into a seamless, data-driven experience engineered specifically for Linux power users, developers, students, and security researchers.

Instead of forcing users to install giant monolithic software bundles, `envkit` enables you to:
1. Launch `envkit` via a modern Qt6 desktop GUI or interactive CLI.
2. Browse a centralized, data-driven application catalog across 8 categories.
3. Automatically detect already-installed applications and view their exact presence.
4. Pick and choose individual applications or select a curated profile.
5. Review estimated package changes and skipped software.
6. Install missing software with live streaming progress, non-blocking logs, and automatic cross-distro package resolution.
7. Save your environment as a custom profile, export it to YAML, and reconstruct your exact workstation on a fresh install or different Linux distribution in minutes.

---

## 2. Screenshots

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  envkit 2.0 — Workstation Setup                                                 - □ ×  │
├───────────────┬────────────────────────────────────────────────────────────────────────┤
│ 🏠 Home       │  Welcome to envkit                                                     │
│ 📦 Applications│  Fedora Linux 44 (KDE Plasma) • dnf5 • x86_64                           │
│ 📋 Profiles   │                                                                        │
│ ✓  Installed  │  ┌──────────────────────────────┐  ┌──────────────────────────────┐    │
│ ⚙️ Settings    │  │ 💻 Development               │  │ ⚡ Terminal Powerhouse        │    │
│ ℹ️ About       │  │ Compilers, IDEs, databases   │  │ Shells, prompts, modern CLI  │    │
│               │  └──────────────────────────────┘  └──────────────────────────────┘    │
│               │                                                                        │
│               │  70 Applications Available  •  63 Installed  •  [Browse Catalog →]     │
└───────────────┴────────────────────────────────────────────────────────────────────────┘
```

*(Place screenshots of the Catalog, Review, and Real-Time Installation views in `assets/screenshots/`)*

---

## 3. Features

- **Effortless Modular Setup**: Select what you want, review what's missing, click Install, and you're done.
- **Unified Core Engine**: The PySide6 Qt6 GUI and the CLI (`envkit`) share 100% of the backend logic, catalog loader, detector, and installer runner.
- **Cross-Distro Abstraction**: Automatically detects and uses `dnf` / `dnf5` (Fedora/RHEL), `pacman` / `yay` (Arch), `apt` (Debian/Ubuntu), and `zypper` (openSUSE).
- **Universal Flatpak Integration**: Fallback and native support for sandboxed Flathub packages.
- **Intelligent Detection Engine**: High-speed detection across binary `$PATH`, package manager queries (`rpm`, `dpkg`, `pacman`), Flatpak registries, and dotfiles/toolchain paths (`~/.nvm`, `~/.cargo`).
- **Data-Driven Catalog**: Over 70+ applications organized into structured YAML files. Add new applications in under 2 minutes without modifying installer code.
- **Curated & Custom Profiles**: Built-in profiles for Developers, Students, Security Researchers, Creators, and Minimalists, plus local custom profile creation, export, and import.
- **Real-Time Asynchronous Installation**: Live per-app status indicators, non-blocking Qt worker thread, stdout/stderr streaming log console, and retry for failed packages.
- **Strict Installation Safety**: No shell `eval`, structured command argument arrays, non-root execution, targeted privilege escalation only when required, and XDG-compliant state/logging (`~/.local/state/envkit/logs/`).
- **Desktop Guard**: Explicit confirmation before pinning any application to GNOME Dash or KDE Plasma taskbars.

---

## 4. Supported Distributions

| Family | Supported Distributions | Default Package Manager | Secondary / Fallback |
| :--- | :--- | :--- | :--- |
| **Fedora / RHEL** | Fedora, Nobara, RHEL, Rocky Linux, AlmaLinux, CentOS Stream | `dnf` / `dnf5` | Flatpak (Flathub) |
| **Arch Linux** | Arch Linux, EndeavourOS, CachyOS, Manjaro, Garuda, BlackArch | `pacman` | `yay` / `paru` (AUR), Flatpak |
| **Debian / Ubuntu** | Debian, Ubuntu, Linux Mint, Pop!_OS, Kali Linux, Parrot OS, Zorin | `apt` | Flatpak (Flathub) |
| **openSUSE** | openSUSE Tumbleweed, openSUSE Leap, SUSE Linux Enterprise | `zypper` | Flatpak (Flathub) |

---

## 5. Installation & Quick Start

Clone the repository and run the setup bootstrapper:

```bash
git clone https://github.com/rushdv/envkit.git
cd envkit
chmod +x setup.sh
./setup.sh
```

The bootstrapper checks runtime dependencies (Python 3, PyYAML, PySide6) and registers the `envkit` command in `~/.local/bin/`.

After setup, simply run:
```bash
envkit
```
- If running in a graphical desktop session (X11 / Wayland) with PySide6, `envkit` launches the **modern Qt6 GUI**.
- If running in a headless environment, SSH session, or without GUI libraries, `envkit` seamlessly falls back to the **interactive CLI menu**.

---

## 6. GUI Usage

1. **Sidebar Navigation**: Switch easily between **Home**, **Applications**, **Profiles**, **Installed**, **Settings**, and **About**.
2. **Browsing & Search**: In the Applications tab, search instantly across names, descriptions, tags, and commands. Filter by category pills or toggle *Hide installed*.
3. **Selection**: Click any card or the `+ Select` button to queue it. The bottom action bar tracks your total selection count in real time.
4. **Review & Confirm**: Click **Review & Install →** to see a clean breakdown of what is already installed vs what will be installed. Optionally enable desktop taskbar pinning.
5. **Real-time Installation**: Watch live progress with per-app indicators (`⟳ Installing`, `✓ Installed`, `✕ Failed`). Expand the live log console to view output in real time.

---

## 7. CLI Usage

The CLI provides full scriptability and automation for terminal users and headless servers:

### Subcommands Reference

| Command | Description |
| :--- | :--- |
| `envkit` | Launch graphical interface (or interactive CLI in terminal) |
| `envkit --gui` | Force launch the PySide6 Qt6 GUI |
| `envkit --cli` | Force launch the interactive CLI menu |
| `envkit doctor` | Run system diagnostics (distro, package manager, sudo, network, flatpak, DE) |
| `envkit list [-c <category>]` | List catalog applications with install status |
| `envkit search <query>` | Instant fuzzy search across catalog applications |
| `envkit installed` | List all applications detected as installed on the system |
| `envkit install <id...>` | Install one or more applications by ID |
| `envkit install <id...> --dry-run` | Simulate installation without making any system changes |
| `envkit install <id...> -y` | Non-interactive install (auto-accept confirmation) |
| `envkit profiles` | List all built-in and custom profiles |
| `envkit install-profile <name_or_file>` | Install all software defined in a profile |
| `envkit export <file.yaml>` | Export detected workstation setup into a profile YAML |
| `envkit export <file.yaml> -p <id>` | Export a specific profile to an external YAML file |

### CLI Examples

```bash
# Diagnostic check
envkit doctor

# Search for container tools
envkit search docker

# Install developer tools non-interactively
envkit install git vscode docker nodejs -y

# Simulate installation without changes
envkit install postgresql bruno --dry-run

# Install a predefined profile
envkit install-profile developer

# Export your workstation setup after a fresh install
envkit export my-workstation.yaml

# Reinstall on a new machine using the exported profile
envkit install-profile my-workstation.yaml
```

---

## 8. Application Catalog

`envkit` includes a curated catalog of 70+ applications organized across 8 categories:

- **Browsers**: Firefox, Brave, Chromium, Zen Browser, Tor Browser
- **Development**: Visual Studio Code, Git, GitHub CLI, Docker, Docker Compose, Node.js, NVM, Python 3, Rust, Go, Java (OpenJDK), GCC, Clang, CMake, PostgreSQL, SQLite, Redis, DBeaver Community, Bruno API Client, Android Studio
- **Terminal**: Zsh, Starship Prompt, Kitty, tmux, fzf, ripgrep (`rg`), fd, bat, eza, zoxide, btop, fastfetch, jq, tree, JetBrains Mono Nerd Font
- **Security**: Nmap, Wireshark, tcpdump, Burp Suite Community, OWASP ZAP, NSA Ghidra, JADX, Hashcat, John the Ripper, socat, whois, ncat
- **Student & Academic**: Obsidian, Zotero, LibreOffice, Xournal++, Okular, Evince, Draw.io
- **Media & Creative**: OBS Studio, VLC Media Player, GIMP, Shotcut, Spotify
- **Communication**: Telegram Desktop, Discord
- **Utilities**: Bitwarden, AnyDesk, Flatseal, qBittorrent

---

## 9. Profiles

Predefined profiles are located in `profiles/`:

- **Minimal Essentials (`minimal.yaml`)**: Git, Firefox.
- **Developer Suite (`developer.yaml`)**: Git, GitHub CLI, VS Code, Node.js, Python, Docker, Docker Compose, PostgreSQL, SQLite, Redis, Bruno, DBeaver.
- **Student & Academic (`student.yaml`)**: Firefox, Obsidian, Zotero, LibreOffice, Okular, Xournal++, Draw.io.
- **Security Researcher (`security.yaml`)**: Nmap, Wireshark, tcpdump, Burp Suite, OWASP ZAP, Ghidra, JADX, Hashcat, John the Ripper, socat, whois, ncat.
- **Content Creator & Media (`creator.yaml`)**: OBS Studio, VLC, GIMP, Shotcut, Spotify.
- **Complete Workstation (`workstation.yaml`)**: Curated daily-driver collection spanning productivity, dev tools, and utilities.

### Custom Profiles
Custom profiles are stored locally in `~/.config/envkit/profiles/` and can be managed directly in the GUI or via `envkit export` / `envkit install-profile`.

---

## 10. Architecture

`envkit` decouples presentation, catalog data, and system execution into distinct modular layers:

```text
                 ┌─────────────────────────┐
                 │     User Interfaces     │
                 │   PySide6 GUI  /  CLI   │
                 └────────────┬────────────┘
                              │
                 ┌────────────▼────────────┐
                 │       Core Engine       │
                 │    (InstallRunner)      │
                 └──────┬───────────┬──────┘
                        │           │
         ┌──────────────▼──┐     ┌──▼──────────────┐
         │  YAML Catalog   │     │ Installed State │
         │  70+ App Configs│     │    Detector     │
         └──────────────┬──┘     └──┬──────────────┘
                        │           │
                 ┌──────▼───────────▼──────┐
                 │  Package Manager Layer  │
                 └──────┬───────────┬──────┘
                        │           │
      ┌────────────┬────┴─────┬─────┴──────┬────────────┐
      │            │          │            │            │
  apt-get         dnf       pacman       zypper      flatpak
 (Debian)      (Fedora)     (Arch)     (openSUSE)   (Flathub)
```

### Directory Structure

```text
envkit/
├── bin/
│   └── envkit                   # Main CLI & GUI executable
├── envkit                       # Root wrapper symlink
├── setup.sh                     # Dependency installer & setup wizard
│
├── core/                        # Shared Python Core Backend
│   ├── catalog.py               # YAML catalog loader, schema, and search
│   ├── config.py                # Git, SSH, dotfiles, and desktop pinning
│   ├── detector.py              # Application detection engine
│   ├── distro.py                # Cross-distro and desktop detection
│   ├── installer.py             # Asynchronous runner with real-time logs
│   ├── logger.py                # XDG-compliant file and console logging
│   ├── package_manager.py       # Package manager abstraction layer
│   ├── privilege.py             # Privilege checks and sudo guards
│   └── profiles.py              # Profile loader, manager, export/import
│
├── catalog/                     # Modular Application Definitions
│   ├── browsers/
│   ├── communication/
│   ├── development/
│   ├── media/
│   ├── security/
│   ├── student/
│   ├── terminal/
│   └── utilities/
│
├── profiles/                    # Built-in YAML Profiles
│   ├── creator.yaml
│   ├── developer.yaml
│   ├── minimal.yaml
│   ├── security.yaml
│   ├── student.yaml
│   └── workstation.yaml
│
├── gui/                         # Modern PySide6 Qt6 GUI
│   ├── app.py                   # Qt application entrypoint
│   ├── main_window.py           # Sidebar & view routing
│   ├── theme.py                 # Modern dark theme styling
│   ├── views/                   # Views (Home, Catalog, Review, Install, etc.)
│   └── widgets/                 # Reusable widgets (AppCard, LogConsole)
│
├── distro/                      # Distro base configuration scripts
├── config/                      # Dotfiles (gitconfig, kitty.conf, starship, zshrc)
├── modules/                     # Legacy module entrypoints
├── scripts/                     # Preserved setup scripts
├── tests/                       # Automated unit tests
└── README.md
```

---

## 11. Adding a New Application

Adding software to `envkit` requires zero code changes to installer logic. Simply drop a new `.yaml` file into `catalog/<category>/<app_id>.yaml`:

```yaml
id: myapp
name: My Cool App
description: A high-performance utility for Linux
category: development
tags:
  - utility
  - dev
homepage: https://example.com/myapp
icon: myapp
source_preference: native

packages:
  fedora: myapp
  arch: myapp
  debian: myapp-cli
  opensuse: myapp
  flatpak:
    id: com.example.MyApp

detection:
  commands:
    - myapp
  flatpak: com.example.MyApp
```

`envkit` automatically indexes the file, adds it to the catalog and search index, and resolves the correct package on whatever distribution the user runs.

---

## 12. Troubleshooting

### Diagnostics Check
Run `envkit doctor` to verify your environment, active package manager, and required tools:
```bash
envkit doctor
```

### Viewing Logs
Installation logs are stored with session timestamps in:
```bash
~/.local/state/envkit/logs/
```

### GUI Doesn't Open
If PySide6 dependencies are missing:
- **Fedora**: `sudo dnf install python3-pyside6`
- **Arch**: `sudo pacman -S pyside6`
- **Ubuntu/Debian**: `sudo apt install python3-pyside6`
- **pip**: `pip install --user PySide6 PyYAML`

Alternatively, `envkit` runs fully in interactive CLI mode:
```bash
envkit --cli
```

---

## 13. Contributing

1. Fork the repository (`https://github.com/rushdv/envkit`).
2. Create your feature branch (`git checkout -b feature/new-app`).
3. Add or update application YAML files in `catalog/` or core logic in `core/`.
4. Run automated tests to verify everything passes:
   ```bash
   python3 -m unittest discover -s tests -p "test_*.py" -v
   ```
5. Commit your changes and submit a Pull Request.

---

## 14. License

Released under the [MIT License](LICENSE). Built with ❤️ for the Linux community.
