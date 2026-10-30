import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from zipfile import ZipFile

from tabulations.artifacts import ArtifactPublisher
from tabulations.constants import CSV_FILES, KBART_LEGACY_FILENAME, KBART_TEMPLATE


class ArtifactPublisherTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.config = SimpleNamespace(
            checkpoint_dir=self.root / "checkpoints",
            tabs_dir=self.root / "tabs",
        )
        self.publisher = ArtifactPublisher(
            self.config,
            Mock(),
            "2026-07-30",
        )

    def _write_collection(self, acronym, value):
        work_dir = self.root / acronym
        work_dir.mkdir()
        kbart_file = KBART_TEMPLATE.format(
            acronym=acronym,
            date="2026-07-30",
        )

        for name in (*CSV_FILES, kbart_file):
            content = f"column_a,column_b\n{value},data\n"
            (work_dir / name).write_text(content, encoding="utf-8")

        return work_dir, kbart_file

    def test_rejects_collection_with_missing_required_file(self):
        work_dir, kbart_file = self._write_collection("arg", "arg")
        missing = work_dir / CSV_FILES[0]
        missing.unlink()

        with self.assertRaisesRegex(RuntimeError, missing.name):
            self.publisher.publish_collection(
                work_dir,
                "arg",
                kbart_file,
                False,
            )

        self.assertFalse((work_dir / "tabs_arg.zip").exists())

    def test_collection_archive_has_exact_required_members(self):
        work_dir, kbart_file = self._write_collection("arg", "arg")

        archive = self.publisher.publish_collection(
            work_dir,
            "arg",
            kbart_file,
            False,
        )

        with ZipFile(archive) as zip_file:
            self.assertEqual(
                zip_file.namelist(),
                [*CSV_FILES, kbart_file, KBART_LEGACY_FILENAME],
            )
            self.assertEqual(
                zip_file.read(KBART_LEGACY_FILENAME),
                zip_file.read(kbart_file),
            )

    def test_collection_archive_is_copied_to_tabs_directory(self):
        work_dir, kbart_file = self._write_collection("arg", "arg")

        archive = self.publisher.publish_collection(
            work_dir,
            "arg",
            kbart_file,
            False,
        )
        published = self.config.tabs_dir / archive.name

        self.assertEqual(published.read_bytes(), archive.read_bytes())
        self.assertFalse((self.config.tabs_dir / "tabs_arg.zip.tmp").exists())

    def test_network_merge_keeps_only_first_header(self):
        self.publisher.prepare_network()
        first_dir, first_kbart = self._write_collection("arg", "arg")
        second_dir, second_kbart = self._write_collection("bol", "bol")

        self.publisher.publish_collection(first_dir, "arg", first_kbart, True)
        self.publisher.publish_collection(second_dir, "bol", second_kbart, True)
        archive = self.publisher.publish_network()
        network_kbart = KBART_TEMPLATE.format(
            acronym="network",
            date="2026-07-30",
        )

        with ZipFile(archive) as zip_file:
            self.assertEqual(
                zip_file.namelist(),
                [*CSV_FILES, network_kbart],
            )

            for name in zip_file.namelist():
                lines = zip_file.read(name).decode("utf-8").splitlines()
                self.assertEqual(
                    lines,
                    ["column_a,column_b", "arg,data", "bol,data"],
                )

        published = self.config.tabs_dir / "tabs_network.zip"
        self.assertEqual(published.read_bytes(), archive.read_bytes())

    def test_network_publish_rejects_empty_directory(self):
        self.publisher.prepare_network()

        with self.assertRaisesRegex(RuntimeError, "nenhum arquivo"):
            self.publisher.publish_network()

    def test_clear_network_removes_aggregation_directory(self):
        self.publisher.prepare_network()
        network_dir = self.config.checkpoint_dir / "network"
        (network_dir / "partial.csv").write_text(
            "header\n",
            encoding="utf-8",
        )

        self.publisher.clear_network()

        self.assertFalse(network_dir.exists())
