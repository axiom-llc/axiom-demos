#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then
  echo "usage: $0 <robotics-production|software-development|specialty-care-administration|soc-operations|logistics-supply-chain>" >&2
  exit 2
fi
case "$1" in
  robotics-production|software-development|specialty-care-administration|soc-operations|logistics-supply-chain) domain="$1" ;;
  *) echo "unsupported simulation: $1" >&2; exit 2 ;;
esac
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
research="${AXIOM_RESEARCH_DIR:-$(cd -- "$here/../.." && pwd)/axiom-research}"
executor="$research/simulations/$domain/execute.py"
[[ -f "$executor" ]] || { echo "axiom-research simulation executor not found: $executor" >&2; exit 1; }
out="${AXIOM_SIM_OUTPUT:-/tmp/axiom-demo-$domain}"
exec python "$executor" --out-dir "$out"
