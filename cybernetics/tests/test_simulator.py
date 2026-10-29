import unittest

from robotics import Authorization, SafetyEnvelope, SimulatedMoveTask, execute, verify_receipt


def authorized(task: SimulatedMoveTask) -> Authorization:
    return Authorization("auth-001", task.digest())


class SimulatorTests(unittest.TestCase):
    def test_deterministic_success_and_receipt(self):
        task = SimulatedMoveTask("move-1", 0, 3, SafetyEnvelope(-5, 5))
        first = execute(task, authorized(task))
        second = execute(task, authorized(task))

        self.assertEqual(first, second)
        self.assertEqual(first.result, "SUCCEEDED")
        self.assertEqual(first.terminal_position, 3)
        self.assertTrue(verify_receipt(first))
        self.assertEqual(
            [event["position"] for event in first.telemetry if event["event"] == "move"],
            [1, 2, 3],
        )

    def test_missing_authorization_rejected_without_motion(self):
        task = SimulatedMoveTask("move-2", 0, 2, SafetyEnvelope(-5, 5))
        receipt = execute(task, None)

        self.assertEqual(receipt.result, "REJECTED")
        self.assertEqual(receipt.reason, "authorization_required")
        self.assertEqual(receipt.terminal_position, 0)
        self.assertEqual(receipt.telemetry, ())
        self.assertTrue(verify_receipt(receipt))

    def test_mismatched_authorization_rejected(self):
        task = SimulatedMoveTask("move-3", 0, 2, SafetyEnvelope(-5, 5))
        receipt = execute(task, Authorization("auth-wrong", "0" * 64))

        self.assertEqual(receipt.result, "REJECTED")
        self.assertEqual(receipt.reason, "authorization_task_digest_mismatch")
        self.assertEqual(receipt.terminal_position, 0)
        self.assertTrue(verify_receipt(receipt))

    def test_out_of_bounds_target_rejected_before_motion(self):
        task = SimulatedMoveTask("move-4", 0, 6, SafetyEnvelope(-5, 5))
        receipt = execute(task, authorized(task))

        self.assertEqual(receipt.result, "REJECTED")
        self.assertEqual(receipt.reason, "position_outside_safety_envelope")
        self.assertEqual(receipt.terminal_position, 0)
        self.assertEqual(receipt.telemetry, ())
        self.assertTrue(verify_receipt(receipt))

    def test_explicit_execution_failure_is_deterministic(self):
        task = SimulatedMoveTask("move-5", 0, 4, SafetyEnvelope(-5, 5), fault_after_steps=2)
        first = execute(task, authorized(task))
        second = execute(task, authorized(task))

        self.assertEqual(first, second)
        self.assertEqual(first.result, "FAILED")
        self.assertEqual(first.reason, "injected_execution_failure")
        self.assertEqual(first.terminal_position, 2)
        self.assertEqual(first.telemetry[-1]["event"], "fault")
        self.assertTrue(verify_receipt(first))

    def test_receipt_tamper_is_detected(self):
        task = SimulatedMoveTask("move-6", 0, 1, SafetyEnvelope(-5, 5))
        receipt = execute(task, authorized(task))
        tampered = receipt.__class__(
            task_id=receipt.task_id,
            task_digest=receipt.task_digest,
            authorization_id=receipt.authorization_id,
            result=receipt.result,
            reason=receipt.reason,
            terminal_position=99,
            telemetry=receipt.telemetry,
            receipt_digest=receipt.receipt_digest,
        )
        self.assertFalse(verify_receipt(tampered))


if __name__ == "__main__":
    unittest.main()
