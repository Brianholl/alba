#!/bin/bash
# Instalador - Taller de Informática
# Uso: bash install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/taller"
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

step() { echo -e "\n${CYAN}[$1/4]${NC} $2"; }
ok()   { echo -e " ${GREEN}✓${NC} $1"; }

echo ""
echo "╔══════════════════════════════════════╗"
echo "║    Instalador Taller de Informática  ║"
echo "╚══════════════════════════════════════╝"

# ── 1. Juegos ─────────────────────────────────────────────────────────────────
step 1 "Instalando juegos y dependencias..."
sudo apt-get update -qq
sudo apt-get install -y \
    tuxpaint gcompris-qt frozen-bubble \
    tuxtype tuxmath kturtle \
    python3-pil.imagetk \
    pulseaudio-utils sound-theme-freedesktop
ok "Juegos instalados"

# ── 2. Archivos del taller ────────────────────────────────────────────────────
step 2 "Copiando archivos a $INSTALL_DIR..."
if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
    cp "$SCRIPT_DIR/launcher.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/asoundrc"    "$INSTALL_DIR/"
fi
chmod +x "$INSTALL_DIR/launcher.py"
ok "Archivos listos en $INSTALL_DIR"

# ── 3. Audio (HDMI por defecto) ───────────────────────────────────────────────
step 3 "Configurando audio HDMI..."
cp "$SCRIPT_DIR/asoundrc" "$HOME/.asoundrc"
# Subir volumen del jack a -5 dB por si se usa salida analógica
amixer -c 1 cset numid=1 -- -500 &>/dev/null || true
ok "Audio configurado (HDMI por defecto, jack a -5 dB)"

# ── 4. Acceso directo y autoarranque ─────────────────────────────────────────
step 4 "Configurando acceso directo y autoarranque..."
DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
mkdir -p "$HOME/.config/autostart" "$DESKTOP_DIR"

cat > "$DESKTOP_DIR/Taller.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Taller de Informática
Comment=Lanzador de juegos educativos
Exec=python3 $INSTALL_DIR/launcher.py
Icon=applications-games
Terminal=false
Categories=Education;Game;
StartupNotify=false
EOF

chmod +x "$DESKTOP_DIR/Taller.desktop"
gio set "$DESKTOP_DIR/Taller.desktop" metadata::trusted true 2>/dev/null || true

cat > "$HOME/.config/autostart/taller.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Taller de Informática
Exec=python3 $INSTALL_DIR/launcher.py
Hidden=false
X-GNOME-Autostart-enabled=true
EOF

# LXDE (Raspberry Pi OS): también agregar al autostart de lxsession
LXDE_AUTOSTART="$HOME/.config/lxsession/LXDE-pi/autostart"
mkdir -p "$(dirname "$LXDE_AUTOSTART")"
if ! grep -qF "launcher.py" "$LXDE_AUTOSTART" 2>/dev/null; then
    echo "@python3 $INSTALL_DIR/launcher.py" >> "$LXDE_AUTOSTART"
fi

ok "Acceso directo en el escritorio ($DESKTOP_DIR)"
ok "Autoarranque al iniciar sesión (XDG + LXDE)"

# ── Resumen ───────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════╗"
echo "║        Instalación completada        ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "  Lanzador : $INSTALL_DIR/launcher.py"
echo "  Audio    : $HOME/.asoundrc  (HDMI)"
echo "  Escritorio: $DESKTOP_DIR/Taller.desktop"
echo "  Autoarranque activado al iniciar sesión"
echo ""
echo "  Reinicia la sesión para que el lanzador"
echo "  arranque automáticamente."
echo ""
