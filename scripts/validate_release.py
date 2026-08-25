#!/usr/bin/env python3
"""Validate the public RF3 package and optionally refresh SHA-256 checksums."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

from analysis.release_audit import audit_release, write_checksums


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-checksums", action="store_true")
    args = parser.parse_args()
    if args.write_checksums:
        write_checksums(PACKAGE_ROOT)
    report = audit_release(PACKAGE_ROOT, verify_checksum_file=True)
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
