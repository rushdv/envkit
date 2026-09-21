"""
scripts/populate_catalog.py — Catalog populator for envkit
Generates structured YAML catalog entries for all required applications.
"""

import os
from pathlib import Path
import yaml

CATALOG_DIR = Path(__file__).resolve().parent.parent / "catalog"

APPS = [
    # ---- BROWSERS ----
    {
        "id": "firefox",
        "name": "Mozilla Firefox",
        "description": "Fast, private, and independent web browser by Mozilla",
        "category": "browsers",
        "tags": ["browser", "web", "internet", "mozilla"],
        "homepage": "https://www.mozilla.org/firefox/",
        "icon": "firefox",
        "source_preference": "native",
        "packages": {
            "fedora": "firefox",
            "arch": "firefox",
            "debian": "firefox-esr",
            "opensuse": "MozillaFirefox",
            "flatpak": {"id": "org.mozilla.firefox"}
        },
        "detection": {
            "commands": ["firefox"],
            "flatpak": "org.mozilla.firefox"
        }
    },
    {
        "id": "brave",
        "name": "Brave Browser",
        "description": "Privacy-focused browser that blocks trackers and ads automatically",
        "category": "browsers",
        "tags": ["browser", "privacy", "chromium", "adblock"],
        "homepage": "https://brave.com/",
        "icon": "brave-browser",
        "source_preference": "flatpak",
        "packages": {
            "arch": {"manager": "yay", "package": "brave-bin"},
            "flatpak": {"id": "com.brave.Browser"}
        },
        "detection": {
            "commands": ["brave-browser", "brave"],
            "flatpak": "com.brave.Browser"
        }
    },
    {
        "id": "chromium",
        "name": "Chromium",
        "description": "Open-source browser project that powers Google Chrome and others",
        "category": "browsers",
        "tags": ["browser", "open-source", "web", "google"],
        "homepage": "https://www.chromium.org/",
        "icon": "chromium",
        "source_preference": "native",
        "packages": {
            "fedora": "chromium",
            "arch": "chromium",
            "debian": "chromium",
            "opensuse": "chromium",
            "flatpak": {"id": "org.chromium.Chromium"}
        },
        "detection": {
            "commands": ["chromium", "chromium-browser"],
            "flatpak": "org.chromium.Chromium"
        }
    },
    {
        "id": "zen-browser",
        "name": "Zen Browser",
        "description": "Beautiful, fast, and feature-rich Firefox fork with vertical tabs",
        "category": "browsers",
        "tags": ["browser", "firefox", "modern", "tabs"],
        "homepage": "https://zen-browser.app/",
        "icon": "zen-browser",
        "source_preference": "flatpak",
        "packages": {
            "arch": {"manager": "yay", "package": "zen-browser-bin"},
            "flatpak": {"id": "app.zen_browser.zen"}
        },
        "detection": {
            "commands": ["zen-browser", "zen"],
            "flatpak": "app.zen_browser.zen"
        }
    },
    {
        "id": "tor-browser",
        "name": "Tor Browser",
        "description": "Protect your privacy and defend yourself against network surveillance and censorship",
        "category": "browsers",
        "tags": ["browser", "tor", "privacy", "anonymity", "security"],
        "homepage": "https://www.torproject.org/",
        "icon": "tor-browser",
        "source_preference": "flatpak",
        "packages": {
            "fedora": "torbrowser-launcher",
            "arch": "torbrowser-launcher",
            "debian": "torbrowser-launcher",
            "opensuse": "torbrowser-launcher",
            "flatpak": {"id": "com.github.micahflee.torbrowser-launcher"}
        },
        "detection": {
            "commands": ["torbrowser-launcher"],
            "flatpak": "com.github.micahflee.torbrowser-launcher"
        }
    },

    # ---- DEVELOPMENT ----
    {
        "id": "vscode",
        "name": "Visual Studio Code",
        "description": "Extensible code editor and IDE developed by Microsoft",
        "category": "development",
        "tags": ["editor", "ide", "microsoft", "code", "programming"],
        "homepage": "https://code.visualstudio.com/",
        "icon": "code",
        "source_preference": "native",
        "packages": {
            "fedora": "code",
            "arch": "code",
            "debian": "code",
            "opensuse": "code",
            "flatpak": {"id": "com.visualstudio.code"}
        },
        "detection": {
            "commands": ["code"],
            "flatpak": "com.visualstudio.code"
        }
    },
    {
        "id": "git",
        "name": "Git",
        "description": "Distributed version control system designed for speed and data integrity",
        "category": "development",
        "tags": ["vcs", "git", "version-control", "cli"],
        "homepage": "https://git-scm.com/",
        "icon": "git",
        "source_preference": "native",
        "packages": {
            "fedora": "git",
            "arch": "git",
            "debian": "git",
            "opensuse": "git"
        },
        "detection": {
            "commands": ["git"]
        }
    },
    {
        "id": "gh",
        "name": "GitHub CLI",
        "description": "GitHub’s official command-line tool bringing PRs, issues, and actions to your terminal",
        "category": "development",
        "tags": ["git", "github", "cli", "pull-requests"],
        "homepage": "https://cli.github.com/",
        "icon": "github",
        "source_preference": "native",
        "packages": {
            "fedora": "gh",
            "arch": "github-cli",
            "debian": "gh",
            "opensuse": "gh"
        },
        "detection": {
            "commands": ["gh"]
        }
    },
    {
        "id": "docker",
        "name": "Docker",
        "description": "Pack, ship and run any application as a lightweight container",
        "category": "development",
        "tags": ["containers", "devops", "docker", "server"],
        "homepage": "https://www.docker.com/",
        "icon": "docker",
        "source_preference": "native",
        "packages": {
            "fedora": "docker-ce",
            "arch": "docker",
            "debian": "docker.io",
            "opensuse": "docker"
        },
        "detection": {
            "commands": ["docker"]
        },
        "post_install": [
            {"group": "docker"},
            {"service": "docker"}
        ],
        "reboot_recommended": True
    },
    {
        "id": "docker-compose",
        "name": "Docker Compose",
        "description": "Tool for defining and running multi-container Docker applications",
        "category": "development",
        "tags": ["docker", "containers", "orchestration", "compose"],
        "homepage": "https://docs.docker.com/compose/",
        "icon": "docker",
        "source_preference": "native",
        "packages": {
            "fedora": "docker-compose-plugin",
            "arch": "docker-compose",
            "debian": "docker-compose-plugin",
            "opensuse": "docker-compose"
        },
        "detection": {
            "commands": ["docker-compose", "docker"]
        }
    },
    {
        "id": "nodejs",
        "name": "Node.js",
        "description": "JavaScript runtime built on Chrome's V8 engine",
        "category": "development",
        "tags": ["javascript", "node", "npm", "runtime", "web"],
        "homepage": "https://nodejs.org/",
        "icon": "nodejs",
        "source_preference": "native",
        "packages": {
            "fedora": "nodejs npm",
            "arch": "nodejs npm",
            "debian": "nodejs npm",
            "opensuse": "nodejs npm"
        },
        "detection": {
            "commands": ["node", "npm"]
        }
    },
    {
        "id": "nvm",
        "name": "NVM (Node Version Manager)",
        "description": "Simple bash script to manage multiple active Node.js versions",
        "category": "development",
        "tags": ["nodejs", "nvm", "version-manager", "javascript"],
        "homepage": "https://github.com/nvm-sh/nvm",
        "icon": "nodejs",
        "source_preference": "script",
        "packages": {
            "script": {
                "command": "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash",
                "requires_sudo": False
            }
        },
        "detection": {
            "paths": ["~/.nvm/nvm.sh"]
        }
    },
    {
        "id": "python",
        "name": "Python 3 & Pip",
        "description": "High-level, general-purpose programming language and pip package manager",
        "category": "development",
        "tags": ["python", "pip", "scripting", "ai", "backend"],
        "homepage": "https://www.python.org/",
        "icon": "python",
        "source_preference": "native",
        "packages": {
            "fedora": "python3 python3-pip python3-virtualenv",
            "arch": "python python-pip python-virtualenv",
            "debian": "python3 python3-pip python3-venv",
            "opensuse": "python3 python3-pip python3-virtualenv"
        },
        "detection": {
            "commands": ["python3", "pip3"]
        }
    },
    {
        "id": "rust",
        "name": "Rust (rustup)",
        "description": "Systems programming language focusing on safety, speed, and concurrency",
        "category": "development",
        "tags": ["rust", "cargo", "systems", "performance"],
        "homepage": "https://www.rust-lang.org/",
        "icon": "rust",
        "source_preference": "script",
        "packages": {
            "script": {
                "command": "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y",
                "requires_sudo": False
            }
        },
        "detection": {
            "commands": ["rustc", "cargo"],
            "paths": ["~/.cargo/bin/rustc"]
        }
    },
    {
        "id": "go",
        "name": "Go (Golang)",
        "description": "Fast, statically typed, compiled language designed for simplicity and scalability",
        "category": "development",
        "tags": ["go", "golang", "google", "cloud", "concurrency"],
        "homepage": "https://go.dev/",
        "icon": "go",
        "source_preference": "native",
        "packages": {
            "fedora": "golang",
            "arch": "go",
            "debian": "golang",
            "opensuse": "go"
        },
        "detection": {
            "commands": ["go"]
        }
    },
    {
        "id": "java",
        "name": "Java (OpenJDK LTS)",
        "description": "Open-source implementation of the Java Platform, Standard Edition",
        "category": "development",
        "tags": ["java", "openjdk", "jvm", "backend", "android"],
        "homepage": "https://openjdk.org/",
        "icon": "java",
        "source_preference": "native",
        "packages": {
            "fedora": "java-latest-openjdk-devel",
            "arch": "jdk-openjdk",
            "debian": "default-jdk",
            "opensuse": "java-17-openjdk-devel"
        },
        "detection": {
            "commands": ["javac", "java"]
        }
    },
    {
        "id": "gcc",
        "name": "GCC & Build Essentials",
        "description": "GNU Compiler Collection C/C++ compilers, make, and base build tools",
        "category": "development",
        "tags": ["c", "cpp", "compiler", "gcc", "make"],
        "homepage": "https://gcc.gnu.org/",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "gcc gcc-c++ make",
            "arch": "base-devel",
            "debian": "build-essential",
            "opensuse": "devel_basis"
        },
        "detection": {
            "commands": ["gcc", "g++", "make"]
        }
    },
    {
        "id": "clang",
        "name": "Clang & LLVM",
        "description": "C, C++, and Objective-C compiler front-end for LLVM",
        "category": "development",
        "tags": ["c", "cpp", "llvm", "clang", "compiler"],
        "homepage": "https://clang.llvm.org/",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "clang",
            "arch": "clang",
            "debian": "clang",
            "opensuse": "clang"
        },
        "detection": {
            "commands": ["clang", "clang++"]
        }
    },
    {
        "id": "cmake",
        "name": "CMake",
        "description": "Cross-platform open-source build system generator",
        "category": "development",
        "tags": ["build", "cmake", "c", "cpp"],
        "homepage": "https://cmake.org/",
        "icon": "cmake",
        "source_preference": "native",
        "packages": {
            "fedora": "cmake",
            "arch": "cmake",
            "debian": "cmake",
            "opensuse": "cmake"
        },
        "detection": {
            "commands": ["cmake"]
        }
    },
    {
        "id": "postgresql",
        "name": "PostgreSQL",
        "description": "Powerful, open source object-relational database system",
        "category": "development",
        "tags": ["sql", "database", "postgres", "rdbms"],
        "homepage": "https://www.postgresql.org/",
        "icon": "postgresql",
        "source_preference": "native",
        "packages": {
            "fedora": "postgresql postgresql-server",
            "arch": "postgresql",
            "debian": "postgresql postgresql-client",
            "opensuse": "postgresql postgresql-server"
        },
        "detection": {
            "commands": ["psql", "postgres"]
        }
    },
    {
        "id": "sqlite",
        "name": "SQLite",
        "description": "C-language library that implements a small, fast, self-contained SQL database engine",
        "category": "development",
        "tags": ["sql", "database", "sqlite", "embedded"],
        "homepage": "https://www.sqlite.org/",
        "icon": "sqlite",
        "source_preference": "native",
        "packages": {
            "fedora": "sqlite",
            "arch": "sqlite",
            "debian": "sqlite3",
            "opensuse": "sqlite3"
        },
        "detection": {
            "commands": ["sqlite3"]
        }
    },
    {
        "id": "redis",
        "name": "Redis CLI",
        "description": "In-memory data structure store used as a database, cache, and message broker",
        "category": "development",
        "tags": ["nosql", "cache", "redis", "in-memory"],
        "homepage": "https://redis.io/",
        "icon": "redis",
        "source_preference": "native",
        "packages": {
            "fedora": "redis",
            "arch": "redis",
            "debian": "redis-tools",
            "opensuse": "redis"
        },
        "detection": {
            "commands": ["redis-cli"]
        }
    },
    {
        "id": "dbeaver",
        "name": "DBeaver Community",
        "description": "Universal database tool for developers, database administrators, and analysts",
        "category": "development",
        "tags": ["database", "gui", "sql", "postgres", "mysql"],
        "homepage": "https://dbeaver.io/",
        "icon": "dbeaver",
        "source_preference": "flatpak",
        "packages": {
            "arch": "dbeaver",
            "flatpak": {"id": "io.dbeaver.DBeaverCommunity"}
        },
        "detection": {
            "commands": ["dbeaver"],
            "flatpak": "io.dbeaver.DBeaverCommunity"
        }
    },
    {
        "id": "bruno",
        "name": "Bruno",
        "description": "Fast and git-friendly open-source API client for exploring and testing APIs",
        "category": "development",
        "tags": ["api", "rest", "graphql", "http", "postman-alternative"],
        "homepage": "https://www.usebruno.com/",
        "icon": "bruno",
        "source_preference": "flatpak",
        "packages": {
            "arch": {"manager": "yay", "package": "bruno-bin"},
            "flatpak": {"id": "use.bruno.Bruno"}
        },
        "detection": {
            "commands": ["bruno"],
            "flatpak": "use.bruno.Bruno"
        }
    },
    {
        "id": "android-studio",
        "name": "Android Studio",
        "description": "Official Integrated Development Environment for Android app development",
        "category": "development",
        "tags": ["android", "mobile", "ide", "kotlin", "java"],
        "homepage": "https://developer.android.com/studio",
        "icon": "android-studio",
        "source_preference": "flatpak",
        "packages": {
            "arch": {"manager": "yay", "package": "android-studio"},
            "flatpak": {"id": "com.google.AndroidStudio"}
        },
        "detection": {
            "commands": ["studio.sh"],
            "flatpak": "com.google.AndroidStudio"
        }
    },

    # ---- TERMINAL ----
    {
        "id": "zsh",
        "name": "Zsh Shell",
        "description": "Extended Bourne shell with many improvements, themes, and plugin support",
        "category": "terminal",
        "tags": ["shell", "zsh", "terminal", "cli"],
        "homepage": "https://www.zsh.org/",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "zsh",
            "arch": "zsh",
            "debian": "zsh",
            "opensuse": "zsh"
        },
        "detection": {
            "commands": ["zsh"]
        }
    },
    {
        "id": "starship",
        "name": "Starship Prompt",
        "description": "Minimal, blazing-fast, and infinitely customizable prompt for any shell",
        "category": "terminal",
        "tags": ["prompt", "starship", "shell", "zsh", "bash"],
        "homepage": "https://starship.rs/",
        "icon": "utilities-terminal",
        "source_preference": "script",
        "packages": {
            "arch": "starship",
            "script": {
                "command": "curl -sS https://starship.rs/install.sh | sh -s -- -y",
                "requires_sudo": True
            }
        },
        "detection": {
            "commands": ["starship"]
        }
    },
    {
        "id": "kitty",
        "name": "Kitty Terminal",
        "description": "Fast, feature-rich, GPU-based terminal emulator",
        "category": "terminal",
        "tags": ["terminal", "emulator", "gpu", "kitty"],
        "homepage": "https://sw.kovidgoyal.net/kitty/",
        "icon": "kitty",
        "source_preference": "native",
        "packages": {
            "fedora": "kitty",
            "arch": "kitty",
            "debian": "kitty",
            "opensuse": "kitty"
        },
        "detection": {
            "commands": ["kitty"]
        }
    },
    {
        "id": "tmux",
        "name": "tmux",
        "description": "Terminal multiplexer enabling multi-window terminal sessions",
        "category": "terminal",
        "tags": ["multiplexer", "terminal", "tmux", "productivity"],
        "homepage": "https://github.com/tmux/tmux/wiki",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "tmux",
            "arch": "tmux",
            "debian": "tmux",
            "opensuse": "tmux"
        },
        "detection": {
            "commands": ["tmux"]
        }
    },
    {
        "id": "fzf",
        "name": "fzf",
        "description": "General-purpose command-line fuzzy finder",
        "category": "terminal",
        "tags": ["fuzzy", "search", "cli", "terminal"],
        "homepage": "https://github.com/junegunn/fzf",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "fzf",
            "arch": "fzf",
            "debian": "fzf",
            "opensuse": "fzf"
        },
        "detection": {
            "commands": ["fzf"]
        }
    },
    {
        "id": "ripgrep",
        "name": "ripgrep (rg)",
        "description": "Line-oriented search tool that recursively searches current directory for a regex pattern",
        "category": "terminal",
        "tags": ["grep", "search", "regex", "fast", "cli"],
        "homepage": "https://github.com/BurntSushi/ripgrep",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "ripgrep",
            "arch": "ripgrep",
            "debian": "ripgrep",
            "opensuse": "ripgrep"
        },
        "detection": {
            "commands": ["rg"]
        }
    },
    {
        "id": "fd",
        "name": "fd",
        "description": "Simple, fast, and user-friendly alternative to find",
        "category": "terminal",
        "tags": ["find", "search", "files", "cli"],
        "homepage": "https://github.com/sharkdp/fd",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "fd-find",
            "arch": "fd",
            "debian": "fd-find",
            "opensuse": "fd"
        },
        "detection": {
            "commands": ["fd", "fdfind"]
        }
    },
    {
        "id": "bat",
        "name": "bat",
        "description": "Cat clone with syntax highlighting and Git integration",
        "category": "terminal",
        "tags": ["cat", "syntax", "viewer", "cli"],
        "homepage": "https://github.com/sharkdp/bat",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "bat",
            "arch": "bat",
            "debian": "bat",
            "opensuse": "bat"
        },
        "detection": {
            "commands": ["bat", "batcat"]
        }
    },
    {
        "id": "eza",
        "name": "eza",
        "description": "Modern, maintained replacement for ls with colors, icons, and git status",
        "category": "terminal",
        "tags": ["ls", "files", "icons", "cli"],
        "homepage": "https://github.com/eza-community/eza",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "eza",
            "arch": "eza",
            "debian": "eza",
            "opensuse": "eza"
        },
        "detection": {
            "commands": ["eza"]
        }
    },
    {
        "id": "zoxide",
        "name": "zoxide",
        "description": "Smarter cd command inspired by z and autojump, remembers your favorite dirs",
        "category": "terminal",
        "tags": ["cd", "navigation", "directory", "cli"],
        "homepage": "https://github.com/ajeetdsouza/zoxide",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "zoxide",
            "arch": "zoxide",
            "debian": "zoxide",
            "opensuse": "zoxide"
        },
        "detection": {
            "commands": ["zoxide"]
        }
    },
    {
        "id": "btop",
        "name": "btop",
        "description": "Resource monitor that shows usage and stats for processor, memory, disks, and network",
        "category": "terminal",
        "tags": ["monitor", "htop", "cpu", "memory", "cli"],
        "homepage": "https://github.com/aristocratos/btop",
        "icon": "utilities-system-monitor",
        "source_preference": "native",
        "packages": {
            "fedora": "btop",
            "arch": "btop",
            "debian": "btop",
            "opensuse": "btop"
        },
        "detection": {
            "commands": ["btop"]
        }
    },
    {
        "id": "fastfetch",
        "name": "fastfetch",
        "description": "Like neofetch, but much faster because written mainly in C",
        "category": "terminal",
        "tags": ["neofetch", "sysinfo", "terminal", "cli"],
        "homepage": "https://github.com/fastfetch-cli/fastfetch",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "fastfetch",
            "arch": "fastfetch",
            "debian": "fastfetch",
            "opensuse": "fastfetch"
        },
        "detection": {
            "commands": ["fastfetch"]
        }
    },
    {
        "id": "jq",
        "name": "jq",
        "description": "Lightweight and flexible command-line JSON processor",
        "category": "terminal",
        "tags": ["json", "parser", "cli", "tools"],
        "homepage": "https://jqlang.github.io/jq/",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "jq",
            "arch": "jq",
            "debian": "jq",
            "opensuse": "jq"
        },
        "detection": {
            "commands": ["jq"]
        }
    },
    {
        "id": "tree",
        "name": "tree",
        "description": "Recursive directory listing program that produces a depth indented listing of files",
        "category": "terminal",
        "tags": ["files", "directory", "hierarchy", "cli"],
        "homepage": "http://mama.indstate.edu/users/ice/tree/",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "tree",
            "arch": "tree",
            "debian": "tree",
            "opensuse": "tree"
        },
        "detection": {
            "commands": ["tree"]
        }
    },
    {
        "id": "nerd-fonts",
        "name": "JetBrains Mono Nerd Font",
        "description": "Developer font with developer icons and glyphs patched for high-DPI and terminals",
        "category": "terminal",
        "tags": ["font", "icons", "nerd-fonts", "starship", "kitty"],
        "homepage": "https://www.nerdfonts.com/",
        "icon": "preferences-desktop-font",
        "source_preference": "script",
        "packages": {
            "arch": "ttf-jetbrains-mono-nerd",
            "script": {
                "command": "mkdir -p ~/.local/share/fonts/JetBrainsMonoNerd && curl -fLo /tmp/jb.zip https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.zip && unzip -q -o /tmp/jb.zip -d ~/.local/share/fonts/JetBrainsMonoNerd && rm -f /tmp/jb.zip && fc-cache -f ~/.local/share/fonts",
                "requires_sudo": False
            }
        },
        "detection": {
            "paths": ["~/.local/share/fonts/JetBrainsMonoNerd"]
        }
    },

    # ---- SECURITY ----
    {
        "id": "nmap",
        "name": "Nmap",
        "description": "Free and open source utility for network discovery and security auditing",
        "category": "security",
        "tags": ["security", "network", "scanner", "recon"],
        "homepage": "https://nmap.org/",
        "icon": "network-workgroup",
        "source_preference": "native",
        "packages": {
            "fedora": "nmap",
            "arch": "nmap",
            "debian": "nmap",
            "opensuse": "nmap"
        },
        "detection": {
            "commands": ["nmap"]
        }
    },
    {
        "id": "wireshark",
        "name": "Wireshark",
        "description": "The world’s foremost and widely-used network protocol analyzer",
        "category": "security",
        "tags": ["security", "packet", "pcap", "sniffer", "network"],
        "homepage": "https://www.wireshark.org/",
        "icon": "wireshark",
        "source_preference": "native",
        "packages": {
            "fedora": "wireshark",
            "arch": "wireshark-qt",
            "debian": "wireshark",
            "opensuse": "wireshark"
        },
        "detection": {
            "commands": ["wireshark"]
        },
        "post_install": [
            {"group": "wireshark"}
        ],
        "reboot_recommended": True
    },
    {
        "id": "tcpdump",
        "name": "tcpdump",
        "description": "Powerful command-line packet analyzer for network traffic inspection",
        "category": "security",
        "tags": ["network", "packets", "sniffer", "security", "cli"],
        "homepage": "https://www.tcpdump.org/",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "tcpdump",
            "arch": "tcpdump",
            "debian": "tcpdump",
            "opensuse": "tcpdump"
        },
        "detection": {
            "commands": ["tcpdump"]
        }
    },
    {
        "id": "burpsuite",
        "name": "Burp Suite Community",
        "description": "Leading graphical tool for testing web application security and proxying traffic",
        "category": "security",
        "tags": ["web", "pentest", "proxy", "security", "vulnerability"],
        "homepage": "https://portswigger.net/burp/communitydownload",
        "icon": "burpsuite",
        "source_preference": "flatpak",
        "packages": {
            "arch": {"manager": "yay", "package": "burpsuite"},
            "flatpak": {"id": "net.portswigger.BurpSuiteCommunity"}
        },
        "detection": {
            "commands": ["burpsuite"],
            "flatpak": "net.portswigger.BurpSuiteCommunity"
        }
    },
    {
        "id": "zap",
        "name": "OWASP ZAP",
        "description": "The world’s most widely used web app scanner, free and open source",
        "category": "security",
        "tags": ["security", "owasp", "web", "scanner", "proxy"],
        "homepage": "https://www.zaproxy.org/",
        "icon": "zaproxy",
        "source_preference": "flatpak",
        "packages": {
            "arch": {"manager": "yay", "package": "zaproxy"},
            "flatpak": {"id": "org.zaproxy.ZAP"}
        },
        "detection": {
            "commands": ["zap.sh", "zaproxy"],
            "flatpak": "org.zaproxy.ZAP"
        }
    },
    {
        "id": "ghidra",
        "name": "NSA Ghidra",
        "description": "Software reverse engineering (SRE) suite developed by the NSA",
        "category": "security",
        "tags": ["reversing", "decompiler", "binary", "security", "nsa"],
        "homepage": "https://ghidra-sre.org/",
        "icon": "ghidra",
        "source_preference": "flatpak",
        "packages": {
            "arch": {"manager": "yay", "package": "ghidra"},
            "flatpak": {"id": "org.ghidra_sre.Ghidra"}
        },
        "detection": {
            "commands": ["ghidra"],
            "flatpak": "org.ghidra_sre.Ghidra"
        }
    },
    {
        "id": "jadx",
        "name": "JADX",
        "description": "Dex to Java decompiler and graphical viewer for Android APK files",
        "category": "security",
        "tags": ["android", "apk", "decompiler", "java", "reversing"],
        "homepage": "https://github.com/skylot/jadx",
        "icon": "jadx-gui",
        "source_preference": "native",
        "packages": {
            "arch": {"manager": "yay", "package": "jadx"}
        },
        "detection": {
            "commands": ["jadx", "jadx-gui"]
        }
    },
    {
        "id": "hashcat",
        "name": "Hashcat",
        "description": "World's fastest and most advanced password recovery utility",
        "category": "security",
        "tags": ["password", "cracking", "gpu", "hashes", "security"],
        "homepage": "https://hashcat.net/hashcat/",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "hashcat",
            "arch": "hashcat",
            "debian": "hashcat",
            "opensuse": "hashcat"
        },
        "detection": {
            "commands": ["hashcat"]
        }
    },
    {
        "id": "john",
        "name": "John the Ripper",
        "description": "Fast and customizable password cracker tool for security testing",
        "category": "security",
        "tags": ["password", "cracking", "security", "hashes", "cli"],
        "homepage": "https://www.openwall.com/john/",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "john",
            "arch": "john",
            "debian": "john",
            "opensuse": "john"
        },
        "detection": {
            "commands": ["john"]
        }
    },
    {
        "id": "socat",
        "name": "socat",
        "description": "Multipurpose relay tool establishing two bidirectional byte streams",
        "category": "security",
        "tags": ["network", "relay", "socket", "security", "cli"],
        "homepage": "http://www.dest-unreach.org/socat/",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "socat",
            "arch": "socat",
            "debian": "socat",
            "opensuse": "socat"
        },
        "detection": {
            "commands": ["socat"]
        }
    },
    {
        "id": "whois",
        "name": "whois",
        "description": "Intelligent client for the WHOIS directory service",
        "category": "security",
        "tags": ["whois", "domain", "recon", "network", "cli"],
        "homepage": "https://github.com/rfc1036/whois",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "whois",
            "arch": "whois",
            "debian": "whois",
            "opensuse": "whois"
        },
        "detection": {
            "commands": ["whois"]
        }
    },
    {
        "id": "ncat",
        "name": "ncat",
        "description": "Modern reimplementation of Netcat with SSL, IPv6, and proxy support",
        "category": "security",
        "tags": ["netcat", "sockets", "network", "cli"],
        "homepage": "https://nmap.org/ncat/",
        "icon": "utilities-terminal",
        "source_preference": "native",
        "packages": {
            "fedora": "ncat",
            "arch": "ncat",
            "debian": "netcat-openbsd",
            "opensuse": "netcat-openbsd"
        },
        "detection": {
            "commands": ["ncat", "nc"]
        }
    },

    # ---- STUDENT / ACADEMIC ----
    {
        "id": "obsidian",
        "name": "Obsidian",
        "description": "Powerful and extensible knowledge base and markdown note-taking app",
        "category": "student",
        "tags": ["notes", "markdown", "knowledge", "pkm", "academic"],
        "homepage": "https://obsidian.md/",
        "icon": "obsidian",
        "source_preference": "flatpak",
        "packages": {
            "arch": {"manager": "yay", "package": "obsidian"},
            "flatpak": {"id": "md.obsidian.Obsidian"}
        },
        "detection": {
            "commands": ["obsidian"],
            "flatpak": "md.obsidian.Obsidian"
        }
    },
    {
        "id": "zotero",
        "name": "Zotero",
        "description": "Free, open-source research assistant and citation/bibliography manager",
        "category": "student",
        "tags": ["research", "citations", "bibliography", "academic", "papers"],
        "homepage": "https://www.zotero.org/",
        "icon": "zotero",
        "source_preference": "flatpak",
        "packages": {
            "arch": {"manager": "yay", "package": "zotero-bin"},
            "flatpak": {"id": "org.zotero.Zotero"}
        },
        "detection": {
            "commands": ["zotero"],
            "flatpak": "org.zotero.Zotero"
        }
    },
    {
        "id": "libreoffice",
        "name": "LibreOffice",
        "description": "Free and powerful open-source office suite for word processing, spreadsheets, and presentations",
        "category": "student",
        "tags": ["office", "documents", "writer", "calc", "impress"],
        "homepage": "https://www.libreoffice.org/",
        "icon": "libreoffice-startcenter",
        "source_preference": "native",
        "packages": {
            "fedora": "libreoffice",
            "arch": "libreoffice-fresh",
            "debian": "libreoffice",
            "opensuse": "libreoffice",
            "flatpak": {"id": "org.libreoffice.LibreOffice"}
        },
        "detection": {
            "commands": ["libreoffice"],
            "flatpak": "org.libreoffice.LibreOffice"
        }
    },
    {
        "id": "xournalpp",
        "name": "Xournal++",
        "description": "Handwriting note-taking and PDF annotation software with stylus support",
        "category": "student",
        "tags": ["notes", "handwriting", "pdf", "annotation", "stylus"],
        "homepage": "https://xournalpp.github.io/",
        "icon": "xournalpp",
        "source_preference": "native",
        "packages": {
            "fedora": "xournalpp",
            "arch": "xournalpp",
            "debian": "xournalpp",
            "opensuse": "xournalpp",
            "flatpak": {"id": "com.github.xournalpp.xournalpp"}
        },
        "detection": {
            "commands": ["xournalpp"],
            "flatpak": "com.github.xournalpp.xournalpp"
        }
    },
    {
        "id": "okular",
        "name": "Okular",
        "description": "Universal document viewer supporting PDF, Postscript, DjVu, CHM, XPS, ePub",
        "category": "student",
        "tags": ["pdf", "viewer", "documents", "kde"],
        "homepage": "https://okular.kde.org/",
        "icon": "okular",
        "source_preference": "native",
        "packages": {
            "fedora": "okular",
            "arch": "okular",
            "debian": "okular",
            "opensuse": "okular",
            "flatpak": {"id": "org.kde.okular"}
        },
        "detection": {
            "commands": ["okular"],
            "flatpak": "org.kde.okular"
        }
    },
    {
        "id": "evince",
        "name": "Evince",
        "description": "GNOME document viewer for multiple document formats",
        "category": "student",
        "tags": ["pdf", "viewer", "gnome", "documents"],
        "homepage": "https://wiki.gnome.org/Apps/Evince",
        "icon": "org.gnome.Evince",
        "source_preference": "native",
        "packages": {
            "fedora": "evince",
            "arch": "evince",
            "debian": "evince",
            "opensuse": "evince",
            "flatpak": {"id": "org.gnome.Evince"}
        },
        "detection": {
            "commands": ["evince"],
            "flatpak": "org.gnome.Evince"
        }
    },
    {
        "id": "drawio",
        "name": "Draw.io",
        "description": "Security-first diagramming software for flowcharts, architecture, and diagrams",
        "category": "student",
        "tags": ["diagrams", "flowchart", "architecture", "uml"],
        "homepage": "https://www.drawio.com/",
        "icon": "drawio",
        "source_preference": "flatpak",
        "packages": {
            "arch": {"manager": "yay", "package": "drawio-desktop-bin"},
            "flatpak": {"id": "com.jgraph.drawio.desktop"}
        },
        "detection": {
            "commands": ["drawio"],
            "flatpak": "com.jgraph.drawio.desktop"
        }
    },

    # ---- MEDIA / CREATIVE ----
    {
        "id": "obs-studio",
        "name": "OBS Studio",
        "description": "Free and open source software for video recording and live streaming",
        "category": "media",
        "tags": ["streaming", "recording", "video", "broadcast"],
        "homepage": "https://obsproject.com/",
        "icon": "com.obsproject.Studio",
        "source_preference": "flatpak",
        "packages": {
            "fedora": "obs-studio",
            "arch": "obs-studio",
            "debian": "obs-studio",
            "opensuse": "obs-studio",
            "flatpak": {"id": "com.obsproject.Studio"}
        },
        "detection": {
            "commands": ["obs"],
            "flatpak": "com.obsproject.Studio"
        }
    },
    {
        "id": "vlc",
        "name": "VLC Media Player",
        "description": "Universal open-source multimedia player that plays most multimedia files",
        "category": "media",
        "tags": ["video", "player", "audio", "media"],
        "homepage": "https://www.videolan.org/vlc/",
        "icon": "vlc",
        "source_preference": "native",
        "packages": {
            "fedora": "vlc",
            "arch": "vlc",
            "debian": "vlc",
            "opensuse": "vlc",
            "flatpak": {"id": "org.videolan.VLC"}
        },
        "detection": {
            "commands": ["vlc"],
            "flatpak": "org.videolan.VLC"
        }
    },
    {
        "id": "gimp",
        "name": "GIMP",
        "description": "Cross-platform image editor for photo retouching, image composition, and authoring",
        "category": "media",
        "tags": ["image", "editor", "photo", "graphics", "photoshop-alternative"],
        "homepage": "https://www.gimp.org/",
        "icon": "gimp",
        "source_preference": "native",
        "packages": {
            "fedora": "gimp",
            "arch": "gimp",
            "debian": "gimp",
            "opensuse": "gimp",
            "flatpak": {"id": "org.gimp.GIMP"}
        },
        "detection": {
            "commands": ["gimp"],
            "flatpak": "org.gimp.GIMP"
        }
    },
    {
        "id": "shotcut",
        "name": "Shotcut",
        "description": "Free, open source, cross-platform video editor with broad format support",
        "category": "media",
        "tags": ["video", "editor", "creative", "timeline"],
        "homepage": "https://shotcut.org/",
        "icon": "org.shotcut.Shotcut",
        "source_preference": "flatpak",
        "packages": {
            "arch": "shotcut",
            "flatpak": {"id": "org.shotcut.Shotcut"}
        },
        "detection": {
            "commands": ["shotcut"],
            "flatpak": "org.shotcut.Shotcut"
        }
    },
    {
        "id": "spotify",
        "name": "Spotify",
        "description": "Digital music, podcast, and video service with access to millions of songs",
        "category": "media",
        "tags": ["music", "audio", "streaming", "podcast"],
        "homepage": "https://www.spotify.com/",
        "icon": "spotify-client",
        "source_preference": "flatpak",
        "packages": {
            "arch": {"manager": "yay", "package": "spotify"},
            "flatpak": {"id": "com.spotify.Client"}
        },
        "detection": {
            "commands": ["spotify"],
            "flatpak": "com.spotify.Client"
        }
    },

    # ---- COMMUNICATION ----
    {
        "id": "telegram",
        "name": "Telegram Desktop",
        "description": "Fast, secure, and synchronized messaging application for desktop",
        "category": "communication",
        "tags": ["chat", "messaging", "telegram", "communication"],
        "homepage": "https://desktop.telegram.org/",
        "icon": "telegram",
        "source_preference": "flatpak",
        "packages": {
            "fedora": "telegram-desktop",
            "arch": "telegram-desktop",
            "debian": "telegram-desktop",
            "opensuse": "telegram-desktop",
            "flatpak": {"id": "org.telegram.desktop"}
        },
        "detection": {
            "commands": ["telegram-desktop"],
            "flatpak": "org.telegram.desktop"
        }
    },
    {
        "id": "discord",
        "name": "Discord",
        "description": "Voice, video, and text communication service used by communities and gamers",
        "category": "communication",
        "tags": ["chat", "voice", "community", "gaming"],
        "homepage": "https://discord.com/",
        "icon": "discord",
        "source_preference": "flatpak",
        "packages": {
            "arch": "discord",
            "flatpak": {"id": "com.discordapp.Discord"}
        },
        "detection": {
            "commands": ["discord"],
            "flatpak": "com.discordapp.Discord"
        }
    },

    # ---- UTILITIES ----
    {
        "id": "bitwarden",
        "name": "Bitwarden",
        "description": "Open source password manager for securely storing and autofilling credentials",
        "category": "utilities",
        "tags": ["passwords", "security", "vault", "credentials"],
        "homepage": "https://bitwarden.com/",
        "icon": "bitwarden",
        "source_preference": "flatpak",
        "packages": {
            "arch": {"manager": "yay", "package": "bitwarden-bin"},
            "flatpak": {"id": "com.bitwarden.desktop"}
        },
        "detection": {
            "commands": ["bitwarden"],
            "flatpak": "com.bitwarden.desktop"
        }
    },
    {
        "id": "anydesk",
        "name": "AnyDesk",
        "description": "Fast and smooth remote desktop connectivity software",
        "category": "utilities",
        "tags": ["remote", "desktop", "support", "screen-sharing"],
        "homepage": "https://anydesk.com/",
        "icon": "anydesk",
        "source_preference": "flatpak",
        "packages": {
            "arch": {"manager": "yay", "package": "anydesk-bin"},
            "flatpak": {"id": "com.anydesk.Anydesk"}
        },
        "detection": {
            "commands": ["anydesk"],
            "flatpak": "com.anydesk.Anydesk"
        }
    },
    {
        "id": "flatseal",
        "name": "Flatseal",
        "description": "Graphical utility to review and modify basic permissions from your Flatpak applications",
        "category": "utilities",
        "tags": ["flatpak", "permissions", "sandbox", "security"],
        "homepage": "https://github.com/tchx84/Flatseal",
        "icon": "com.github.tchx84.Flatseal",
        "source_preference": "flatpak",
        "packages": {
            "arch": "flatseal",
            "flatpak": {"id": "com.github.tchx84.Flatseal"}
        },
        "detection": {
            "commands": ["flatseal"],
            "flatpak": "com.github.tchx84.Flatseal"
        }
    },
    {
        "id": "qbittorrent",
        "name": "qBittorrent",
        "description": "Free and reliable P2P BitTorrent client written in C++ / Qt",
        "category": "utilities",
        "tags": ["torrent", "p2p", "download", "bittorrent"],
        "homepage": "https://www.qbittorrent.org/",
        "icon": "qbittorrent",
        "source_preference": "native",
        "packages": {
            "fedora": "qbittorrent",
            "arch": "qbittorrent",
            "debian": "qbittorrent",
            "opensuse": "qbittorrent",
            "flatpak": {"id": "org.qbittorrent.qBittorrent"}
        },
        "detection": {
            "commands": ["qbittorrent"],
            "flatpak": "org.qbittorrent.qBittorrent"
        }
    }
]

def main():
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for app in APPS:
        cat = app["category"]
        cat_dir = CATALOG_DIR / cat
        cat_dir.mkdir(parents=True, exist_ok=True)

        app_file = cat_dir / f"{app['id']}.yaml"
        with open(app_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(app, f, sort_keys=False)
        count += 1

    print(f"Successfully generated {count} catalog entries across {len(set(a['category'] for a in APPS))} categories in {CATALOG_DIR}")

if __name__ == "__main__":
    main()
