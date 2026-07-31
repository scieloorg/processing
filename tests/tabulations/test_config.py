import tempfile
import unittest
from pathlib import Path

from tabulations.config import Config


class ConfigTest(unittest.TestCase):
    def test_uses_runner_defaults(self):
        config = Config({})

        self.assertFalse(config.docker_env)
        self.assertEqual(config.work_dir, Path("/var/www/processing"))
        self.assertEqual(config.log_dir, Path("/var/log/processing"))
        self.assertEqual(
            config.tabs_dir,
            Path("/var/www/static_scielo_org/tabs"),
        )
        self.assertEqual(
            config.checkpoint_dir,
            config.tabs_dir / ".processing-checkpoints",
        )
        self.assertEqual(
            config.failed_collections_file,
            config.log_dir / "failed_collections.queue",
        )
        self.assertEqual(
            config.processing_settings_file,
            "/etc/scieloapps/processing.ini",
        )
        self.assertEqual(config.max_retries, 3)
        self.assertEqual(config.retry_delay, 5)
        self.assertTrue(config.exit_on_failure)
        self.assertEqual(config.slack_webhook_url, "")

    def test_applies_overrides_and_creates_directories(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            settings_file = root / "processing.ini"
            settings_file.write_text("[app]\n", encoding="utf-8")
            environment = {
                "DOCKER_ENV": "yes",
                "WORK_DIR": str(root / "work"),
                "LOG_DIR": str(root / "logs"),
                "TABS_DIR": str(root / "tabs"),
                "CHECKPOINT_DIR": str(root / "checkpoints"),
                "FAILED_COLLECTIONS_FILE": str(root / "failed.queue"),
                "PROCESSING_SETTINGS_FILE": str(settings_file),
                "MAX_RETRIES": "7",
                "RETRY_DELAY": "0",
                "EXIT_ON_FAILURE": "off",
                "SLACK_WEBHOOK_URL": "https://example.test/slack",
            }

            config = Config(environment).validate()

            self.assertTrue(config.docker_env)
            self.assertEqual(config.max_retries, 7)
            self.assertEqual(config.retry_delay, 0)
            self.assertFalse(config.exit_on_failure)
            self.assertEqual(
                config.slack_webhook_url,
                "https://example.test/slack",
            )
            self.assertEqual(
                config.failed_collections_file,
                root / "failed.queue",
            )
            for directory in (
                config.work_dir,
                config.log_dir,
                config.tabs_dir,
                config.checkpoint_dir,
            ):
                self.assertTrue(directory.is_dir())

    def test_docker_default_does_not_require_settings_file(self):
        config = Config({"DOCKER_ENV": "1"})

        self.assertEqual(config.processing_settings_file, "")

    def test_rejects_invalid_boolean_values(self):
        for name in ("DOCKER_ENV", "EXIT_ON_FAILURE"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, name):
                Config({name: "sometimes"})

    def test_rejects_invalid_integer_values(self):
        cases = (
            ({"MAX_RETRIES": "many"}, "MAX_RETRIES"),
            ({"MAX_RETRIES": "0"}, "MAX_RETRIES"),
            ({"RETRY_DELAY": "-1"}, "RETRY_DELAY"),
        )

        for environment, name in cases:
            with (
                self.subTest(name=name, value=environment[name]),
                self.assertRaisesRegex(ValueError, name),
            ):
                Config(environment)

    def test_rejects_missing_settings_file(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            config = Config(
                {
                    "DOCKER_ENV": "1",
                    "WORK_DIR": str(root / "work"),
                    "LOG_DIR": str(root / "logs"),
                    "TABS_DIR": str(root / "tabs"),
                    "PROCESSING_SETTINGS_FILE": str(root / "missing.ini"),
                }
            )

            with self.assertRaisesRegex(
                RuntimeError,
                "arquivo de configuração não encontrado",
            ):
                config.validate()
