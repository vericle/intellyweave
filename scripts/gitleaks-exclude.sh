#!/usr/bin/env bash
# ============================================================
# Gitleaks Auto-Exclude Script
# ============================================================
# This script parses gitleaks findings and adds files containing
# detected secrets to .git/info/exclude to prevent future commits.
#
# Usage: Called automatically by pre-commit after gitleaks runs
# Report: Reads from temp/gitleaks-report.json
# Output: Appends to .git/info/exclude
#
# This script is idempotent - safe to run multiple times.
# ============================================================

set -euo pipefail

# Configuration
REPORT_FILE="temp/gitleaks-report.json"
EXCLUDE_FILE=".git/info/exclude"
MARKER="# Auto-added by gitleaks-exclude.sh"

# Colors for output (disabled in CI)
if [[ -t 1 ]] && [[ -z "${CI:-}" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    NC=''
fi

# Check if report exists and has findings
if [[ ! -f "$REPORT_FILE" ]]; then
    # No report means gitleaks didn't find anything or didn't run
    exit 0
fi

# Check if report is empty or contains empty array
if [[ ! -s "$REPORT_FILE" ]] || [[ "$(cat "$REPORT_FILE")" == "[]" ]]; then
    exit 0
fi

# Ensure .git/info directory exists
mkdir -p "$(dirname "$EXCLUDE_FILE")"

# Ensure exclude file exists
touch "$EXCLUDE_FILE"

# Extract unique file paths from the report
# Uses jq if available, falls back to grep/sed
if command -v jq &> /dev/null; then
    FILES=$(jq -r '.[].File' "$REPORT_FILE" 2>/dev/null | sort -u)
else
    # Fallback: basic parsing without jq
    FILES=$(grep -oP '"File":\s*"\K[^"]+' "$REPORT_FILE" 2>/dev/null | sort -u)
fi

# Exit if no files found
if [[ -z "$FILES" ]]; then
    exit 0
fi

# Track if we added anything
ADDED_COUNT=0

# Add marker comment if not present
if ! grep -qF "$MARKER" "$EXCLUDE_FILE" 2>/dev/null; then
    echo "" >> "$EXCLUDE_FILE"
    echo "$MARKER" >> "$EXCLUDE_FILE"
fi

# Add each file to exclude if not already present
while IFS= read -r file; do
    [[ -z "$file" ]] && continue

    # Check if already in exclude file
    if ! grep -qxF "$file" "$EXCLUDE_FILE" 2>/dev/null; then
        echo "$file" >> "$EXCLUDE_FILE"
        echo -e "${YELLOW}[gitleaks-exclude]${NC} Added to .git/info/exclude: ${RED}$file${NC}"
        ADDED_COUNT=$((ADDED_COUNT + 1))
    fi
done <<< "$FILES"

# Summary
if [[ $ADDED_COUNT -gt 0 ]]; then
    echo -e "${GREEN}[gitleaks-exclude]${NC} Added $ADDED_COUNT file(s) to .git/info/exclude"
    echo -e "${YELLOW}[gitleaks-exclude]${NC} These files will be ignored in future commits"
    echo -e "${YELLOW}[gitleaks-exclude]${NC} To commit them anyway, use: git add -f <file>"
fi

exit 0
