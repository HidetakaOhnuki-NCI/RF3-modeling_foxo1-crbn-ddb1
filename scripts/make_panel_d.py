#!/usr/bin/env python3
"""Generate Figure Panel D from FOXO1 541-580 CRBN-residue counts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from analysis.panel_d import render_panel_d


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=PACKAGE_ROOT / "data" / "processed" / "panel_d_crbn_541_580_contacts.csv",
    )
    parser.add_argument(
        "--output", type=Path, default=PACKAGE_ROOT / "figures" / "panel_d_crbn_541_580_contacts.png"
    )
    args = parser.parse_args()
    print(f"figure={render_panel_d(args.input, args.output).resolve()}")


if __name__ == "__main__":
    main()
