from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

try:
    from analysis.panel_c import (
        build_panel_c_figure,
        load_panel_c_counts,
        render_panel_c,
    )
    from analysis.panel_d import (
        GSPT1_CONTACT_RESIDUES,
        build_panel_d_figure,
        load_panel_d_counts,
        render_panel_d,
    )
except ImportError:
    build_panel_c_figure = None
    load_panel_c_counts = None
    render_panel_c = None
    GSPT1_CONTACT_RESIDUES = ()
    build_panel_d_figure = None
    load_panel_d_counts = None
    render_panel_d = None


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PANEL_C_CSV = PACKAGE_ROOT / "data" / "processed" / "panel_c_foxo1_residue_contacts.csv"
PANEL_D_CSV = PACKAGE_ROOT / "data" / "processed" / "panel_d_crbn_541_580_contacts.csv"


class PanelCTests(unittest.TestCase):
    def require_implementation(self) -> None:
        self.assertIsNotNone(load_panel_c_counts, "Panel C is not implemented")

    def test_counts_cover_655_positions_in_both_conditions(self):
        self.require_implementation()
        frame = load_panel_c_counts(PANEL_C_CSV)
        self.assertEqual(len(frame), 1310)
        for condition in ("absent", "present"):
            positions = frame.loc[frame["cc90009"] == condition, "foxo1_position"]
            self.assertEqual(positions.tolist(), list(range(1, 656)))

    def test_figure_has_two_panels_requested_lines_black_stars_and_no_grid(self):
        self.require_implementation()
        frame = load_panel_c_counts(PANEL_C_CSV)
        figure = build_panel_c_figure(frame)
        try:
            self.assertEqual(len(figure.axes), 2)
            for axis in figure.axes:
                self.assertEqual(axis.lines[0].get_linestyle(), "-")
                self.assertEqual(axis.lines[1].get_linestyle(), "--")
                self.assertFalse(any(line.get_visible() for line in axis.get_xgridlines()))
                stars = [text for text in axis.texts if text.get_text() == "*"]
                self.assertGreater(len(stars), 0)
                self.assertTrue(all(text.get_color() == "#000000" for text in stars))
            self.assertEqual(figure.axes[-1].get_xticks()[-2:].tolist(), [600.0, 655.0])
        finally:
            import matplotlib.pyplot as plt

            plt.close(figure)

    def test_panel_c_writes_nonempty_png(self):
        self.require_implementation()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "panel_c.png"
            render_panel_c(PANEL_C_CSV, output)
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 100_000)


class PanelDTests(unittest.TestCase):
    def require_implementation(self) -> None:
        self.assertIsNotNone(load_panel_d_counts, "Panel D is not implemented")
        self.assertEqual(len(GSPT1_CONTACT_RESIDUES), 22)

    def test_counts_cover_crbn_46_through_442_once(self):
        self.require_implementation()
        frame = load_panel_d_counts(PANEL_D_CSV)
        self.assertEqual(len(frame), 397)
        self.assertEqual(frame["crbn_residue_id"].tolist(), list(range(46, 443)))
        self.assertEqual(set(frame["source_tile"]), {"tile_0541_0580"})

    def test_figure_has_one_panel_lines_stars_and_external_arrowheads(self):
        self.require_implementation()
        frame = load_panel_d_counts(PANEL_D_CSV)
        figure = build_panel_d_figure(frame)
        try:
            self.assertEqual(len(figure.axes), 1)
            axis = figure.axes[0]
            self.assertEqual(axis.lines[0].get_linestyle(), "-")
            self.assertEqual(axis.lines[1].get_linestyle(), "--")
            arrow_lines = [
                line for line in axis.lines if line.get_label() == "_gspt1_contact_residues"
            ]
            self.assertEqual(len(arrow_lines), 1)
            self.assertEqual(len(arrow_lines[0].get_xdata()), 22)
            self.assertFalse(arrow_lines[0].get_clip_on())
            stars = [text for text in axis.texts if text.get_text() == "*"]
            self.assertGreater(len(stars), 0)
            self.assertTrue(all(text.get_color() == "#000000" for text in stars))
            self.assertFalse(any(line.get_visible() for line in axis.get_xgridlines()))
        finally:
            import matplotlib.pyplot as plt

            plt.close(figure)

    def test_panel_d_writes_nonempty_png(self):
        self.require_implementation()
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "panel_d.png"
            render_panel_d(PANEL_D_CSV, output)
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 50_000)


if __name__ == "__main__":
    unittest.main()
