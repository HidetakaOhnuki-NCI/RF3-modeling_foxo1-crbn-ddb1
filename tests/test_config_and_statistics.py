from __future__ import annotations

import math
import unittest
from pathlib import Path

try:
    from analysis.config import load_protocol, validate_protocol_record
    from analysis.statistics import benjamini_hochberg, wilson_interval
except ImportError:
    load_protocol = None
    validate_protocol_record = None
    benjamini_hochberg = None
    wilson_interval = None


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class ProtocolTests(unittest.TestCase):
    def require_implementation(self) -> None:
        self.assertIsNotNone(load_protocol, "analysis.config is not implemented")
        self.assertIsNotNone(
            validate_protocol_record, "protocol record validation is not implemented"
        )

    def test_public_protocol_accepts_only_200_steps_10_recycles_batch_1(self):
        self.require_implementation()
        protocol = load_protocol(PACKAGE_ROOT / "config" / "rf3_protocol.json")
        self.assertEqual(protocol["inference"]["num_steps"], 200)
        self.assertEqual(protocol["inference"]["n_recycles"], 10)
        self.assertEqual(protocol["inference"]["diffusion_batch_size"], 1)
        validate_protocol_record(
            {"num_steps": 200, "n_recycles": 10, "diffusion_batch_size": 1},
            protocol,
        )

    def test_rejects_legacy_and_boolean_protocol_values(self):
        self.require_implementation()
        protocol = {
            "inference": {
                "num_steps": 200,
                "n_recycles": 10,
                "diffusion_batch_size": 1,
            }
        }
        invalid_records = (
            {"num_steps": 50, "n_recycles": 1, "diffusion_batch_size": 1},
            {"num_steps": True, "n_recycles": 10, "diffusion_batch_size": 1},
            {"num_steps": 200, "n_recycles": 10},
        )
        for record in invalid_records:
            with self.subTest(record=record), self.assertRaises(ValueError):
                validate_protocol_record(record, protocol)


class StatisticsTests(unittest.TestCase):
    def require_implementation(self) -> None:
        self.assertIsNotNone(benjamini_hochberg, "BH correction is not implemented")
        self.assertIsNotNone(wilson_interval, "Wilson interval is not implemented")

    def test_benjamini_hochberg_matches_hand_calculated_values(self):
        self.require_implementation()
        observed = benjamini_hochberg([0.01, 0.04, 0.03])
        expected = [0.03, 0.04, 0.04]
        for actual, wanted in zip(observed, expected, strict=True):
            self.assertAlmostEqual(actual, wanted, places=12)

    def test_wilson_interval_for_zero_of_100(self):
        self.require_implementation()
        low, high = wilson_interval(0, 100)
        self.assertTrue(math.isclose(low, 0.0, abs_tol=1e-15))
        self.assertAlmostEqual(high, 0.03699349820698568, places=12)

    def test_wilson_interval_rejects_invalid_counts(self):
        self.require_implementation()
        for successes, total in ((1, 0), (-1, 100), (101, 100)):
            with self.subTest(successes=successes, total=total), self.assertRaises(
                ValueError
            ):
                wilson_interval(successes, total)


if __name__ == "__main__":
    unittest.main()
