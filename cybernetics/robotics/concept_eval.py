"""Deterministic concept-budget evaluation; no hardware I/O."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def evaluate_concept(concept: dict[str, Any]) -> dict[str, Any]:
    b = concept["budgets"]
    expected_battery_mass = b["battery_energy_kwh"] * 1000.0 / b["battery_pack_specific_energy_wh_per_kg"]
    expected_mixed_runtime = b["battery_energy_kwh"] / b["mixed_average_power_kw"]
    expected_heavy_runtime = b["battery_energy_kwh"] / b["heavy_average_power_kw"]
    mass_sum = sum(b["mass_breakdown_kg"].values())

    checks = {
        "simulation_only": concept.get("hardware_control_enabled") is False,
        "battery_mass_consistent": abs(expected_battery_mass - b["mass_breakdown_kg"]["battery_pack"]) <= 0.1,
        "mixed_runtime_consistent": abs(expected_mixed_runtime - b["mixed_runtime_hours"]) <= 0.01,
        "heavy_runtime_consistent": abs(expected_heavy_runtime - b["heavy_runtime_hours"]) <= 0.01,
        "mass_budget_consistent": abs(mass_sum - b["nominal_system_mass_kg"]) <= 0.1,
        "authority_invariant_present": "authority" in concept["safety"]["authority_model"],
        "dependency_dimensions_complete": set(concept["supply_chain_independence"]["measured_categories"])
        == {"materials", "energy", "components", "tools", "maintenance", "software", "human_intervention"},
    }
    payload = {"concept_id": concept["id"], "revision": concept["revision"], "checks": checks}
    return {
        **payload,
        "result": "ACCEPT" if all(checks.values()) else "REVISE",
        "evaluation_digest": sha256(_canonical(payload)).hexdigest(),
    }


def evaluate_path(path: str | Path) -> dict[str, Any]:
    return evaluate_concept(json.loads(Path(path).read_text()))
