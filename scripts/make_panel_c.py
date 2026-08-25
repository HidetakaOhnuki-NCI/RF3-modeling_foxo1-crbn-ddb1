#!/usr/bin/env python3
"""Generate Figure Panel C from the validated FOXO1-residue counts table."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from analysis.panel_c import render_panel_c


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=PACKAGE_ROOT / "data" / "processed" / "panel_c_foxo1_residue_contacts.csv",
    )
    parser.add_argument(
        "--output", type=Path, default=PACKAGE_ROOT / "figures" / "panel_c_foxo1_residue_contacts.png"
    )
    args = parser.parse_args()
    print(f"figure={render_panel_c(args.input, args.output).resolve()}")


if __name__ == "__main__":
    main()
