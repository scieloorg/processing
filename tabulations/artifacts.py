import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from tabulations.constants import CSV_FILES, KBART_LEGACY_FILENAME, KBART_TEMPLATE


class ArtifactPublisher:
    def __init__(self, config, logger, report_date):
        self.config = config
        self.logger = logger
        self.report_date = report_date
        self._network_dir = config.checkpoint_dir / "network"

    def prepare_network(self):
        """Prepara uma nova área temporária para a composição da rede."""
        self.clear_network()
        self._network_dir.mkdir(parents=True)

    def publish_collection(
        self,
        work_dir,
        destination,
        kbart_file,
        network_mode,
    ):
        """Valida, compacta e publica atomicamente os arquivos da coleção."""
        work_dir = Path(work_dir)
        paths = [work_dir / name for name in (*CSV_FILES, kbart_file)]
        missing = [path.name for path in paths if not path.is_file()]

        if missing:
            names = ", ".join(missing)
            raise RuntimeError(f"arquivos obrigatórios ausentes: {names}")

        archive = work_dir / f"tabs_{destination}.zip"
        self._write_archive(paths, archive, kbart_file)
        self._publish_archive(archive)

        if network_mode:
            self._append_network(paths, kbart_file)

        self.logger.info("ARQUIVO coleção=%s arquivo=%s", destination, archive)

        return archive

    def publish_network(self):
        """Compacta e publica atomicamente os arquivos consolidados da rede."""
        network_kbart = KBART_TEMPLATE.format(
            acronym="network",
            date=self.report_date,
        )
        paths = [
            self._network_dir / name
            for name in (*CSV_FILES, network_kbart)
            if (self._network_dir / name).is_file()
        ]

        if not paths:
            raise RuntimeError("nenhum arquivo disponível para tabs_network.zip")

        archive = self._network_dir / "tabs_network.zip"
        self._write_archive(paths, archive)
        self._publish_archive(archive)
        self.logger.info("ARQUIVO rede=%s", archive)

        return archive

    def clear_network(self):
        """Remove somente a área temporária usada na composição da rede."""
        if self._network_dir.exists():
            shutil.rmtree(self._network_dir)

    def _write_archive(self, paths, archive, kbart_file=None):
        archive.parent.mkdir(parents=True, exist_ok=True)
        temporary = archive.with_suffix(".zip.tmp")

        try:
            with ZipFile(temporary, "w", ZIP_DEFLATED) as zip_file:
                for path in paths:
                    zip_file.write(path, arcname=path.name)
                    if path.name == kbart_file:
                        zip_file.write(path, arcname=KBART_LEGACY_FILENAME)

            temporary.replace(archive)
        finally:
            temporary.unlink(missing_ok=True)

    def _publish_archive(self, archive):
        self.config.tabs_dir.mkdir(parents=True, exist_ok=True)
        destination = self.config.tabs_dir / archive.name
        temporary = destination.with_suffix(".zip.tmp")

        try:
            shutil.copy2(archive, temporary)
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)

    def _append_network(self, paths, kbart_file):
        self._network_dir.mkdir(parents=True, exist_ok=True)
        network_kbart = KBART_TEMPLATE.format(
            acronym="network",
            date=self.report_date,
        )

        for source in paths:
            name = network_kbart if source.name == kbart_file else source.name
            destination = self._network_dir / name
            has_content = destination.is_file() and destination.stat().st_size

            with (
                source.open("r", encoding="utf-8", newline="") as source_file,
                destination.open("a", encoding="utf-8", newline="") as output,
            ):
                if has_content:
                    next(source_file, None)

                shutil.copyfileobj(source_file, output)
