#!/bin/bash
# imgup - Linux/macOS client configuration script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_URL="https://images.example.com/upload"
DEFAULT_TOKEN="change_me_please"
VERSION="1.0"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

usage() {
    cat <<EOF
imgup client configuration

Usage:
  ./configure.sh [--config PATH] [--show]

Options:
  --config PATH  Write a specific config file
  --show         Print current config and exit
  -h, --help     Show this help
EOF
}

default_config_file() {
    local local_config="$SCRIPT_DIR/imgup_config.json"
    local user_config="${XDG_CONFIG_HOME:-$HOME/.config}/imgup/imgup_config.json"

    if [ -w "$SCRIPT_DIR" ]; then
        printf '%s' "$local_config"
    else
        printf '%s' "$user_config"
    fi
}

json_value() {
    local key="$1"
    local file="$2"
    sed -n "s/^[[:space:]]*\"$key\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p" "$file" | head -n 1
}

json_escape() {
    printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

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

read_token() {
    local prompt="$1"
    local value
    if [ -t 0 ]; then
        printf '%b' "$prompt"
        stty -echo
        IFS= read -r value
        stty echo
        printf '\n'
    else
        IFS= read -r value
    fi
    printf '%s' "$value"
}

mask_token() {
    local token="$1"
    if [ "$token" = "$DEFAULT_TOKEN" ] || [ -z "$token" ]; then
        printf '<not configured>'
    elif [ "${#token}" -le 10 ]; then
        printf '******'
    else
        printf '%s...%s' "${token:0:6}" "${token: -4}"
    fi
}

CONFIG_FILE=""
SHOW_ONLY=0

while [ $# -gt 0 ]; do
    case "$1" in
        --config)
            [ $# -ge 2 ] || { echo "Missing value for --config" >&2; exit 2; }
            CONFIG_FILE="$2"
            shift 2
            ;;
        --show)
            SHOW_ONLY=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

CONFIG_FILE="${CONFIG_FILE:-${IMGUP_CONFIG:-$(default_config_file)}}"

CURRENT_URL=""
CURRENT_TOKEN=""
if [ -f "$CONFIG_FILE" ]; then
    CURRENT_URL="$(json_value url "$CONFIG_FILE")"
    CURRENT_TOKEN="$(json_value token "$CONFIG_FILE")"
fi

CURRENT_URL="${IMGUP_URL:-${CURRENT_URL:-$DEFAULT_URL}}"
CURRENT_TOKEN="${IMGUP_TOKEN:-${CURRENT_TOKEN:-$DEFAULT_TOKEN}}"

if [ "$SHOW_ONLY" -eq 1 ]; then
    echo "Config : $CONFIG_FILE"
    echo "URL    : $(normalize_url "$CURRENT_URL")"
    echo "Token  : $(mask_token "$CURRENT_TOKEN")"
    exit 0
fi

echo -e "${BOLD}imgup Linux/macOS client setup${NC}"
echo ""
echo -e "${CYAN}Config file:${NC} $CONFIG_FILE"
echo ""

printf "Image host domain or upload endpoint [%s]: " "$(normalize_url "$CURRENT_URL")"
IFS= read -r input_url
input_url="$(trim "$input_url")"
if [ -z "$input_url" ]; then
    input_url="$CURRENT_URL"
fi

upload_url="$(normalize_url "$input_url")" || {
    echo -e "${RED}Invalid image host domain or upload endpoint.${NC}" >&2
    exit 1
}

if [ "$CURRENT_TOKEN" = "$DEFAULT_TOKEN" ]; then
    token_prompt="Upload token: "
else
    token_prompt="Upload token [leave blank to keep current]: "
fi

input_token="$(read_token "$token_prompt")"
input_token="$(trim "$input_token")"
if [ -z "$input_token" ]; then
    input_token="$CURRENT_TOKEN"
fi

if [ -z "$input_token" ] || [ "$input_token" = "$DEFAULT_TOKEN" ]; then
    echo -e "${RED}Upload token is required.${NC}" >&2
    exit 1
fi

mkdir -p "$(dirname "$CONFIG_FILE")"
cat > "$CONFIG_FILE" <<EOF
{
  "url": "$(json_escape "$upload_url")",
  "token": "$(json_escape "$input_token")",
  "version": "$VERSION"
}
EOF
chmod 600 "$CONFIG_FILE" 2>/dev/null || true

echo ""
echo -e "${GREEN}Configuration saved.${NC}"
echo -e "${CYAN}URL:${NC} $upload_url"
echo -e "${CYAN}Try:${NC} ./upload.sh photo.jpg"
