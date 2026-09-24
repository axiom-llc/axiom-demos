# AXIOM Core Stack Reference

Deterministic executable reference for the canonical ASON → APEX → RAG boundaries. The implementation is owned by `axiom-infra/core_stack.py`; this demo provides the discoverable operator entry point and does not duplicate runtime logic.

It requires the sibling AXIOM checkouts and the local Infra Compose stack. The run performs a provider-free RAG inspection, submits an exact local file plan through ASON, verifies APEX's durable authorization/plan binding through the run-detail API, and emits exact repository revisions plus a SHA-256 evidence digest.

```bash
cd ../axiom-infra
export RAG_API_TOKEN='local-test-token' APEX_API_KEY='local-test-key' GEMINI_API_KEY='offline-validation-only'
docker compose up --build --wait apex
../axiom-demos/core-stack/run.sh
docker compose down
```

This is local integration evidence, not a production deployment, external security assurance, cryptographic attestation, or an exactly-once guarantee.
