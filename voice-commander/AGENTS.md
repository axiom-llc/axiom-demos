# Durable Agent Rules: Voice Commander

- For command execution, transcript/user-controlled values must never reach shell=True.
- Dynamic commands must use argv with shell=False unless an explicitly reviewed exception is required.
- shell=True is permitted only for exact static commands originating from trusted configuration.
- Preserve exact phrase matching for static commands; do not introduce fuzzy/prefix/substring matching without explicit authorization.
- Security tests must mock subprocess execution.
- Do not use network access or add dependencies without explicit authorization.
- Minimize file reads and context.
- requirements.txt is currently outside this task; do not modify or stage it.
- Known security baseline: commit dce912a.
