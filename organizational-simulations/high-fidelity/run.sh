#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then
  echo "usage: $0 <software-development|logistics-supply-chain>" >&2
  exit 2
fi
case "$1" in
  software-development|logistics-supply-chain) domain="$1" ;;
  *) echo "unsupported high-fidelity simulation: $1" >&2; exit 2 ;;
esac
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
research="${AXIOM_RESEARCH_DIR:-$(cd -- "$here/../../.." && pwd)/axiom-research}"
executor="$research/simulations/$domain/high-fidelity/cycle/execute.py"
[[ -f "$executor" ]] || { echo "axiom-research high-fidelity executor not found: $executor" >&2; exit 1; }
out="${AXIOM_SIM_OUTPUT:-/tmp/axiom-demo-high-fidelity-$domain}"
exec python "$executor" --out-dir "$out"
