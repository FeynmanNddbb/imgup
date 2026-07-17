#!/bin/bash
# imgup one-click installer
# Run: curl -fsSL https://raw.githubusercontent.com/yourusername/imgup/main/install.sh | bash

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

INSTALL_DIR="/opt/imgup"
SERVICE_FILE="/etc/systemd/system/imgup.service"

echo -e "${BOLD}"
echo "  ██╗███╗   ███╗ ██████╗ ██╗   ██╗██████╗ "
echo "  ██║████╗ ████║██╔════╝ ██║   ██║██╔══██╗"
echo "  ██║██╔████╔██║██║  ███╗██║   ██║██████╔╝"
echo "  ██║██║╚██╔╝██║██║   ██║██║   ██║██╔═══╝ "
echo "  ██║██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██║     "
echo "  ╚═╝╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═╝     "
echo -e "${NC}"
echo -e "${CYAN}Lightweight image upload server${NC}"
echo ""

# ─── Gather config ─────────────────────────────────────────────────────────
read -rp "Upload directory       [/data/images]: " UPLOAD_DIR
UPLOAD_DIR="${UPLOAD_DIR:-/data/images}"

read -rp "Base URL  [https://images.example.com]: " BASE_URL
BASE_URL="${BASE_URL:-https://images.example.com}"

read -rp "Port                           [8765]: " PORT
PORT="${PORT:-8765}"

TOKEN=$(openssl rand -hex 16 2>/dev/null || cat /dev/urandom | tr -dc 'a-f0-9' | head -c 32)
echo -e "Upload token ${YELLOW}(auto-generated)${NC}: ${BOLD}$TOKEN${NC}"
echo ""

# ─── Install ────────────────────────────────────────────────────────────────
echo -e "${CYAN}[1/4]${NC} Creating directories..."
mkdir -p "$INSTALL_DIR" "$UPLOAD_DIR"

echo -e "${CYAN}[2/4]${NC} Copying server.py..."
cp "$(dirname "$0")/server.py" "$INSTALL_DIR/server.py"
chmod +x "$INSTALL_DIR/server.py"

echo -e "${CYAN}[3/4]${NC} Installing systemd service..."
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=imgup - Lightweight Image Upload Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment=UPLOAD_DIR=$UPLOAD_DIR
Environment=UPLOAD_TOKEN=$TOKEN
Environment=BASE_URL=$BASE_URL
Environment=PORT=$PORT
Environment=MAX_SIZE_MB=20
ExecStart=/usr/bin/python3 $INSTALL_DIR/server.py
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now imgup.service

echo -e "${CYAN}[4/4]${NC} Configuring upload client..."
CLIENT="$INSTALL_DIR/upload.sh"
cp "$(dirname "$0")/upload.sh" "$CLIENT"
sed -i "s|change_me_please|$TOKEN|g" "$CLIENT"
sed -i "s|https://images.lovecode.xin|$BASE_URL|g" "$CLIENT"
chmod +x "$CLIENT"
ln -sf "$CLIENT" /usr/local/bin/imgup

echo ""
echo -e "${GREEN}${BOLD}✓ imgup installed successfully!${NC}"
echo ""
echo -e "  ${BOLD}Token  :${NC} $TOKEN"
echo -e "  ${BOLD}Port   :${NC} $PORT"
echo -e "  ${BOLD}Dir    :${NC} $UPLOAD_DIR"
echo ""
echo -e "  ${CYAN}Upload a file:${NC}  imgup photo.jpg"
echo -e "  ${CYAN}Service status:${NC} systemctl status imgup"
echo ""
echo -e "${YELLOW}⚠  Add this Caddy block to your Caddyfile:${NC}"
echo ""
echo "  $BASE_URL {"
echo "    handle /upload { reverse_proxy 127.0.0.1:$PORT }"
echo "    handle { root * $UPLOAD_DIR; file_server browse }"
echo "  }"
echo ""
