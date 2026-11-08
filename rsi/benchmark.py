"""Synthetic bundle parser paired microbenchmark, no user data."""
from __future__ import annotations
import argparse
from contextlib import redirect_stderr, redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
from statistics import median
import tempfile
import time
from rsi.native import generate


def load(source, path):
    namespace = {"__name__": "rsi_bundle_parser"}
    exec(compile(source, path, "exec"), namespace)
    return namespace["split"]


def fixture():
    inner = ["Data line %05d with symbols %s" % (i, "!@#$") for i in range(9000)]
    inner[213] = "===== END FILE: incorrect.txt ====="
    return ("===== BEGIN FILE: ./results/output.txt =====\n" +
            "\n".join(inner) +
            "\n===== END FILE: ./results/output.txt =====\n")


def benchmark(root):
    result = generate(root)
    if len(result["candidates"]) != 1:
        return {"status": "NO_APPLICABLE_RULE"}
    rule = json.loads((root / "rsi/generators.json").read_text())["rules"][0]
    source = (root / rule["path"]).read_text(encoding="utf-8")
    after = source.replace(rule["before"], rule["after"], 1)
    original, candidate = load(source, rule["path"]), load(after, rule["path"])
    with tempfile.TemporaryDirectory() as d:
        base = Path(d)
        inp = base / "bundle.txt"
        inp.write_text(fixture())
        a = base / "baseline"
        b = base / "candidate"
        a.mkdir()
        b.mkdir()
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            c0 = original(inp, a)
            c1 = candidate(inp, b)
        if c0 != c1 or c0 != 1 or (
            a / "results/output.txt").read_bytes() != (
            b / "results/output.txt").read_bytes():
            raise ValueError("bundle output or count changed")
        # Malformed bundle: identical failed partial scan and no file creation.
        inp.write_text("===== BEGIN FILE: missed.txt =====\na\n")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            if original(inp, a) != candidate(inp, b):
                raise ValueError("malformed input behavior changed")
        inp.write_text(fixture())
        measures = []
        for i in range(11):
            pairs = (("base", original, a), ("candidate", candidate, b)) if i % 2 == 0 else (
                ("candidate", candidate, b), ("base", original, a))
            sample = {}
            for label, fn, destination in pairs:
                output = io.StringIO()
                start = time.perf_counter_ns()
                with redirect_stdout(output):
                    for _ in range(30):
                        fn(inp, destination)
                sample[label] = (time.perf_counter_ns() - start) / 30
            measures.append(sample)
    old = median(x["base"] for x in measures)
    new = median(x["candidate"] for x in measures)
    return {
        "schema": "axiom-native-rsi/benchmark-v1",
        "source_revision": result["source_revision"],
        "candidate_id": result["candidates"][0]["candidate_id"],
        "source_sha256": sha256(source.encode()).hexdigest(),
        "candidate_sha256": sha256(after.encode()).hexdigest(),
        "workload_provenance": "synthetic 9000-line text bundle with mismatched END marker",
        "paired_samples": 11,
        "operations_per_sample": 30,
        "baseline_median_ns_per_op": old,
        "candidate_median_ns_per_op": new,
        "paired_median_gain_ns_per_op": median(x["base"]-x["candidate"] for x in measures),
        "gain_percentage": (old-new)*100/old if old else None,
        "quality_equivalent": True,
        "promotion_authorized": False,
        "status": "POSITIVE_MACHINE_MEASUREMENT" if new < old else "NONPOSITIVE_MEASUREMENT",
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = benchmark(root)
    if args.output:
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n")
    print(json.dumps(result, sort_keys=True))
