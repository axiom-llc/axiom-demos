# AXIOM Cybernetics Simulation

Deterministic robotics simulation with authorization binding, safety envelopes, fault injection, telemetry and tamper-evident execution receipts.

## Run

Python3.11 or newer; standard library only.

```bash
python -m unittest discover -s tests -v
```

The six runtime tests exercise deterministic motion, rejection before motion, task-bound authorization, injected faults and receipt tampering. Scenario fixtures provide modular inspection and fabrication models. [Original source identities](../SOURCES.json) preserve the private engineering source revision without exporting operational records or source media.

MIT-licensed software.
