#!/usr/bin/env bash
shopt -s nullglob

for f in *.mp4 *.mkv; do
  dir="${f%.*}"
  mkdir -p -- "$dir"
  echo "$f -> $dir/"
  ffmpeg -i "$f" "$dir/frame_%04d.png"
done
