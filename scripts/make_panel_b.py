#!/usr/bin/env python3
"""Generate Figure Panel B from protocol-matched GSPT1 model metrics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from analysis.panel_b import run_panel_b


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=PACKAGE_ROOT / "data" / "processed" / "panel_b_gspt1_matched_schema.csv",
    )
    parser.add_argument(
        "--protocol",
        type=Path,
        default=PACKAGE_ROOT / "config" / "rf3_protocol.json",
    )
    parser.add_argument("--output-dir", type=Path, default=PACKAGE_ROOT / "figures")
    args = parser.parse_args()
    outputs = run_panel_b(args.input, args.protocol, args.output_dir)
    for name, path in outputs.items():
        print(f"{name}={path.resolve()}")


if __name__ == "__main__":
    main()
