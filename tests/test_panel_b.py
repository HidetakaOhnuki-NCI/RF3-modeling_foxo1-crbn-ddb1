from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

try:
    from analysis.panel_b import (
        REQUIRED_CONDITIONS,
        build_panel_b_figure,
        calculate_panel_b_statistics,
        render_panel_b,
        validate_panel_b_rows,
    )
except ImportError:
    REQUIRED_CONDITIONS = ()
    build_panel_b_figure = None
    calculate_panel_b_statistics = None
    render_panel_b = None
    validate_panel_b_rows = None


PROTOCOL = {
    "inference": {
        "num_steps": 200,
        "n_recycles": 10,
        "diffusion_batch_size": 1,
    },
    "replicates": {"gspt1_models_per_arm": 3},
}


def matched_frame() -> pd.DataFrame:
    values = {
        "gspt1_wt_cc90009_present": [0.80, 0.90, 0.70],
        "gspt1_wt_cc90009_absent": [0.10, 0.20, 0.15],
        "gspt1_g575n_cc90009_present": [0.05, 0.10, 0.20],
        "gspt1_randomized_cc90009_present": [0.00, 0.05, 0.10],
    }
    rows = []
    for condition_index, (condition, similarities) in enumerate(values.items()):
        for replicate_index, similarity in enumerate(similarities):
            rows.append(
                {
                    "condition_id": condition,
                    "seed": 1000 * (condition_index + 1) + replicate_index,
                    "num_steps": 200,
                    "n_recycles": 10,
                    "diffusion_batch_size": 1,
                    "jaccard_similarity": similarity,
                }
            )
    return pd.DataFrame(rows)


class PanelBTests(unittest.TestCase):
    def require_implementation(self) -> None:
        self.assertIsNotNone(validate_panel_b_rows, "Panel B is not implemented")
        self.assertEqual(len(REQUIRED_CONDITIONS), 4)

    def test_rejects_mixed_protocol_and_incomplete_arms(self):
        self.require_implementation()
        mixed = matched_frame()
        mixed.loc[0, "num_steps"] = 50
        with self.assertRaisesRegex(ValueError, "num_steps"):
            validate_panel_b_rows(mixed, PROTOCOL)

        incomplete = matched_frame().query(
            "condition_id != 'gspt1_randomized_cc90009_present'"
        )
        with self.assertRaisesRegex(ValueError, "condition arms"):
            validate_panel_b_rows(incomplete, PROTOCOL)

    def test_rejects_duplicate_seeds_and_unbalanced_replicates(self):
        self.require_implementation()
        duplicate = matched_frame()
        duplicate.loc[1, "seed"] = duplicate.loc[0, "seed"]
        with self.assertRaisesRegex(ValueError, "duplicate seed"):
            validate_panel_b_rows(duplicate, PROTOCOL)

        unbalanced = matched_frame().drop(index=0)
        with self.assertRaisesRegex(ValueError, "replicate"):
            validate_panel_b_rows(unbalanced, PROTOCOL)

    def test_matched_rows_generate_two_prespecified_comparisons(self):
        self.require_implementation()
        frame = matched_frame()
        validate_panel_b_rows(frame, PROTOCOL)
        results = calculate_panel_b_statistics(frame)
        self.assertEqual(
            results["comparison_id"].tolist(),
            ["wt_ccplus_vs_wt_ccminus", "wt_ccplus_vs_g575n_ccplus"],
        )
        self.assertTrue((results["alternative"] == "greater").all())
        self.assertTrue((results["mannwhitney_p"] < 0.1).all())

    def test_matched_rows_generate_nonempty_four_arm_figure(self):
        self.require_implementation()
        frame = matched_frame()
        figure = build_panel_b_figure(frame)
        try:
            self.assertEqual(len(figure.axes), 1)
            self.assertEqual(len(figure.axes[0].get_xticklabels()), 4)
        finally:
            import matplotlib.pyplot as plt

            plt.close(figure)

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "panel_b.png"
            render_panel_b(frame, output)
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 10_000)


if __name__ == "__main__":
    unittest.main()
