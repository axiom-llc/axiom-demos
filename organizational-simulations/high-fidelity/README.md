# High-fidelity organizational cycles

Thin wrappers for the two accepted multi-day AXIOM operational-fidelity cycles. Canonical models, executors, retained evidence, acceptance records, and publication claims live in `axiom-research`.

```bash
./organizational-simulations/high-fidelity/software-development.sh
./organizational-simulations/high-fidelity/logistics-supply-chain.sh
```

Each wrapper delegates to `simulations/<domain>/high-fidelity/cycle/execute.py` in Research and writes fresh output under `/tmp` by default. Set `AXIOM_RESEARCH_DIR` for a non-sibling Research checkout and `AXIOM_SIM_OUTPUT` to select another output directory.

These remain synthetic `VALIDATED_EXECUTABLE_DEMO` reproductions. They do not establish production deployment, regulatory compliance, measured economic benefit, arbitrary-enterprise completeness, or exactly-once external effects.
