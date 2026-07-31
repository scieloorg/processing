import os
import sys
from types import SimpleNamespace

COMMAND_NAMES = (
    "processing_publication_all",
    "processing_publication_journals",
    "processing_publication_journals_status_changes",
    "processing_export_kbart",
)
RUNNER_CODE = """
import sys
from tabulations.cli import main

sys.exit(main())
"""
MOCK_PROCESSING = """#!/bin/bash
command_name="$(basename "$0")"
collection=""
output_file=""

if [[ -n "${COUNT_DIR:-}" ]]; then
    count_file="$COUNT_DIR/$command_name"
    count=0
    [[ -f "$count_file" ]] && count="$(< "$count_file")"
    printf '%s\\n' "$((count + 1))" > "$count_file"
fi

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

if [[ "${FAIL_EXPORT:-0}" == "1" && \
      "$command_name" == "processing_export_kbart" ]]; then
    exit 1
fi

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


def make_config(root, **overrides):
    values = {
        "checkpoint_dir": root / "checkpoints",
        "failed_collections_file": root / "failed.queue",
        "log_dir": root / "logs",
        "max_retries": 1,
        "retry_delay": 0,
        "tabs_dir": root / "tabs",
        "exit_on_failure": True,
    }
    values.update(overrides)

    for name in ("checkpoint_dir", "log_dir", "tabs_dir"):
        values[name].mkdir(parents=True, exist_ok=True)

    return SimpleNamespace(**values)


def prepare_integration(root, **overrides):
    bin_dir = root / "bin"
    log_dir = root / "logs"
    tabs_dir = root / "tabs"

    for directory in (bin_dir, log_dir, tabs_dir):
        directory.mkdir()

    mock_processing = bin_dir / "mock-processing"
    mock_processing.write_text(MOCK_PROCESSING, encoding="utf-8")
    mock_processing.chmod(0o755)

    for command_name in COMMAND_NAMES:
        (bin_dir / command_name).symlink_to(mock_processing)

    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{bin_dir}{os.pathsep}{environment['PATH']}",
            "DOCKER_ENV": "1",
            "PROCESSING_SETTINGS_FILE": "",
            "WORK_DIR": str(root),
            "LOG_DIR": str(log_dir),
            "TABS_DIR": str(tabs_dir),
            "MAX_RETRIES": "1",
            "RETRY_DELAY": "0",
            "EXIT_ON_FAILURE": "false",
            "SLACK_WEBHOOK_URL": "",
        }
    )
    environment.update(overrides)

    return SimpleNamespace(
        command=[sys.executable, "-c", RUNNER_CODE],
        environment=environment,
        tabs_dir=tabs_dir,
    )
