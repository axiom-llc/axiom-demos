# !/usr/bin/env bash
# Recursively concatenate non-hidden files with file boundary markers.

find . -type f \
  ! -path '*/.*' \
  ! -name 'combined.txt' \
  -print0 | sort -z | xargs -0 -I{} sh -c 'printf "\n===== BEGIN FILE: %s =====\n" "{}"; cat "{}"; printf "\n===== END FILE: %s =====\n" "{}"' > combined.txt
