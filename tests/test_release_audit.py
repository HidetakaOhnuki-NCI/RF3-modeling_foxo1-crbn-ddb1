from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

try:
    from analysis.release_audit import (
        audit_release,
        find_private_path_hits,
        verify_checksums,
        write_checksums,
    )
except ImportError:
    audit_release = None
    find_private_path_hits = None
    verify_checksums = None
    write_checksums = None


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class PrivatePathTests(unittest.TestCase):
    def require_implementation(self) -> None:
        self.assertIsNotNone(find_private_path_hits, "release audit is not implemented")

    def test_detects_drive_unc_username_hostname_and_job_path(self):
        self.require_implementation()
        slash = chr(92)
        cases = {
            "drive.txt": "input=" + "A" + ":" + slash + "private" + slash + "model.cif",
            "unc.md": "source=" + (slash * 2) + "server" + slash + "share" + slash + "model.cif",
            "user.py": "owner='" + "ohnu" + "kih'",
            "host.txt": "host=" + "hpc" + "drive" + ".nih.gov",
            "job.md": "source " + "job" + "_" + "26344291",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, content in cases.items():
                (root / name).write_text(content, encoding="utf-8")
            hits = find_private_path_hits(root)
            self.assertEqual({hit["file"] for hit in hits}, set(cases))

    def test_allows_relative_paths_identifiers_and_public_urls(self):
        self.require_implementation()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "safe.md").write_text(
                "data/processed/table.csv PDB 6XK9 https://www.rcsb.org/structure/6XK9",
                encoding="utf-8",
            )
            self.assertEqual(find_private_path_hits(root), [])


class ChecksumTests(unittest.TestCase):
    def require_implementation(self) -> None:
        self.assertIsNotNone(write_checksums, "checksum writer is not implemented")
        self.assertIsNotNone(verify_checksums, "checksum verifier is not implemented")

    def test_checksum_verifier_detects_mutation(self):
        self.require_implementation()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "data.txt"
            target.write_text("original\n", encoding="utf-8")
            checksum_path = write_checksums(root)
            self.assertEqual(verify_checksums(root, checksum_path), [])
            target.write_text("changed\n", encoding="utf-8")
            errors = verify_checksums(root, checksum_path)
            self.assertEqual(len(errors), 1)
            self.assertIn("data.txt", errors[0])

    def test_checksum_writer_excludes_git_metadata(self):
        self.require_implementation()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "data.txt").write_text("content\n", encoding="utf-8")
            git_dir = root / ".git"
            git_dir.mkdir()
            (git_dir / "config").write_text("private metadata\n", encoding="utf-8")
            checksum_path = write_checksums(root)
            checksum_text = checksum_path.read_text(encoding="utf-8")
            self.assertIn("data.txt", checksum_text)
            self.assertNotIn(".git", checksum_text)


class ActualPackageTests(unittest.TestCase):
    def require_implementation(self) -> None:
        self.assertIsNotNone(audit_release, "release audit is not implemented")

    def test_package_passes_nonchecksum_release_checks(self):
        self.require_implementation()
        report = audit_release(PACKAGE_ROOT, verify_checksum_file=False)
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["panel_c_rows"], 1310)
        self.assertEqual(report["panel_d_rows"], 397)
        self.assertEqual(report["private_path_hits"], [])


if __name__ == "__main__":
    unittest.main()
