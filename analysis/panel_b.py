"""Protocol-matched GSPT1 control analysis for Figure Panel B."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

from analysis.config import load_protocol, validate_protocol_record


REQUIRED_COLUMNS = (
    "condition_id",
    "seed",
    "num_steps",
    "n_recycles",
    "diffusion_batch_size",
    "jaccard_similarity",
)
REQUIRED_CONDITIONS = (
    "gspt1_wt_cc90009_present",
    "gspt1_wt_cc90009_absent",
    "gspt1_g575n_cc90009_present",
    "gspt1_randomized_cc90009_present",
)
DISPLAY_LABELS = {
    "gspt1_wt_cc90009_present": "GSPT1 WT\nwith CC-90009",
    "gspt1_wt_cc90009_absent": "GSPT1 WT\nwithout CC-90009",
    "gspt1_g575n_cc90009_present": "GSPT1 G575N\nwith CC-90009",
    "gspt1_randomized_cc90009_present": "Randomized GSPT1\nwith CC-90009",
}


def validate_panel_b_rows(frame: pd.DataFrame, protocol: dict) -> None:
    """Validate a complete, balanced, protocol-matched Panel B table."""
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Panel B input is missing columns: {missing}")
    observed_conditions = set(frame["condition_id"].astype(str))
    expected_conditions = set(REQUIRED_CONDITIONS)
    if observed_conditions != expected_conditions:
        raise ValueError(
            "Panel B condition arms do not match the required set: "
            f"missing={sorted(expected_conditions - observed_conditions)}, "
            f"extra={sorted(observed_conditions - expected_conditions)}"
        )
    for row in frame.loc[:, REQUIRED_COLUMNS].to_dict(orient="records"):
        validate_protocol_record(row, protocol)

    counts = frame.groupby("condition_id", sort=False).size().to_dict()
    expected_n = int(protocol.get("replicates", {}).get("gspt1_models_per_arm", 0))
    if expected_n <= 0:
        raise ValueError("Protocol must define a positive gspt1_models_per_arm")
    if any(int(counts.get(condition, 0)) != expected_n for condition in REQUIRED_CONDITIONS):
        raise ValueError(
            f"Panel B replicate counts must equal {expected_n} in every arm; observed={counts}"
        )
    for condition, group in frame.groupby("condition_id", sort=False):
        if group["seed"].astype(str).duplicated().any():
            raise ValueError(f"Panel B arm {condition} contains a duplicate seed")
    similarities = pd.to_numeric(frame["jaccard_similarity"], errors="coerce")
    if similarities.isna().any() or not np.isfinite(similarities).all():
        raise ValueError("jaccard_similarity must contain finite numeric values")
    if ((similarities < 0.0) | (similarities > 1.0)).any():
        raise ValueError("jaccard_similarity must be between 0 and 1")


def calculate_panel_b_statistics(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate the two prespecified one-sided Mann-Whitney comparisons."""
    values = {
        condition: pd.to_numeric(
            frame.loc[frame["condition_id"] == condition, "jaccard_similarity"]
        ).to_numpy(dtype=float)
        for condition in REQUIRED_CONDITIONS
    }
    positive_id = "gspt1_wt_cc90009_present"
    comparisons = (
        ("wt_ccplus_vs_wt_ccminus", "gspt1_wt_cc90009_absent"),
        ("wt_ccplus_vs_g575n_ccplus", "gspt1_g575n_cc90009_present"),
    )
    rows = []
    for comparison_id, comparator_id in comparisons:
        result = mannwhitneyu(
            values[positive_id], values[comparator_id], alternative="greater"
        )
        rows.append(
            {
                "comparison_id": comparison_id,
                "group_1": positive_id,
                "group_2": comparator_id,
                "alternative": "greater",
                "n_group_1": len(values[positive_id]),
                "n_group_2": len(values[comparator_id]),
                "mannwhitney_u": float(result.statistic),
                "mannwhitney_p": float(result.pvalue),
            }
        )
    return pd.DataFrame(rows)


def build_panel_b_figure(frame: pd.DataFrame):
    """Build the four-arm Jaccard box plot without writing it."""
    ordered = [
        pd.to_numeric(
            frame.loc[frame["condition_id"] == condition, "jaccard_similarity"]
        ).to_numpy(dtype=float)
        for condition in REQUIRED_CONDITIONS
    ]
    figure, axis = plt.subplots(figsize=(8.4, 5.8))
    box = axis.boxplot(
        ordered,
        tick_labels=[DISPLAY_LABELS[condition] for condition in REQUIRED_CONDITIONS],
        patch_artist=True,
        showmeans=True,
        meanprops={
            "marker": "^",
            "markerfacecolor": "#2E8B57",
            "markeredgecolor": "#2E8B57",
            "markersize": 7,
        },
        medianprops={"color": "#111111", "linewidth": 1.6},
        whiskerprops={"color": "#555555", "linewidth": 1.2},
        capprops={"color": "#555555", "linewidth": 1.2},
        flierprops={"marker": ""},
    )
    for index, patch in enumerate(box["boxes"]):
        patch.set_facecolor("#A9D6E5" if index == 0 else "#D0D0D0")
        patch.set_edgecolor("#333333")
        patch.set_alpha(0.9)
    for position, group_values in enumerate(ordered, start=1):
        jitter = np.linspace(-0.16, 0.16, len(group_values)) if len(group_values) > 1 else [0.0]
        point_colors = ["#B22222" if value > 0.7 else "#666666" for value in group_values]
        axis.scatter(
            position + np.asarray(jitter),
            group_values,
            c=point_colors,
            s=24,
            edgecolors="white",
            linewidths=0.35,
            zorder=4,
        )
    axis.set_ylabel("CRBN-interface Jaccard similarity")
    axis.set_ylim(-0.03, 1.03)
    axis.grid(False)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_linewidth(1.4)
    figure.tight_layout()
    return figure


def render_panel_b(frame: pd.DataFrame, output_path: Path, *, dpi: int = 300) -> Path:
    """Write the Panel B PNG and close its Matplotlib figure."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure = build_panel_b_figure(frame)
    try:
        figure.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    finally:
        plt.close(figure)
    return output_path


def run_panel_b(
    input_csv: Path, protocol_json: Path, output_dir: Path
) -> dict[str, Path]:
    """Validate matched data and write Panel B statistics and figure."""
    protocol = load_protocol(protocol_json)
    frame = pd.read_csv(input_csv)
    validate_panel_b_rows(frame, protocol)
    output_dir.mkdir(parents=True, exist_ok=True)
    statistics_path = output_dir / "panel_b_mannwhitney_tests.csv"
    figure_path = output_dir / "panel_b_native_jaccard_boxplot.png"
    calculate_panel_b_statistics(frame).to_csv(statistics_path, index=False)
    render_panel_b(frame, figure_path)
    return {"statistics": statistics_path, "figure": figure_path}
