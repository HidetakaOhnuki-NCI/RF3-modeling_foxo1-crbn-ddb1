"""Render the FOXO1 541-580 to CRBN-residue profile for Figure Panel D."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.path import Path as MarkerPath
from matplotlib.transforms import blended_transform_factory


NATIVE_COLOR = "#2E86AB"
RANDOMIZED_COLOR = "#4D4D4D"
ARROWHEAD_COLOR = "#003B6F"
SOURCE_TILE = "tile_0541_0580"
GSPT1_CONTACT_RESIDUES = (
    148,
    149,
    150,
    151,
    152,
    351,
    352,
    353,
    355,
    357,
    371,
    372,
    376,
    377,
    378,
    386,
    388,
    390,
    395,
    397,
    400,
    420,
)
REQUIRED_COLUMNS = (
    "source_tile",
    "crbn_residue_id",
    "native_contact_fraction",
    "native_wilson95_low",
    "native_wilson95_high",
    "randomized_contact_fraction",
    "randomized_wilson95_low",
    "randomized_wilson95_high",
    "significant_within_tile_q0p05",
)


def _truth(value: object) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"Invalid Boolean value: {value!r}")


def load_panel_d_counts(path: Path) -> pd.DataFrame:
    """Read and validate FOXO1 541-580 contacts for CRBN residues 46-442."""
    frame = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Panel D data are missing columns: {missing}")
    if set(frame["source_tile"].astype(str)) != {SOURCE_TILE}:
        raise ValueError(f"Panel D data must contain only {SOURCE_TILE}")
    frame = frame.copy()
    frame["crbn_residue_id"] = pd.to_numeric(frame["crbn_residue_id"], errors="raise").astype(int)
    frame = frame.sort_values("crbn_residue_id").reset_index(drop=True)
    if frame["crbn_residue_id"].tolist() != list(range(46, 443)):
        raise ValueError("Panel D must cover CRBN residues 46-442 exactly once")
    return frame


def build_panel_d_figure(frame: pd.DataFrame):
    """Build the single-panel CRBN residue profile with GSPT1 arrowheads."""
    residues = frame["crbn_residue_id"].to_numpy(dtype=float)
    native = 100.0 * frame["native_contact_fraction"].to_numpy(dtype=float)
    randomized = 100.0 * frame["randomized_contact_fraction"].to_numpy(dtype=float)
    native_low = 100.0 * frame["native_wilson95_low"].to_numpy(dtype=float)
    native_high = 100.0 * frame["native_wilson95_high"].to_numpy(dtype=float)
    randomized_low = 100.0 * frame["randomized_wilson95_low"].to_numpy(dtype=float)
    randomized_high = 100.0 * frame["randomized_wilson95_high"].to_numpy(dtype=float)
    largest_upper = max(float(native_high.max()), float(randomized_high.max()))
    upper_limit = max(10.0, 5.0 * float(np.ceil((largest_upper + 5.0) / 5.0)))

    figure, axis = plt.subplots(figsize=(16, 5.2))
    axis.fill_between(residues, native_low, native_high, color=NATIVE_COLOR, alpha=0.13, linewidth=0)
    axis.fill_between(
        residues,
        randomized_low,
        randomized_high,
        color=RANDOMIZED_COLOR,
        alpha=0.10,
        linewidth=0,
    )
    axis.plot(residues, native, color=NATIVE_COLOR, linestyle="-", linewidth=2.5, label="Native FOXO1 541-580")
    axis.plot(
        residues,
        randomized,
        color=RANDOMIZED_COLOR,
        linestyle="--",
        linewidth=2.0,
        label="Randomized peptides",
    )
    for residue, upper, significant in zip(
        residues,
        np.maximum(native_high, randomized_high),
        frame["significant_within_tile_q0p05"],
        strict=True,
    ):
        if _truth(significant):
            axis.text(
                residue,
                upper + 0.9,
                "*",
                color="#000000",
                fontsize=20,
                ha="center",
                va="bottom",
                clip_on=False,
                zorder=5,
            )
    arrowhead = MarkerPath(
        [(-0.18, 0.7), (0.18, 0.7), (0.0, -1.0), (-0.18, 0.7)],
        [MarkerPath.MOVETO, MarkerPath.LINETO, MarkerPath.LINETO, MarkerPath.CLOSEPOLY],
    )
    axis.plot(
        GSPT1_CONTACT_RESIDUES,
        [1.055] * len(GSPT1_CONTACT_RESIDUES),
        transform=blended_transform_factory(axis.transData, axis.transAxes),
        linestyle="None",
        marker=arrowhead,
        markersize=11,
        markerfacecolor=ARROWHEAD_COLOR,
        markeredgecolor=ARROWHEAD_COLOR,
        clip_on=False,
        zorder=6,
        label="_gspt1_contact_residues",
    )
    axis.set_xlim(46, 442)
    axis.set_ylim(0.0, upper_limit)
    axis.set_xticks(list(range(60, 441, 20)))
    axis.set_xlabel("CRBN residue number (chain B, 6XK9 construct numbering)")
    axis.set_ylabel("FOXO1 contact probability (%)")
    axis.set_title("FOXO1 541-580 with CC-90009", loc="left", fontweight="bold")
    axis.legend(frameon=False, loc="upper left")
    axis.grid(False)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_linewidth(1.6)
    axis.tick_params(width=1.6)
    figure.subplots_adjust(left=0.07, right=0.99, top=0.84, bottom=0.16)
    return figure


def render_panel_d(input_csv: Path, output_path: Path, *, dpi: int = 300) -> Path:
    """Validate the Panel D CSV and write a high-resolution PNG."""
    frame = load_panel_d_counts(input_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure = build_panel_d_figure(frame)
    try:
        figure.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    finally:
        plt.close(figure)
    return output_path
