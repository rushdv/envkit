#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_distro

log "[5/7] Installing Security Researcher & Pentesting Tools"

# --- Core network reconnaissance & packet analysis ---
info "Installing network analysis & reconnaissance tools..."
pkg_install nmap nmap nmap nmap
pkg_install wireshark wireshark wireshark wireshark
pkg_install tcpdump tcpdump tcpdump tcpdump
pkg_install socat socat socat socat
pkg_install whois whois whois whois
pkg_install mtr mtr mtr mtr
pkg_install ncat ncat netcat-openbsd netcat-openbsd || true

# Add current user to wireshark group to allow non-root packet capture
if getent group wireshark >/dev/null; then
  sudo usermod -aG wireshark "$USER" 2>/dev/null || true
  ok "User added to wireshark group"
fi

# --- Web & Binary Security Tools (Flatpak / AUR) ---
ensure_flatpak

SECURITY_FLATPAKS=(
  org.zaproxy.ZAP                          # OWASP ZAP Web Application Security Scanner
  net.portswigger.BurpSuiteCommunity       # Burp Suite Community Edition
  org.ghidra_sre.Ghidra                    # NSA Ghidra Software Reverse Engineering Suite
)

for app in "${SECURITY_FLATPAKS[@]}"; do
  info "Installing $app via Flatpak..."
  flatpak install -y flathub "$app" || warn "Could not install $app via Flatpak — skipping"
done

# Arch / AUR pentest utilities if on Arch
if [[ "$PKG_MANAGER" == "pacman" ]] && command -v yay &>/dev/null; then
  info "Installing additional Arch/AUR security utilities..."
  yay -S --noconfirm --needed jadx metasploit hashcat john || warn "Some AUR security packages failed to install"
else
  info "Installing password & hash auditing utilities..."
  pkg_install hashcat hashcat hashcat hashcat || true
  pkg_install john john john john || true
fi

# --- Virtualization (for Kali / isolated lab VMs) ---
echo
echo "Virtualization setup for running Kali Linux or security lab VMs:"
echo "  [1] QEMU / KVM / virt-manager (Recommended for Linux: native, fastest performance)"
echo "  [2] VirtualBox"
echo "  [3] Skip virtualization"
read -rp "Select option [1/2/3, default 1]: " virt_choice
virt_choice="${virt_choice:-1}"

case "$virt_choice" in
  1)
    log "Installing QEMU / KVM / virt-manager"
    case "$PKG_MANAGER" in
      dnf)
        sudo dnf install -y @virtualization virt-manager
        ;;
      pacman)
        sudo pacman -S --noconfirm --needed qemu-full virt-manager dnsmasq iptables-nft
        ;;
      apt)
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y qemu-system libvirt-daemon-system libvirt-clients virt-manager
        ;;
      zypper)
        sudo zypper --non-interactive install -y qemu-kvm libvirt virt-manager
        ;;
    esac
    sudo systemctl enable --now libvirtd 2>/dev/null || true
    sudo usermod -aG libvirt "$USER" 2>/dev/null || sudo usermod -aG kvm "$USER" 2>/dev/null || true
    ok "KVM / virt-manager installed (log out/in for group to apply)"
    ;;
  2)
    log "Installing VirtualBox"
    case "$PKG_MANAGER" in
      dnf)
        sudo dnf install -y @virtualization VirtualBox akmod-VirtualBox || true
        ;;
      pacman)
        sudo pacman -S --noconfirm --needed virtualbox virtualbox-host-dkms || \
        sudo pacman -S --noconfirm --needed virtualbox virtualbox-host-modules-arch || true
        sudo modprobe vboxdrv 2>/dev/null || true
        ;;
      apt)
        # Pre-seed debconf to prevent virtualbox-ext-pack PUEL interactive hang
        echo "virtualbox-ext-pack virtualbox-ext-pack/license_accepted select true" | sudo debconf-set-selections 2>/dev/null || true
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y virtualbox virtualbox-ext-pack || \
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y virtualbox
        ;;
      zypper)
        sudo zypper --non-interactive install -y virtualbox
        ;;
    esac
    sudo usermod -aG vboxusers "$USER" 2>/dev/null || true
    ok "VirtualBox installed"
    ;;
  *)
    info "Skipping virtualization."
    ;;
esac

ok "Security researcher & pentesting toolkit ready"
