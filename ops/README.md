# AXIOM Engineering Utilities

A reusable toolkit for document conversion, structured text bundles and media inspection.

- `md2html.py`: Markdown to standalone HTML with atomic output.
- `converters/json_to_md.py`: structured JSON to Markdown tables.
- `files/bundle-text.sh` and `files/split_text_bundle.py`: text bundle round trips.
- `media/extract-frames.sh` and `media/check-metadata.sh`: FFmpeg/ExifTool inspection utilities.

## Run

```bash
python -m pip install -r requirements-md2html.txt
python -m unittest discover -s tests -v
```

Convert trusted Markdown documents; embedded HTML is preserved. Media commands use the corresponding FFmpeg/ExifTool executables. Input paths, destinations and operating settings are explicit command arguments. The original MIT license is retained; source file identities are recorded in [SOURCES.json](../SOURCES.json).
