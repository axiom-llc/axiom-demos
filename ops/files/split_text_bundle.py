#!/usr/bin/env python3
# split_files.py
"""
Split a single text file containing multiple:

    ===== BEGIN FILE: <path> =====
    <content>
    ===== END FILE: <path> =====

blocks into individual files on disk, preserving relative paths
(creating parent directories as needed).

Usage:
    python3 split_files.py combined.txt [output_dir]

    combined.txt   path to the file containing the BEGIN/END blocks
    output_dir     optional; defaults to current directory
"""
import sys
import re
from pathlib import Path

BEGIN_RE = re.compile(r"^===== BEGIN FILE: (.+?) =====\s*$")
END_RE = re.compile(r"^===== END FILE: (.+?) =====\s*$")


def split(source_path: Path, out_dir: Path) -> int:
    lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines()

    count = 0
    i = 0
    n = len(lines)

    while i < n:
        m = BEGIN_RE.match(lines[i])
        if not m:
            i += 1
            continue

        rel_path = m.group(1).strip()
        # normalize leading "./" and backslashes so it maps cleanly
        # onto whatever OS this runs on
        rel_path = rel_path[2:] if rel_path.startswith("./") else rel_path
        rel_path = rel_path.replace("\\", "/")

        body_start = i + 1
        j = body_start
        end_match = None
        while j < n:
            em = END_RE.match(lines[j])
            if em and em.group(1).strip() == m.group(1).strip():
                end_match = em
                break
            j += 1

        if end_match is None:
            print(f"ERROR: no matching END FILE for '{rel_path}' "
                  f"(BEGIN at line {i + 1}) — stopping.", file=sys.stderr)
            return count

        body = "\n".join(lines[body_start:j])
        # strip exactly one leading and one trailing blank line, if present,
        # since the BEGIN/END markers usually sit on their own lines
        if body.startswith("\n"):
            body = body[1:]

        target = out_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body + "\n", encoding="utf-8")

        print(f"wrote {target} ({len(body)} bytes)")
        count += 1
        i = j + 1

    return count


def main() -> None:
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <combined_file> [output_dir]", file=sys.stderr)
        sys.exit(1)

    source_path = Path(sys.argv[1])
    if not source_path.is_file():
        print(f"ERROR: '{source_path}' not found or not a file.", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)

    written = split(source_path, out_dir)
    print(f"\n{written} file(s) written under {out_dir.resolve()}")


if __name__ == "__main__":
    main()
