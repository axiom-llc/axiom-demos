#!/usr/bin/env python3
"""Convert Markdown files to deterministic standalone styled HTML."""

import argparse
from html import escape
import os
from pathlib import Path
import tempfile

try:
    import markdown
except ImportError as exc:  # pragma: no cover - exercised by CLI environment
    raise SystemExit(
        "md2html requires Python-Markdown; install requirements-md2html.txt"
    ) from exc

EXTENSIONS = ("fenced_code", "tables", "toc", "nl2br")
CSS = """body { max-width: 900px; margin: auto; padding: 2em; background: #002b36; color: #839496; font-family: sans-serif; line-height: 1.6; }
a { color: #268bd2; }
h1,h2,h3,h4,h5,h6 { color: #93a1a1; }
code, pre { background: #073642; color: #93a1a1; }
pre { padding: 1em; overflow-x: auto; }
blockquote { border-left: 4px solid #586e75; padding-left: 1em; color: #93a1a1; }
table { border-collapse: collapse; margin: 1em 0; }
th, td { border: 1px solid #586e75; padding: 0.5em 1em; }
th { background: #073642; color: #93a1a1; }
"""
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{css}</style>
</head>
<body>
{content}
</body>
</html>
"""


def render_markdown(text: str, title: str) -> str:
    """Render trusted Markdown text; raw HTML is intentionally not sanitized."""
    content = markdown.markdown(text, extensions=list(EXTENSIONS))
    return HTML_TEMPLATE.format(title=escape(title), css=CSS, content=content)


def convert(md_file: str | Path, html_file: str | Path) -> Path:
    source = Path(md_file)
    target = Path(html_file)
    if source.resolve() == target.resolve():
        raise ValueError("input and output paths must differ")
    text = source.read_text(encoding="utf-8")
    output = render_markdown(text, source.stem)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(output)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, target)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Markdown to styled HTML")
    parser.add_argument("input", help="Markdown file")
    parser.add_argument("-o", "--output", help="Output HTML file")
    args = parser.parse_args()
    source = Path(args.input)
    target = Path(args.output) if args.output else source.with_suffix(".html")
    try:
        output = convert(source, target)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
