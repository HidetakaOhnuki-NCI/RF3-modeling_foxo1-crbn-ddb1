"""Audit the public package for reproducibility, integrity, and path safety."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from analysis.config import load_protocol
from analysis.panel_c import load_panel_c_counts
from analysis.panel_d import load_panel_d_counts


CHECKSUM_FILENAME = "SHA256SUMS.txt"
TEXT_EXTENSIONS = {
    ".cxc",
    ".csv",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
PRIVATE_PATTERNS = {
    "windows_drive_path": re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]"),
    "unc_path": re.compile(r"\\\\[A-Za-z0-9._-]+[\\/]"),
    "username": re.compile(r"\b" + "ohnu" + "kih" + r"\b", re.IGNORECASE),
    "internal_hostname": re.compile(
        r"\b(?:hpcdrive|nciis-[A-Za-z0-9-]+)\.nih\.gov\b", re.IGNORECASE
    ),
    "private_job_id": re.compile(r"\bjob[_ -]?\d{6,}\b", re.IGNORECASE),
}
REQUIRED_FILES = (
    "README.md",
    "requirements.txt",
    "config/rf3_protocol.json",
    "analysis/config.py",
    "analysis/statistics.py",
    "analysis/panel_b.py",
    "analysis/panel_c.py",
    "analysis/panel_d.py",
    "analysis/release_audit.py",
    "scripts/make_panel_b.py",
    "scripts/make_panel_c.py",
    "scripts/make_panel_d.py",
    "scripts/validate_release.py",
    "chimerax/panel_a_interface.cxc",
    "docs/METHODS.md",
    "docs/WORKFLOW.md",
    "docs/DATA_DICTIONARY.md",
    "docs/REPRODUCIBILITY.md",
    "data/processed/panel_b_gspt1_matched_schema.csv",
    "data/processed/panel_c_foxo1_residue_contacts.csv",
    "data/processed/panel_d_crbn_541_580_contacts.csv",
    "data/processed/PROVENANCE.json",
    "data/manifests/raw_model_manifest_schema.csv",
    "figures/panel_c_foxo1_residue_contacts.png",
    "figures/panel_d_crbn_541_580_contacts.png",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _release_files(root: Path, *, include_checksum: bool = False) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts
        if ".git" in relative_parts or "__pycache__" in relative_parts or path.suffix == ".pyc":
            continue
        if not include_checksum and path.name == CHECKSUM_FILENAME:
            continue
        files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def find_private_path_hits(root: Path) -> list[dict[str, object]]:
    """Return private path or identifier patterns found in public text files."""
    hits: list[dict[str, object]] = []
    for path in _release_files(root, include_checksum=True):
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            hits.append(
                {
                    "file": path.relative_to(root).as_posix(),
                    "line": 0,
                    "pattern": "invalid_utf8",
                }
            )
            continue
        for line_number, line in enumerate(lines, start=1):
            for name, pattern in PRIVATE_PATTERNS.items():
                if pattern.search(line):
                    hits.append(
                        {
                            "file": path.relative_to(root).as_posix(),
                            "line": line_number,
                            "pattern": name,
                        }
                    )
    return hits


def write_checksums(root: Path) -> Path:
    """Write deterministic SHA-256 entries for all release files except itself."""
    output = root / CHECKSUM_FILENAME
    lines = [
        f"{sha256(path)}  {path.relative_to(root).as_posix()}"
        for path in _release_files(root)
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def verify_checksums(root: Path, checksum_path: Path | None = None) -> list[str]:
    """Return missing, malformed, or mismatched checksum errors."""
    checksum_path = checksum_path or root / CHECKSUM_FILENAME
    if not checksum_path.is_file():
        return [f"Missing checksum file: {CHECKSUM_FILENAME}"]
    errors: list[str] = []
    seen: set[str] = set()
    for line_number, line in enumerate(
        checksum_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        parts = line.split("  ", maxsplit=1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9A-Fa-f]{64}", parts[0]):
            errors.append(f"Malformed checksum line {line_number}")
            continue
        expected, relative = parts[0].upper(), parts[1]
        seen.add(relative)
        target = root / Path(relative)
        if not target.is_file():
            errors.append(f"Missing checksummed file: {relative}")
        elif sha256(target) != expected:
            errors.append(f"Checksum mismatch: {relative}")
    expected_paths = {
        path.relative_to(root).as_posix() for path in _release_files(root)
    }
    for missing in sorted(expected_paths - seen):
        errors.append(f"File absent from checksum manifest: {missing}")
    for extra in sorted(seen - expected_paths):
        errors.append(f"Checksum manifest contains unexpected file: {extra}")
    return errors


def audit_release(root: Path, *, verify_checksum_file: bool = True) -> dict[str, object]:
    """Run all public-release checks and return a JSON-serializable report."""
    errors: list[str] = []
    missing_files = [relative for relative in REQUIRED_FILES if not (root / relative).is_file()]
    errors.extend(f"Missing required file: {relative}" for relative in missing_files)

    protocol = load_protocol(root / "config" / "rf3_protocol.json")
    inference = protocol["inference"]
    expected_inference = {"num_steps": 200, "n_recycles": 10, "diffusion_batch_size": 1}
    if {key: inference.get(key) for key in expected_inference} != expected_inference:
        errors.append("RF3 protocol is not exactly 200 steps, 10 recycles, batch size 1")

    panel_c_rows = 0
    panel_d_rows = 0
    try:
        panel_c_rows = len(
            load_panel_c_counts(root / "data" / "processed" / "panel_c_foxo1_residue_contacts.csv")
        )
    except (OSError, ValueError) as exc:
        errors.append(f"Panel C data validation failed: {exc}")
    try:
        panel_d_rows = len(
            load_panel_d_counts(root / "data" / "processed" / "panel_d_crbn_541_580_contacts.csv")
        )
    except (OSError, ValueError) as exc:
        errors.append(f"Panel D data validation failed: {exc}")

    provenance_path = root / "data" / "processed" / "PROVENANCE.json"
    if provenance_path.is_file():
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        for filename in (
            "panel_c_foxo1_residue_contacts.csv",
            "panel_d_crbn_541_580_contacts.csv",
        ):
            target = provenance_path.parent / filename
            expected = provenance.get(filename, {}).get("shared_sha256", "").upper()
            if not expected or not target.is_file() or sha256(target) != expected:
                errors.append(f"Processed-data provenance mismatch: {filename}")
    else:
        errors.append("Missing processed-data provenance")

    private_hits = find_private_path_hits(root)
    errors.extend(
        f"Private pattern {hit['pattern']} in {hit['file']}:{hit['line']}"
        for hit in private_hits
    )

    checksum_errors = verify_checksums(root) if verify_checksum_file else []
    errors.extend(checksum_errors)
    return {
        "ok": not errors,
        "errors": errors,
        "required_file_count": len(REQUIRED_FILES),
        "missing_files": missing_files,
        "panel_c_rows": panel_c_rows,
        "panel_d_rows": panel_d_rows,
        "private_path_hits": private_hits,
        "checksum_errors": checksum_errors,
    }
