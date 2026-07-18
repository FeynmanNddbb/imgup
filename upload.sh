#!/bin/bash
# imgup - Client upload script
# Usage: ./upload.sh <file1> [file2] ...

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_URL="https://images.example.com/upload"
DEFAULT_TOKEN="change_me_please"

normalize_url() {
    local url="$1"
    url="${url#"${url%%[![:space:]]*}"}"
    url="${url%"${url##*[![:space:]]}"}"
    url="${url#https://}"
    url="${url#http://}"
    url="${url#www.}"
    url="${url%/}"

    if [[ "$url" != */upload ]]; then
        url="$url/upload"
    fi

    printf 'https://%s' "$url"
}

json_value() {
    local key="$1"
    local file="$2"
    sed -n "s/^[[:space:]]*\"$key\"[[:space:]]*:[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p" "$file" | head -n 1
}

find_config_file() {
    local xdg_config="${XDG_CONFIG_HOME:-$HOME/.config}/imgup/imgup_config.json"
    if [ -n "$IMGUP_CONFIG" ]; then
        printf '%s' "$IMGUP_CONFIG"
    elif [ -f "$SCRIPT_DIR/imgup_config.json" ]; then
        printf '%s' "$SCRIPT_DIR/imgup_config.json"
    elif [ -f "$xdg_config" ]; then
        printf '%s' "$xdg_config"
    else
        printf '%s' "$SCRIPT_DIR/imgup_config.json"
    fi
}

CONFIG_FILE="$(find_config_file)"
CONFIG_URL=""
CONFIG_TOKEN=""
if [ -f "$CONFIG_FILE" ]; then
    CONFIG_URL="$(json_value url "$CONFIG_FILE")"
    CONFIG_TOKEN="$(json_value token "$CONFIG_FILE")"
fi

UPLOAD_URL="${IMGUP_URL:-${CONFIG_URL:-$DEFAULT_URL}}"
TOKEN="${IMGUP_TOKEN:-${CONFIG_TOKEN:-$DEFAULT_TOKEN}}"
UPLOAD_URL="$(normalize_url "$UPLOAD_URL")"

usage() {
    echo -e "${BOLD}imgup${NC} - quick image uploader"
    echo ""
    echo -e "  ${CYAN}Usage:${NC}   $0 <image> [image2] ..."
    echo -e "  ${CYAN}Config:${NC}  $CONFIG_FILE"
    echo -e "  ${CYAN}Setup:${NC}   ./configure.sh"
    echo -e "  ${CYAN}Env:${NC}     IMGUP_URL / IMGUP_TOKEN override config"
    echo ""
    echo -e "  ${CYAN}Example:${NC} $0 screenshot.png photo.jpg"
    exit 0
}

copy_to_clipboard() {
    local text="$1"
    if command -v xclip >/dev/null 2>&1; then
        echo -n "$text" | xclip -selection clipboard && echo -e "   ${CYAN}Copied to clipboard${NC}"
    elif command -v xsel >/dev/null 2>&1; then
        echo -n "$text" | xsel --clipboard --input && echo -e "   ${CYAN}Copied to clipboard${NC}"
    elif command -v pbcopy >/dev/null 2>&1; then
        echo -n "$text" | pbcopy && echo -e "   ${CYAN}Copied to clipboard${NC}"
    fi
}

[ $# -eq 0 ] && usage

if [ "$TOKEN" = "$DEFAULT_TOKEN" ]; then
    echo -e "${RED}imgup is not configured.${NC}"
    echo -e "Run ${CYAN}./configure.sh${NC} or set ${CYAN}IMGUP_URL${NC} and ${CYAN}IMGUP_TOKEN${NC}."
    exit 1
fi

success_count=0
fail_count=0
all_urls=()

for file in "$@"; do
    echo -e "${BOLD}Uploading:${NC} $file"

    if [ ! -f "$file" ]; then
        echo -e "   ${RED}File not found${NC}"
        ((fail_count++))
        continue
    fi

    response=$(curl -s -w "\n%{http_code}" -X POST "$UPLOAD_URL" \
        -H "X-Upload-Token: $TOKEN" \
        -F "file=@$file")

    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        url=$(echo "$body" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
        size=$(echo "$body" | grep -o '"size":[0-9]*' | cut -d':' -f2)
        size_kb=$(( ${size:-0} / 1024 ))
        echo -e "   ${GREEN}OK${NC} $url ${YELLOW}(${size_kb} KB)${NC}"
        all_urls+=("$url")
        ((success_count++))
    else
        error=$(echo "$body" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
        echo -e "   ${RED}Failed [HTTP $http_code]: ${error:-unknown error}${NC}"
        ((fail_count++))
    fi
    echo
done

echo -e "${BOLD}------------------------------${NC}"
echo -e "  ${GREEN}Success: $success_count${NC}  ${RED}Failed: $fail_count${NC}"

if [ ${#all_urls[@]} -eq 1 ]; then
    copy_to_clipboard "${all_urls[0]}"
elif [ ${#all_urls[@]} -gt 1 ]; then
    echo -e "\n${BOLD}All URLs:${NC}"
    for url in "${all_urls[@]}"; do
        echo "  $url"
    done
    joined=$(printf '%s\n' "${all_urls[@]}")
    copy_to_clipboard "$joined"
fi
