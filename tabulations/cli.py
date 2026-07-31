import argparse
import logging
import os
import sys
from datetime import date, datetime

from tabulations.artifacts import ArtifactPublisher
from tabulations.collection import CollectionProcessor
from tabulations.commands import CommandExecutor
from tabulations.config import Config
from tabulations.state import StateStore
from tabulations.workflow import SlackNotifier, Workflow


def _configure_logger(config, run_id):
    master_log = config.log_dir / f"master_{run_id}.log"
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)

    file_handler = logging.FileHandler(master_log, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(f"tabulations.{run_id}")
    logger.handlers[:] = [console, file_handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    return logger


def main(arguments=None, environment=None):
    """Configura e executa as tabulações, retornando um código de saída."""
    parser = argparse.ArgumentParser(
        description="Gera tabulações SciELO com logs e retomada por etapa."
    )
    parser.add_argument("collections", nargs="*", metavar="COLEÇÃO")
    parsed = parser.parse_args(arguments)
    requested = [
        collection for argument in parsed.collections for collection in argument.split()
    ]

    try:
        config = Config(environment)
        config.validate()

        if config.processing_settings_file:
            os.environ["PROCESSING_SETTINGS_FILE"] = config.processing_settings_file

        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_date = date.today().isoformat()
        logger = _configure_logger(config, run_id)
        state_store = StateStore(
            config.checkpoint_dir,
            config.failed_collections_file,
        )
        notifier = SlackNotifier(config.slack_webhook_url, logger)
        artifacts = ArtifactPublisher(config, logger, report_date)
        commands = CommandExecutor(
            config,
            state_store,
            logger,
            report_date,
        )
        collection_processor = CollectionProcessor(
            state_store,
            commands,
            artifacts,
            notifier,
            logger,
            report_date,
        )
        workflow = Workflow(
            config,
            state_store,
            collection_processor,
            artifacts,
            notifier,
            logger,
        )

        return workflow.run(requested)
    except (OSError, RuntimeError, ValueError) as error:
        print(
            f"processing_tabs: erro de configuração: {error}",
            file=sys.stderr,
        )
        return 2
