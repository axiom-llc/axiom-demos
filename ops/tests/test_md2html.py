import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import md2html

MD_SOURCE = """[TOC]

# Alpha Heading

Some **text**.

```python
x = 1
```

| A | B |
|---|---|
| 1 | 2 |
"""


class RenderTests(unittest.TestCase):
    def test_expected_extensions(self):
        html = md2html.render_markdown(MD_SOURCE, 'A < B')
        self.assertIn('<div class="toc">', html)
        self.assertIn('<h1 id="alpha-heading">', html)
        self.assertIn('<pre><code class="language-python">', html)
        self.assertIn('<th>A</th>', html)
        self.assertIn('<title>A &lt; B</title>', html)

    def test_no_implicit_toc(self):
        html = md2html.render_markdown('# Alpha\n', 'Alpha')
        self.assertNotIn('class="toc"', html)

    def test_raw_html_is_not_a_sanitization_boundary(self):
        html = md2html.render_markdown('<span data-test="raw">x</span>', 'raw')
        self.assertIn('<span data-test="raw">x</span>', html)


class ConversionTests(unittest.TestCase):
    def test_atomic_conversion_and_default_cli_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / 'sample.md'
            src.write_text('# Gamma\n', encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(ROOT / 'md2html.py'), str(src)],
                capture_output=True, text=True,
                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            out = src.with_suffix('.html')
            self.assertEqual(result.stdout.strip(), str(out))
            self.assertIn('id="gamma"', out.read_text(encoding='utf-8'))
            self.assertEqual(list(Path(tmp).glob('.sample.html.*')), [])

    def test_refuses_same_input_and_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / 'same.md'
            src.write_text('# Keep me\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'must differ'):
                md2html.convert(src, src)
            self.assertEqual(src.read_text(encoding='utf-8'), '# Keep me\n')

    def test_missing_parent_is_reported_without_partial_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / 'in.md'
            src.write_text('# X\n', encoding='utf-8')
            target = Path(tmp) / 'missing' / 'out.html'
            with self.assertRaises(FileNotFoundError):
                md2html.convert(src, target)
            self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
