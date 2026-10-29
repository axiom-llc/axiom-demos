#!/usr/bin/env bash
set -euo pipefail
# Recursively concatenate non-hidden files with file boundary markers.
find . -type f \
  ! -path '*/.*' \
  ! -name 'combined.txt' \
  -print0 | sort -z | while IFS= read -r -d '' file; do
    printf '\n===== BEGIN FILE: %s =====\n' "$file"
    cat -- "$file"
    printf '\n===== END FILE: %s =====\n' "$file"
  done > combined.txt
