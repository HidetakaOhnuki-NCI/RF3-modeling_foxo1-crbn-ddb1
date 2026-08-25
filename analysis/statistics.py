"""Small dependency-free statistical helpers used by multiple panels."""

from __future__ import annotations

import math
from collections.abc import Sequence
from statistics import NormalDist


def benjamini_hochberg(p_values: Sequence[float]) -> list[float]:
    """Return Benjamini-Hochberg adjusted p-values in input order."""
    values = [float(value) for value in p_values]
    if any(not math.isfinite(value) or value < 0.0 or value > 1.0 for value in values):
        raise ValueError("p-values must be finite values between 0 and 1")
    if not values:
        return []
    order = sorted(range(len(values)), key=values.__getitem__)
    adjusted = [1.0] * len(values)
    running = 1.0
    for reverse_index in range(len(order) - 1, -1, -1):
        original_index = order[reverse_index]
        rank = reverse_index + 1
        running = min(running, values[original_index] * len(values) / rank)
        adjusted[original_index] = min(1.0, running)
    return adjusted


def wilson_interval(
    successes: int, total: int, *, confidence_level: float = 0.95
) -> tuple[float, float]:
    """Return the Wilson score interval for a binomial proportion."""
    if isinstance(successes, bool) or isinstance(total, bool):
        raise ValueError("successes and total must be integers")
    if not isinstance(successes, int) or not isinstance(total, int):
        raise ValueError("successes and total must be integers")
    if total <= 0 or successes < 0 or successes > total:
        raise ValueError("Require 0 <= successes <= total and total > 0")
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must be between 0 and 1")
    z = NormalDist().inv_cdf(0.5 + confidence_level / 2.0)
    proportion = successes / total
    z2 = z * z
    denominator = 1.0 + z2 / total
    center = (proportion + z2 / (2.0 * total)) / denominator
    half_width = (
        z
        * math.sqrt(
            proportion * (1.0 - proportion) / total + z2 / (4.0 * total * total)
        )
        / denominator
    )
    return max(0.0, center - half_width), min(1.0, center + half_width)
