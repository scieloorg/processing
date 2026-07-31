from tabulations.constants import ACRONYM_PATTERN, CSV_FILES, KBART_TEMPLATE


class CollectionProcessor:
    def __init__(
        self,
        state_store,
        command_executor,
        artifact_publisher,
        notifier,
        logger,
        report_date,
    ):
        self.state_store = state_store
        self.command_executor = command_executor
        self.artifact_publisher = artifact_publisher
        self.notifier = notifier
        self.logger = logger
        self.report_date = report_date

    def process(self, item, network_mode):
        """Executa as etapas da coleção e publica o pacote quando completas."""
        if not ACRONYM_PATTERN.fullmatch(item):
            self.logger.error(
                "Acrônimo inválido: %s (esperado: abc, abc-XY ou abc-)",
                item,
            )
            return False

        acronym, separator, nationality = item.partition("-")
        destination = "bra" if acronym == "scl" else acronym
        work_dir, state, restarted = self.state_store.prepare_collection(
            item,
            self.report_date,
        )
        state_path = work_dir / "state.json"
        kbart_file = KBART_TEMPLATE.format(
            acronym=destination,
            date=self.report_date,
        )

        if restarted:
            self.logger.info(
                "CHECKPOINT coleção=%s ação=reiniciado data=%s",
                item,
                self.report_date,
            )

        self.logger.info("COLEÇÃO início=%s checkpoint=%s", item, work_dir)
        failed_steps = self._run_steps(
            item,
            acronym,
            nationality if separator else "",
            work_dir,
            state_path,
            state,
            kbart_file,
        )

        if failed_steps:
            self._report_failure(item, failed_steps, work_dir)
            return False

        try:
            archive = self.artifact_publisher.publish_collection(
                work_dir,
                destination,
                kbart_file,
                network_mode,
            )
        except (OSError, RuntimeError) as error:
            self.logger.error(
                "COLEÇÃO falhou=%s etapa=compactação motivo=%s",
                item,
                error,
            )
            return False

        self.logger.info("COLEÇÃO sucesso=%s arquivo=%s", item, archive)
        return True

    def _run_steps(
        self,
        item,
        acronym,
        nationality,
        work_dir,
        state_path,
        state,
        kbart_file,
    ):
        steps = (
            (
                "publication_all",
                "processing_publication_all",
                CSV_FILES[:7],
                ("-n", nationality) if nationality else (), None,
                ("documents_counts.csv",),
            ),
            (
                "publication_journals",
                "processing_publication_journals",
                ("journals.csv",),
                (), "journals.csv",
                ("journals.csv",),
            ),
            (
                "publication_journals_status_changes",
                "processing_publication_journals_status_changes",
                ("journals_status_changes.csv",),
                (), "journals_status_changes.csv", (),
            ),
            (
                "export_kbart",
                "processing_export_kbart",
                (kbart_file,),
                (), kbart_file,
                (kbart_file,),
            ),
        )
        failed = []

        for name, command, outputs, extra_args, result_file, data_outputs in steps:
            succeeded = self.command_executor.run(
                item,
                name,
                command,
                acronym,
                work_dir,
                state_path,
                state,
                outputs,
                extra_args,
                result_file,
                data_outputs,
            )
            if not succeeded:
                failed.append(name)

        return failed

    def _report_failure(self, item, failed_steps, work_dir):
        self.logger.error(
            "COLEÇÃO falhou=%s etapas=%s checkpoint=%s",
            item,
            ",".join(failed_steps),
            work_dir,
        )
        self.notifier.send(
            f":x: Processing: coleção `{item}` incompleta. "
            f"Etapas: {', '.join(failed_steps)}. Retomada: `{work_dir}`."
        )
