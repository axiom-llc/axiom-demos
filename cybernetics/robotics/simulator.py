"""Deterministic simulation-only robotics milestone.

No hardware-control capability is implemented here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


@dataclass(frozen=True)
class SafetyEnvelope:
    minimum: int
    maximum: int

    def valid(self) -> bool:
        return self.minimum <= self.maximum

    def contains(self, position: int) -> bool:
        return self.minimum <= position <= self.maximum


@dataclass(frozen=True)
class SimulatedMoveTask:
    task_id: str
    initial_position: int
    target_position: int
    safety: SafetyEnvelope
    fault_after_steps: int | None = None

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "action": "move_simulated_object",
            "initial_position": self.initial_position,
            "target_position": self.target_position,
            "safety": asdict(self.safety),
            "fault_after_steps": self.fault_after_steps,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True)
class Authorization:
    authorization_id: str
    approved_task_digest: str


@dataclass(frozen=True)
class ExecutionReceipt:
    task_id: str
    task_digest: str
    authorization_id: str | None
    result: str
    reason: str
    terminal_position: int
    telemetry: tuple[dict[str, Any], ...]
    receipt_digest: str

    def unsigned_payload(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_digest": self.task_digest,
            "authorization_id": self.authorization_id,
            "result": self.result,
            "reason": self.reason,
            "terminal_position": self.terminal_position,
            "telemetry": list(self.telemetry),
        }


def _receipt(
    task: SimulatedMoveTask,
    authorization_id: str | None,
    result: str,
    reason: str,
    terminal_position: int,
    telemetry: list[dict[str, Any]],
) -> ExecutionReceipt:
    unsigned = {
        "task_id": task.task_id,
        "task_digest": task.digest(),
        "authorization_id": authorization_id,
        "result": result,
        "reason": reason,
        "terminal_position": terminal_position,
        "telemetry": telemetry,
    }
    return ExecutionReceipt(
        task_id=task.task_id,
        task_digest=task.digest(),
        authorization_id=authorization_id,
        result=result,
        reason=reason,
        terminal_position=terminal_position,
        telemetry=tuple(telemetry),
        receipt_digest=_digest(unsigned),
    )


def verify_receipt(receipt: ExecutionReceipt) -> bool:
    return receipt.receipt_digest == _digest(receipt.unsigned_payload())


def execute(task: SimulatedMoveTask, authorization: Authorization | None) -> ExecutionReceipt:
    """Execute one deterministic simulation-only move.

    Rejection occurs before simulated motion if authorization or safety is invalid.
    Injected faults are deterministic and produce FAILED receipts.
    """
    telemetry: list[dict[str, Any]] = []
    position = task.initial_position

    if not task.task_id:
        return _receipt(task, None, "REJECTED", "empty_task_id", position, telemetry)

    if authorization is None:
        return _receipt(task, None, "REJECTED", "authorization_required", position, telemetry)

    if not authorization.authorization_id:
        return _receipt(task, None, "REJECTED", "empty_authorization_id", position, telemetry)

    if authorization.approved_task_digest != task.digest():
        return _receipt(
            task,
            authorization.authorization_id,
            "REJECTED",
            "authorization_task_digest_mismatch",
            position,
            telemetry,
        )

    if not task.safety.valid():
        return _receipt(
            task,
            authorization.authorization_id,
            "REJECTED",
            "invalid_safety_envelope",
            position,
            telemetry,
        )

    if not task.safety.contains(task.initial_position) or not task.safety.contains(task.target_position):
        return _receipt(
            task,
            authorization.authorization_id,
            "REJECTED",
            "position_outside_safety_envelope",
            position,
            telemetry,
        )

    if task.fault_after_steps is not None and task.fault_after_steps < 0:
        return _receipt(
            task,
            authorization.authorization_id,
            "REJECTED",
            "invalid_fault_step",
            position,
            telemetry,
        )

    direction = 0 if task.target_position == position else (1 if task.target_position > position else -1)
    step = 0

    while position != task.target_position:
        if task.fault_after_steps is not None and step == task.fault_after_steps:
            telemetry.append({"step": step, "position": position, "event": "fault"})
            return _receipt(
                task,
                authorization.authorization_id,
                "FAILED",
                "injected_execution_failure",
                position,
                telemetry,
            )

        next_position = position + direction
        if not task.safety.contains(next_position):
            telemetry.append({"step": step, "position": position, "event": "safety_stop"})
            return _receipt(
                task,
                authorization.authorization_id,
                "FAILED",
                "runtime_safety_limit",
                position,
                telemetry,
            )

        position = next_position
        step += 1
        telemetry.append({"step": step, "position": position, "event": "move"})

    telemetry.append({"step": step, "position": position, "event": "complete"})
    return _receipt(
        task,
        authorization.authorization_id,
        "SUCCEEDED",
        "target_reached",
        position,
        telemetry,
    )
