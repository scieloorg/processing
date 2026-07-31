import tempfile
import unittest
from pathlib import Path
from unittest.mock import ANY, Mock, patch

from tabulations.commands import CommandExecutor, _execute
from tests.tabulations.fixtures import make_config


class CommandExecutorTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.config = make_config(self.root)
        self.state_store = Mock()
        self.state_store.is_completed.return_value = False
        self.state_store.outputs_valid.return_value = True
        self.logger = Mock()
        self.executor = CommandExecutor(
            self.config,
            self.state_store,
            self.logger,
            "2026-07-30",
        )
        self.work_dir = self.root / "work"
        self.work_dir.mkdir()
        self.state_path = self.work_dir / "state.json"
        self.state = {"steps": {}}

    def _run_command(self, data_outputs=()):
        return self.executor.run(
            "arg-AR",
            "publication_all",
            "processing_publication_all",
            "arg",
            self.work_dir,
            self.state_path,
            self.state,
            ("result.csv",),
            data_outputs=data_outputs,
        )

    def test_marks_success_without_writing_stdout_to_command_log(self):
        command_log = self.config.log_dir / "publication_all_arg-AR.log"
        command_log.write_text("command-owned\n", encoding="utf-8")

        def run_process(*args):
            (self.work_dir / "result.csv").write_text(
                "header\nvalue\n",
                encoding="utf-8",
            )
            return 0

        with patch(
            "tabulations.commands._execute",
            side_effect=run_process,
        ):
            result = self._run_command()

        self.assertTrue(result)
        self.state_store.mark_completed.assert_called_once()
        self.state_store.mark_failed.assert_not_called()
        self.assertEqual(
            command_log.read_text(encoding="utf-8"),
            "command-owned\n",
        )

    def test_retries_until_output_is_valid(self):
        self.config.max_retries = 2
        self.config.retry_delay = 3

        def run_process(*args):
            if run_process.calls:
                (self.work_dir / "result.csv").write_text(
                    "value\n",
                    encoding="utf-8",
                )
                return 0

            run_process.calls += 1
            return 1

        run_process.calls = 0

        with (
            patch(
                "tabulations.commands._execute",
                side_effect=run_process,
            ) as command,
            patch("tabulations.commands.time.sleep") as sleep,
        ):
            result = self._run_command()

        self.assertTrue(result)
        self.assertEqual(command.call_count, 2)
        sleep.assert_called_once_with(3)

    def test_exit_zero_with_invalid_output_is_failure(self):
        self.state_store.outputs_valid.return_value = False

        with patch("tabulations.commands._execute", return_value=0):
            result = self._run_command(("result.csv",))

        self.assertFalse(result)
        self.state_store.mark_completed.assert_not_called()
        self.state_store.outputs_valid.assert_called_once_with(
            self.work_dir,
            ("result.csv",),
            ("result.csv",),
        )
        self.state_store.mark_failed.assert_called_once()

    def test_skips_process_for_valid_checkpoint(self):
        self.state_store.is_completed.return_value = True

        with patch("tabulations.commands._execute") as command:
            result = self._run_command()

        self.assertTrue(result)
        command.assert_not_called()
        self.state_store.mark_completed.assert_not_called()


class ProcessTest(unittest.TestCase):
    def test_streams_stdout_to_logger(self):
        process = Mock(stdout=("generated row\n", "\n"))
        process.wait.return_value = 0
        logger = Mock()

        with patch(
            "tabulations.commands.subprocess.Popen",
            return_value=process,
        ):
            result = _execute(["processing_publication_all"], "/tmp", logger)

        self.assertEqual(result, 0)
        logger.info.assert_called_once_with(
            "SAÍDA comando=%s mensagem=%s",
            "processing_publication_all",
            "generated row",
        )

    def test_returns_spawn_error_without_raising(self):
        logger = Mock()

        with patch(
            "tabulations.commands.subprocess.Popen",
            side_effect=OSError("missing"),
        ):
            result = _execute(["missing-command"], "/tmp", logger)

        self.assertEqual(result, 127)
        logger.error.assert_called_once_with(
            "Não foi possível iniciar %s: %s",
            "missing-command",
            ANY,
        )
