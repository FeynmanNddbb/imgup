#!/bin/bash
# imgup - Linux/macOS client installer

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_CLIENT="$SCRIPT_DIR/upload.sh"
TARGET_CLIENT="/usr/local/bin/imgup"
CONFIG_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/imgup/imgup_config.json"
VERSION="1.0"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

trim() {
    local value="$1"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    printf '%s' "$value"
}

normalize_url() {
    local url
    url="$(trim "$1")"
    url="${url#https://}"
    url="${url#http://}"
    url="${url#www.}"
    url="${url%/}"

    if [ -z "$url" ]; then
        return 1
    fi

    if [[ "$url" != */upload ]]; then
        url="$url/upload"
    fi

    printf 'https://%s' "$url"
}

json_escape() {
    printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

read_token() {
    local value
    if [ -t 0 ]; then
        printf "Upload token: "
        stty -echo
        IFS= read -r value
        stty echo
        printf '\n'
    else
        IFS= read -r value
    fi
    printf '%s' "$value"
}

install_client() {
    if [ ! -f "$SOURCE_CLIENT" ]; then
        echo -e "${RED}Cannot find upload.sh next to install-client.sh.${NC}" >&2
        exit 1
    fi

    if [ -w "$(dirname "$TARGET_CLIENT")" ]; then
        install -m 755 "$SOURCE_CLIENT" "$TARGET_CLIENT"
    elif command -v sudo >/dev/null 2>&1; then
        sudo install -m 755 "$SOURCE_CLIENT" "$TARGET_CLIENT"
    else
        echo -e "${RED}Need permission to write $TARGET_CLIENT, but sudo is not available.${NC}" >&2
        exit 1
    fi
}

write_config() {
    local url="$1"
    local token="$2"

    mkdir -p "$(dirname "$CONFIG_FILE")"
    cat > "$CONFIG_FILE" <<EOF
{
  "url": "$(json_escape "$url")",
  "token": "$(json_escape "$token")",
  "version": "$VERSION"
}
EOF
    chmod 600 "$CONFIG_FILE" 2>/dev/null || true
}

echo -e "${BOLD}imgup Linux/macOS client installer${NC}"
echo ""
echo "This installs the global command: $TARGET_CLIENT"
echo "This writes client config to: $CONFIG_FILE"
echo ""

printf "Image host domain, for example images.example.com: "
IFS= read -r input_url
upload_url="$(normalize_url "$input_url")" || {
    echo -e "${RED}Image host domain is required.${NC}" >&2
    exit 1
}

input_token="$(read_token)"
input_token="$(trim "$input_token")"
if [ -z "$input_token" ]; then
    echo -e "${RED}Upload token is required.${NC}" >&2
    exit 1
fi

install_client
write_config "$upload_url" "$input_token"

echo ""
echo -e "${GREEN}imgup client installed.${NC}"
echo -e "${CYAN}Command:${NC} imgup photo.jpg"
echo -e "${CYAN}URL:${NC} $upload_url"
