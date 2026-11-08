"""RSI source-to-diff validation, exact rollback, and parser semantics."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from rsi.native import GenerationError, generate, propose, validate_rule
from rsi.benchmark import benchmark, fixture, load

ROOT = Path(__file__).resolve().parents[1]
RULE = json.loads((ROOT / "rsi/generators.json").read_text())["rules"][0]
SOURCE = (ROOT / RULE["path"]).read_text(encoding="utf-8")


class TestNativeRSI(unittest.TestCase):
    def test_revision_pin_idempotence_and_saturation(self):
        result = generate(ROOT)
        self.assertEqual(len(result["candidates"]), 1)
        self.assertFalse(result["mutation_authority"])
        self.assertEqual(propose(SOURCE, RULE, "a"*40), propose(SOURCE, RULE, "a"*40))
        self.assertIsNone(propose(SOURCE.replace(RULE["before"],RULE["after"],1), RULE, "a"*40))
        with self.assertRaises(GenerationError):
            generate(ROOT, "a"*40)

    def test_ambiguous_or_unsafe_patch_rejected(self):
        with self.assertRaises(GenerationError):
            propose(SOURCE+RULE["before"],RULE,"a"*40)
        for path in ("/root/x.py","../escaped.py","tests/test_x.py"):
            with self.assertRaises(GenerationError):
                validate_rule({**RULE,"path":path})

    def test_output_equivalence_and_reverse_patch(self):
        patch = propose(SOURCE,RULE,"a"*40)["patch"]
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = root / RULE["path"]
            target.parent.mkdir(parents=True)
            target.write_text(SOURCE)
            before = target.read_bytes()
            subprocess.run(["git","init","-q"],cwd=root,check=True)
            for arguments in (["git","apply","--check","-"],["git","apply","-"],
                              ["git","apply","-R","--check","-"],["git","apply","-R","-"]):
                subprocess.run(arguments,cwd=root,input=patch,text=True,check=True,
                               capture_output=True)
            self.assertEqual(target.read_bytes(),before)
        original = load(SOURCE,RULE["path"])
        modified = load(SOURCE.replace(RULE["before"],RULE["after"],1),RULE["path"])
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            src=root/"input.txt"
            src.write_text(fixture())
            old=root/"old"
            new=root/"new"
            old.mkdir()
            new.mkdir()
            self.assertEqual(original(src,old),modified(src,new))
            self.assertEqual((old/"results/output.txt").read_bytes(),
                             (new/"results/output.txt").read_bytes())

    def test_paired_synthetic_benchmark_receipt(self):
        report = benchmark(ROOT)
        self.assertTrue(report["quality_equivalent"])
        self.assertEqual(report["paired_samples"],11)
        self.assertFalse(report["promotion_authorized"])


if __name__ == "__main__":
    unittest.main()
