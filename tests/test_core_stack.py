from pathlib import Path
def test_core_stack_reference_delegates_to_infra():
    root=Path(__file__).resolve().parents[1]; readme=(root/'core-stack/README.md').read_text(); script=(root/'core-stack/run.sh').read_text()
    assert 'ASON → APEX → RAG' in readme; assert 'axiom-infra/core_stack.py' in readme; assert 'axiom-infra/core_stack.py' in script
