import os
from pathlib import Path


def _read_bool(environment, name, default):
    value = environment.get(name)

    if value is None:
        return default

    normalized = str(value).strip().lower()

    if normalized in {"1", "true", "yes", "on"}:
        return True

    if normalized in {"0", "false", "no", "off"}:
        return False

    raise ValueError(f"{name} deve ser true/false, 1/0, yes/no ou on/off")


def _read_int(environment, name, default, minimum):
    value = environment.get(name, default)

    try:
        value = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} deve ser um número inteiro") from error

    if value < minimum:
        raise ValueError(f"{name} deve ser maior ou igual a {minimum}")

    return value


class Config:
    def __init__(self, environment=None):
        environment = os.environ if environment is None else environment
        self.docker_env = _read_bool(environment, "DOCKER_ENV", False)

        self.work_dir = Path(environment.get("WORK_DIR", "/var/www/processing"))
        self.log_dir = Path(environment.get("LOG_DIR", "/var/log/processing"))
        self.tabs_dir = Path(
            environment.get(
                "TABS_DIR",
                "/var/www/static_scielo_org/tabs",
            )
        )

        checkpoint_dir = environment.get("CHECKPOINT_DIR")
        failed_file = environment.get("FAILED_COLLECTIONS_FILE")
        settings_default = "" if self.docker_env else "/etc/scieloapps/processing.ini"

        self.checkpoint_dir = Path(
            checkpoint_dir or self.tabs_dir / ".processing-checkpoints"
        )
        self.failed_collections_file = Path(
            failed_file or self.log_dir / "failed_collections.queue"
        )
        self.processing_settings_file = environment.get(
            "PROCESSING_SETTINGS_FILE",
            settings_default,
        )
        self.max_retries = _read_int(environment, "MAX_RETRIES", 3, 1)
        self.retry_delay = _read_int(environment, "RETRY_DELAY", 5, 0)
        self.exit_on_failure = _read_bool(
            environment,
            "EXIT_ON_FAILURE",
            True,
        )
        self.slack_webhook_url = environment.get("SLACK_WEBHOOK_URL", "")

    def validate(self):
        """Cria os diretórios necessários e valida a configuração externa."""
        for directory in (
            self.work_dir,
            self.log_dir,
            self.tabs_dir,
            self.checkpoint_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

        if (
            self.processing_settings_file
            and not Path(self.processing_settings_file).is_file()
        ):
            raise RuntimeError(
                "arquivo de configuração não encontrado: "
                f"{self.processing_settings_file}"
            )

        return self
