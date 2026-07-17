#!/bin/bash
# imgup - Client upload script
# Usage: ./upload.sh <file1> [file2] ...

# ─── Config ───────────────────────────────────────────────────────────────────
UPLOAD_URL="${IMGUP_URL:-https://images.example.com/upload}"
TOKEN="${IMGUP_TOKEN:-change_me_please}"
# ──────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

usage() {
    echo -e "${BOLD}imgup${NC} — quick image uploader"
    echo ""
    echo -e "  ${CYAN}Usage:${NC}   $0 <image> [image2] ..."
    echo -e "  ${CYAN}Env:${NC}     IMGUP_URL   upload endpoint  (default: $UPLOAD_URL)"
    echo -e "           IMGUP_TOKEN token for auth    (default: set in script)"
    echo ""
    echo -e "  ${CYAN}Example:${NC} $0 screenshot.png photo.jpg"
    exit 0
}

copy_to_clipboard() {
    local text="$1"
    if command -v xclip &>/dev/null; then
        echo -n "$text" | xclip -selection clipboard && echo -e "   ${CYAN}📋 Copied to clipboard${NC}"
    elif command -v xsel &>/dev/null; then
        echo -n "$text" | xsel --clipboard --input && echo -e "   ${CYAN}📋 Copied to clipboard${NC}"
    elif command -v pbcopy &>/dev/null; then
        echo -n "$text" | pbcopy && echo -e "   ${CYAN}📋 Copied to clipboard${NC}"
    fi
}

[ $# -eq 0 ] && usage

success_count=0
fail_count=0
all_urls=()

for file in "$@"; do
    echo -e "${BOLD}📤 Uploading:${NC} $file"

    if [ ! -f "$file" ]; then
        echo -e "   ${RED}✗ File not found${NC}"
        ((fail_count++))
        continue
    fi

    response=$(curl -s -w "\n%{http_code}" -X POST "$UPLOAD_URL" \
        -H "X-Upload-Token: $TOKEN" \
        -F "file=@$file")

    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        url=$(echo "$body" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
        size=$(echo "$body" | grep -o '"size":[0-9]*' | cut -d':' -f2)
        size_kb=$(( ${size:-0} / 1024 ))
        echo -e "   ${GREEN}✓ ${url}${NC}  ${YELLOW}(${size_kb} KB)${NC}"
        all_urls+=("$url")
        ((success_count++))
    else
        error=$(echo "$body" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
        echo -e "   ${RED}✗ Failed [HTTP $http_code]: ${error:-unknown error}${NC}"
        ((fail_count++))
    fi
    echo
done

# Summary
echo -e "${BOLD}──────────────────────────────${NC}"
echo -e "  ${GREEN}✓ Success: $success_count${NC}  ${RED}✗ Failed: $fail_count${NC}"

if [ ${#all_urls[@]} -eq 1 ]; then
    copy_to_clipboard "${all_urls[0]}"
elif [ ${#all_urls[@]} -gt 1 ]; then
    echo -e "\n${BOLD}All URLs:${NC}"
    for u in "${all_urls[@]}"; do
        echo "  $u"
    done
    joined=$(printf '%s\n' "${all_urls[@]}")
    copy_to_clipboard "$joined"
fi
