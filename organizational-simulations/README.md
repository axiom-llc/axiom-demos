# Organizational simulations

Thin executable wrappers for the five accepted AXIOM organizational simulations. The canonical models, fixtures, execution requests, evidence, evaluations, and case-study records live in `axiom-research`; this directory contains no independent workflow logic.

Each wrapper delegates to the matching Research `execute.py`, runs against isolated local APEX state, and writes fresh output under `/tmp` by default. Set `AXIOM_RESEARCH_DIR` when Research is not a sibling checkout and `AXIOM_SIM_OUTPUT` to select another non-canonical output directory.

```bash
./organizational-simulations/robotics-production.sh
./organizational-simulations/software-development.sh
./organizational-simulations/specialty-care-administration.sh
./organizational-simulations/soc-operations.sh
./organizational-simulations/logistics-supply-chain.sh
```

These are `VALIDATED_EXECUTABLE_DEMO` reproductions of synthetic local-file simulations, not production deployments. They do not establish regulatory compliance, independent assurance, real-world throughput, economic benefit, exactly-once external effects, or autonomous professional authority.

Canonical evidence and publication boundaries: https://github.com/axiom-llc/axiom-research/tree/main/simulations

## Accepted high-fidelity cycles

Software development and logistics/supply-chain also have accepted three-day, six-work-item synthetic operational cycles covering carryover, dynamic arrivals, queue growth/drain, staffing/calendar changes, shared-resource contention, and balanced synthetic ledger cycles. Reproduce them through the thin wrappers in [`high-fidelity/`](high-fidelity/).
