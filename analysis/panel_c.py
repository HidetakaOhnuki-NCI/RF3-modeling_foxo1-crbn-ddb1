"""Render the FOXO1-residue CRBN contact profile for Figure Panel C."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


NATIVE_COLOR = "#E67E22"
RANDOMIZED_COLOR = "#4D4D4D"
REQUIRED_COLUMNS = (
    "foxo1_position",
    "cc90009",
    "native_frequency_pct",
    "native_wilson95_low",
    "native_wilson95_high",
    "randomized_frequency_pct",
    "randomized_wilson95_low",
    "randomized_wilson95_high",
    "bh_q",
    "significant",
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


def load_panel_c_counts(path: Path) -> pd.DataFrame:
    """Read and validate the 655-position table for both CC-90009 states."""
    frame = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Panel C data are missing columns: {missing}")
    frame = frame.copy()
    frame["foxo1_position"] = pd.to_numeric(frame["foxo1_position"], errors="raise").astype(int)
    if set(frame["cc90009"].astype(str)) != {"absent", "present"}:
        raise ValueError("Panel C requires absent and present CC-90009 states")
    for condition in ("absent", "present"):
        rows = frame.loc[frame["cc90009"] == condition].sort_values("foxo1_position")
        if rows["foxo1_position"].tolist() != list(range(1, 656)):
            raise ValueError(f"Panel C {condition} rows must cover FOXO1 positions 1-655 once")
    return frame.sort_values(["cc90009", "foxo1_position"]).reset_index(drop=True)


def build_panel_c_figure(frame: pd.DataFrame):
    """Build the two-panel Native-versus-randomized FOXO1 profile."""
    figure, axes = plt.subplots(2, 1, figsize=(16, 8.5), sharex=True, sharey=True)
    panel_specs = (
        ("absent", "Without CC-90009"),
        ("present", "With CC-90009"),
    )
    for axis, (condition, title) in zip(axes, panel_specs, strict=True):
        rows = frame.loc[frame["cc90009"] == condition].sort_values("foxo1_position")
        x = rows["foxo1_position"].to_numpy(dtype=float)
        native = rows["native_frequency_pct"].to_numpy(dtype=float)
        randomized = rows["randomized_frequency_pct"].to_numpy(dtype=float)
        native_low = 100.0 * rows["native_wilson95_low"].to_numpy(dtype=float)
        native_high = 100.0 * rows["native_wilson95_high"].to_numpy(dtype=float)
        randomized_low = 100.0 * rows["randomized_wilson95_low"].to_numpy(dtype=float)
        randomized_high = 100.0 * rows["randomized_wilson95_high"].to_numpy(dtype=float)
        axis.fill_between(x, native_low, native_high, color=NATIVE_COLOR, alpha=0.14, linewidth=0)
        axis.fill_between(
            x,
            randomized_low,
            randomized_high,
            color=RANDOMIZED_COLOR,
            alpha=0.12,
            linewidth=0,
        )
        axis.plot(x, native, color=NATIVE_COLOR, linestyle="-", linewidth=2.3, label="Native FOXO1")
        axis.plot(
            x,
            randomized,
            color=RANDOMIZED_COLOR,
            linestyle="--",
            linewidth=1.4,
            label="Randomized peptides",
        )
        for position, n_high, r_high, significant in zip(
            x,
            native_high,
            randomized_high,
            rows["significant"],
            strict=True,
        ):
            if _truth(significant):
                axis.text(
                    position,
                    max(n_high, r_high) + 1.2,
                    "*",
                    color="#000000",
                    fontsize=12,
                    ha="center",
                    va="bottom",
                    clip_on=False,
                )
        axis.set_title(title, loc="left", fontsize=13, fontweight="bold")
        axis.set_ylabel("CRBN contact probability (%)")
        axis.set_ylim(0.0, 60.0)
        axis.grid(False)
        axis.spines[["top", "right"]].set_visible(False)
        axis.spines[["left", "bottom"]].set_linewidth(1.6)
        axis.tick_params(width=1.6)
    axes[0].legend(frameon=False, ncol=2, loc="upper right")
    axes[-1].set_xlim(1, 655)
    axes[-1].set_xticks([1, *range(50, 601, 50), 655])
    axes[-1].set_xlabel("FOXO1 residue number")
    figure.tight_layout(h_pad=1.4)
    return figure


def render_panel_c(input_csv: Path, output_path: Path, *, dpi: int = 300) -> Path:
    """Validate the Panel C CSV and write a high-resolution PNG."""
    frame = load_panel_c_counts(input_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure = build_panel_c_figure(frame)
    try:
        figure.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    finally:
        plt.close(figure)
    return output_path
