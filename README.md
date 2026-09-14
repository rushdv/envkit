# linux-setup

A modular, cross-distro post-install script. Run it once on a fresh
Fedora / Arch-based (CachyOS, EndeavourOS, Manjaro) / Debian-Ubuntu
install and get your full development + terminal + security + apps
environment back, instead of installing everything by hand.

## Quick start

```bash
git clone https://github.com/rushdv/linux-setup.git
cd linux-setup
chmod +x setup.sh
./setup.sh
```

You'll get an interactive menu to pick which modules to run:

```
=================================
      Linux Setup Assistant
=================================

  [1] system   — System update + repo setup
  [2] dev      — Development tools
  [3] terminal — Terminal environment
  [4] security — Security tools
  [5] apps     — Daily-use apps via Flatpak
  [6] config   — Final config (git identity, SSH key)

Your choice: (Enter = all)
```

## Structure

```
linux-setup/
├── setup.sh              # entry point — distro detection + interactive menu
├── lib/
│   └── common.sh         # logging, distro detection, pkg_install() abstraction
├── distro/
│   ├── fedora.sh          # RPM Fusion
│   ├── arch.sh            # yay (AUR helper)
│   └── debian.sh          # apt prerequisites
├── scripts/
│   ├── 01-system.sh
│   ├── 02-dev.sh
│   ├── 03-terminal.sh
│   ├── 04-security.sh
│   ├── 05-apps.sh
│   └── 06-config.sh
├── config/                # dotfiles, symlinked into $HOME (won't overwrite existing files)
│   ├── zshrc
│   ├── starship.toml
│   ├── kitty.conf
│   └── gitconfig
└── extensions/
    └── vscode-extensions.txt
```

## How cross-distro support works

`lib/common.sh` detects the distro and exposes one function,
`pkg_install <fedora-pkg> <arch-pkg> <debian-pkg>`, so every script in
`scripts/` stays distro-agnostic. Example:

```bash
pkg_install postgresql postgresql postgresql
pkg_install postgresql-server "-" postgresql-contrib   # "-" = skip on that distro
```

Adding a new distro means adding one `case` branch in
`lib/common.sh::detect_distro()` and one file in `distro/`.

## Notes

- **Metasploit / Burp Suite / Ghidra / JADX**: no official Fedora or
  Debian packages. On Arch-based systems the script installs them via
  AUR (`yay`); elsewhere it's a manual step — or just run them inside
  your existing Kali VM, which is what `04-security.sh` recommends.
- **Dotfiles are symlinked, not copied** — edit the files in `config/`
  and the changes apply immediately to your shell.
- Safe to re-run: package installs are idempotent, and dotfile
  symlinking skips files that already exist.

## Customizing for yourself

Fork this repo and edit:
- `extensions/vscode-extensions.txt` — your own extension list
- `config/*` — your own dotfiles
- `scripts/05-apps.sh` — your own Flatpak app list
- `scripts/02-dev.sh` — add/remove languages and tools you use

## License

MIT — use, fork, and adapt freely.
