# coding: utf-8
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from zipfile import ZipFile


CSV_FILES = [
    "documents_affiliations.csv",
    "documents_affiliation_nationality.csv",
    "documents_authors.csv",
    "documents_counts.csv",
    "documents_dates.csv",
    "documents_languages.csv",
    "documents_licenses.csv",
    "journals.csv",
    "journals_status_changes.csv",
]


MOCK_PROCESSING = """#!/bin/bash
command_name="$(basename "$0")"
collection=""
output_file=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -c)
            collection="$2"
            shift 2
            ;;
        -r)
            output_file="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

if [[ "$collection" == "scl" ]]; then
    exit 1
fi

case "$command_name" in
    processing_publication_all)
        for csv in \
            documents_affiliations \
            documents_affiliation_nationality \
            documents_authors \
            documents_counts \
            documents_dates \
            documents_languages \
            documents_licenses
        do
            printf 'column_a,column_b\\n%s,data\\n' "$collection" > "${csv}.csv"
        done
        ;;
    processing_publication_journals|\
    processing_publication_journals_status_changes|\
    processing_export_kbart)
        printf 'column_a,column_b\\n%s,data\\n' "$collection" > "$output_file"
        ;;
esac
"""


class RunShTest(unittest.TestCase):

    def test_network_csv_files_keep_one_header_when_first_collection_fails(self):
        repository_dir = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as temporary_directory:
            work_dir = Path(temporary_directory)
            bin_dir = work_dir / "bin"
            log_dir = work_dir / "logs"
            tabs_dir = work_dir / "tabs"
            bin_dir.mkdir()
            log_dir.mkdir()
            tabs_dir.mkdir()

            mock_processing = bin_dir / "mock-processing"
            mock_processing.write_text(MOCK_PROCESSING, encoding="utf-8")
            mock_processing.chmod(0o755)

            command_names = [
                "processing_publication_all",
                "processing_publication_journals",
                "processing_publication_journals_status_changes",
                "processing_export_kbart",
            ]
            for command_name in command_names:
                (bin_dir / command_name).symlink_to(mock_processing)

            environment = os.environ.copy()
            environment.update(
                {
                    "PATH": f"{bin_dir}{os.pathsep}{environment['PATH']}",
                    "DOCKER_ENV": "1",
                    "PROCESSING_SETTINGS_FILE": "",
                    "WORK_DIR": str(work_dir),
                    "LOG_DIR": str(log_dir),
                    "TABS_DIR": str(tabs_dir),
                    "MAX_RETRIES": "1",
                    "RETRY_DELAY": "0",
                    "EXIT_ON_FAILURE": "false",
                    "SLACK_WEBHOOK_URL": "",
                }
            )

            subprocess.run(
                ["bash", str(repository_dir / "run.sh")],
                cwd=repository_dir,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )

            with ZipFile(tabs_dir / "tabs_network.zip") as network_zip:
                names = network_zip.namelist()
                self.assertEqual(len(names), len(CSV_FILES) + 1)
                self.assertTrue(set(CSV_FILES).issubset(names))

                for name in names:
                    lines = network_zip.read(name).decode("utf-8").splitlines()
                    self.assertEqual(
                        lines[0],
                        "column_a,column_b",
                        f"{name} não preservou o cabeçalho",
                    )
                    self.assertEqual(
                        lines.count("column_a,column_b"),
                        1,
                        f"{name} contém cabeçalhos duplicados",
                    )


if __name__ == "__main__":
    unittest.main()
