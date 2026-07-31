import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.tabulations.fixtures import prepare_integration


class TabulationsIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.repository_dir = Path(__file__).resolve().parents[2]
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)

    def _run_processing(self, fixture, *collections, check=True):
        return subprocess.run(
            [*fixture.command, *collections],
            cwd=self.repository_dir,
            env=fixture.environment,
            check=check,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_network_archive_is_preserved_when_a_collection_fails(self):
        fixture = prepare_integration(self.root, EXIT_ON_FAILURE="true")
        network_archive = fixture.tabs_dir / "tabs_network.zip"
        previous_archive = b"previous complete network archive"
        network_archive.write_bytes(previous_archive)

        result = self._run_processing(fixture, check=False)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(network_archive.read_bytes(), previous_archive)
        self.assertTrue((fixture.tabs_dir / "tabs_arg.zip").is_file())

    def test_resumes_only_the_incomplete_step(self):
        count_dir = self.root / "counts"
        count_dir.mkdir()
        fixture = prepare_integration(
            self.root,
            COUNT_DIR=str(count_dir),
            FAIL_EXPORT="1",
        )

        self._run_processing(fixture, "arg-AR")
        fixture.environment["FAIL_EXPORT"] = "0"
        resumed = self._run_processing(fixture, "arg-AR")

        expected_counts = {
            "processing_publication_all": "1",
            "processing_publication_journals": "1",
            "processing_publication_journals_status_changes": "1",
            "processing_export_kbart": "2",
        }

        for command_name, expected in expected_counts.items():
            count = (count_dir / command_name).read_text().strip()
            self.assertEqual(count, expected)

        self.assertIn("checkpoint_válido", resumed.stdout)
        self.assertTrue((fixture.tabs_dir / "tabs_arg.zip").is_file())
