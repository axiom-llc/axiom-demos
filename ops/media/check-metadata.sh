#!/usr/bin/env bash
# check-metadata.sh — verify video files have no residual metadata
SKIP='^(File Name|Directory|File Size|File Modification|File Access|File Inode|File Permissions|File Type|MIME Type|Major Brand|Minor Version|Compatible Brands|Media Duration|Track Duration)'
for f in *.{mp4,m4v,webm,asf}; do
  [[ -e "$f" ]] || continue
  n=$(exiftool "$f" 2>/dev/null | grep -vE "$SKIP" | wc -l)
  (( n == 0 )) && echo "✓ $f: Clean" || { echo "✗ $f: $n fields"; exiftool "$f" | grep -vE "$SKIP"; }
done
