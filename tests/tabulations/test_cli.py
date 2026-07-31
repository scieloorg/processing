import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

from tabulations.cli import main
from tests.tabulations.fixtures import make_config


class CliTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)

    def test_splits_grouped_and_separate_collection_arguments(self):
        config = make_config(self.root)
        config.validate = Mock()
        config.processing_settings_file = ""
        config.slack_webhook_url = ""
        config_factory = Mock(return_value=config)
        workflow = Mock()
        workflow.run.return_value = 9
        workflow_factory = Mock(return_value=workflow)
        dependencies = {
            "Config": config_factory,
            "_configure_logger": Mock(return_value=Mock()),
            "StateStore": Mock(),
            "SlackNotifier": Mock(),
            "ArtifactPublisher": Mock(),
            "CommandExecutor": Mock(),
            "CollectionProcessor": Mock(),
            "Workflow": workflow_factory,
        }
        environment = {"DOCKER_ENV": "1"}

        with patch.multiple("tabulations.cli", **dependencies):
            result = main(
                ["arg-AR bol-BO", "mex-MX", "per-PE ury-UY"],
                environment,
            )

        self.assertEqual(result, 9)
        config_factory.assert_called_once_with(environment)
        config.validate.assert_called_once_with()
        workflow.run.assert_called_once_with(
            ["arg-AR", "bol-BO", "mex-MX", "per-PE", "ury-UY"],
        )

    def test_configuration_error_returns_two(self):
        error_output = StringIO()

        with (
            patch(
                "tabulations.cli.Config",
                side_effect=ValueError("MAX_RETRIES inválido"),
            ),
            redirect_stderr(error_output),
        ):
            result = main([], {})

        self.assertEqual(result, 2)
        self.assertIn(
            "processing_tabs: erro de configuração: MAX_RETRIES inválido",
            error_output.getvalue(),
        )
