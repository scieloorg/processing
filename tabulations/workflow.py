import json
import socket
import sys
import time
import urllib.error
import urllib.request

from tabulations.constants import DEFAULT_ACRONYMS


class SlackNotifier:
    def __init__(self, webhook_url, logger):
        self.webhook_url = webhook_url
        self.logger = logger

    def send(self, message):
        """Envia uma notificação sem transformar falhas de rede em erros fatais."""
        if not self.webhook_url:
            return

        request = urllib.request.Request(
            self.webhook_url,
            data=json.dumps({"text": message}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=10):
                pass
        except (OSError, urllib.error.URLError) as error:
            self.logger.warning(
                "Falha ao enviar notificação ao Slack: %s",
                error,
            )


class Workflow:
    def __init__(
        self,
        config,
        state_store,
        collection_processor,
        artifact_publisher,
        notifier,
        logger,
    ):
        self.config = config
        self.state_store = state_store
        self.collection_processor = collection_processor
        self.artifact_publisher = artifact_publisher
        self.notifier = notifier
        self.logger = logger
        self.started_at = time.monotonic()

    def run(self, requested):
        """Processa as coleções solicitadas e retorna o código de saída final."""
        network_mode = not requested
        collections = self._collections_to_process(requested)

        if network_mode:
            self.artifact_publisher.prepare_network()

        self._log_start(collections, network_mode)
        failed = self._process_collections(collections, network_mode)

        if network_mode and not failed:
            try:
                self.artifact_publisher.publish_network()
            except (OSError, RuntimeError) as error:
                self.logger.error("REDE falhou motivo=%s", error)
                failed.append("network")
        elif network_mode:
            self.logger.error(
                "REDE não_publicada motivo=coleções_com_falha "
                "arquivo_anterior=preservado"
            )

        self.state_store.save_pending(item for item in failed if item != "network")

        if failed:
            return self._finish_with_failures(collections, failed)

        self.state_store.clear_collections(collections)
        self.artifact_publisher.clear_network()
        return self._finish_successfully(collections)

    def _collections_to_process(self, requested):
        collections = list(requested or DEFAULT_ACRONYMS)
        pending = self.state_store.load_pending()

        if pending:
            self.logger.info(
                "RETOMADA coleções_pendentes=%s",
                ",".join(pending),
            )
            collections = list(dict.fromkeys((*pending, *collections)))

        return collections

    def _process_collections(self, collections, network_mode):
        failed = []

        for position, item in enumerate(collections, 1):
            self.logger.info(
                "PROGRESSO coleção=%s posição=%d/%d",
                item,
                position,
                len(collections),
            )

            try:
                succeeded = self.collection_processor.process(
                    item,
                    network_mode,
                )
            except Exception:
                self.logger.exception(
                    "COLEÇÃO falhou=%s motivo=erro_inesperado; "
                    "o processamento continuará",
                    item,
                )
                succeeded = False

            if not succeeded:
                failed.append(item)

        return failed

    def _log_start(self, collections, network_mode):
        self.logger.info(
            "PROCESSAMENTO início host=%s python=%s coleções=%d rede=%s "
            "checkpoints=%s",
            socket.gethostname(),
            sys.version.split()[0],
            len(collections),
            network_mode,
            self.config.checkpoint_dir,
        )
        self.notifier.send(
            f":hourglass_flowing_sand: Processing iniciado em "
            f"`{socket.gethostname()}`."
        )

    def _finish_with_failures(self, collections, failed):
        duration = time.monotonic() - self.started_at
        self.logger.error(
            "PROCESSAMENTO concluído_com_falhas=%d/%d itens=%s duração=%.1fs "
            "fila=%s",
            len(failed),
            len(collections),
            ",".join(failed),
            duration,
            self.config.failed_collections_file,
        )
        self.notifier.send(
            f":x: Processing finalizado com falhas ({len(failed)}/"
            f"{len(collections)}) em {duration:.0f}s. "
            f"Itens: {', '.join(failed)}."
        )
        return 1 if self.config.exit_on_failure else 0

    def _finish_successfully(self, collections):
        duration = time.monotonic() - self.started_at
        self.logger.info(
            "PROCESSAMENTO sucesso coleções=%d duração=%.1fs arquivos=%s",
            len(collections),
            duration,
            self.config.tabs_dir,
        )
        self.notifier.send(
            f":white_check_mark: Processing finalizado com sucesso. "
            f"Coleções: {len(collections)}. Tempo: {duration:.0f}s."
        )
        return 0
