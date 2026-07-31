import subprocess
import time


def _execute(command, work_dir, logger):
    try:
        process = subprocess.Popen(
            command,
            cwd=work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except OSError as error:
        logger.error(
            "Não foi possível iniciar %s: %s",
            command[0],
            error,
        )
        return 127

    if process.stdout is None:
        return process.wait()

    for line in process.stdout:
        if line.strip():
            logger.info(
                "SAÍDA comando=%s mensagem=%s",
                command[0],
                line.rstrip(),
            )

    return process.wait()


class CommandExecutor:
    def __init__(self, config, state_store, logger, report_date):
        self.config = config
        self.state_store = state_store
        self.logger = logger
        self.report_date = report_date

    def run(
        self,
        item,
        step,
        executable,
        acronym,
        work_dir,
        state_path,
        state,
        outputs,
        extra_args=(),
        result_file=None,
        data_outputs=(),
    ):
        """Executa uma etapa com retomada, tentativas e validação dos arquivos."""
        if self.state_store.is_completed(
            state,
            step,
            work_dir,
            outputs,
            data_outputs,
        ):
            self.logger.info(
                "RETOMADA coleção=%s etapa=%s ação=ignorada motivo=checkpoint_válido",
                item,
                step,
            )
            return True

        for output in outputs:
            (work_dir / output).unlink(missing_ok=True)

        command_log = self.config.log_dir / f"{step}_{item}.log"
        command = [
            executable,
            "-c",
            acronym,
            *extra_args,
            "-o",
            str(command_log),
            "-l",
            "ERROR",
        ]

        if result_file:
            command.extend(("-r", result_file))

        return self._run_attempts(
            item,
            step,
            work_dir,
            state_path,
            state,
            outputs,
            command,
            command_log,
            data_outputs,
        )

    def _run_attempts(
        self, item, step, work_dir, state_path, state, outputs, command,
        command_log, data_outputs
    ):
        for attempt in range(1, self.config.max_retries + 1):
            if attempt > 1 and self.config.retry_delay:
                time.sleep(self.config.retry_delay)

            started_at = time.monotonic()
            self.logger.info(
                "INÍCIO coleção=%s etapa=%s tentativa=%d/%d comando=%s",
                item,
                step,
                attempt,
                self.config.max_retries,
                " ".join(command),
            )
            return_code = _execute(command, work_dir, self.logger)
            duration = time.monotonic() - started_at

            if return_code == 0 and self.state_store.outputs_valid(
                work_dir,
                outputs,
                data_outputs,
            ):
                self.state_store.mark_completed(
                    state_path,
                    state,
                    step,
                    self.report_date,
                    duration,
                    outputs,
                )
                self.logger.info(
                    "SUCESSO coleção=%s etapa=%s duração=%.1fs arquivos=%s",
                    item,
                    step,
                    duration,
                    ",".join(outputs),
                )
                return True

            self._log_failure(
                item,
                step,
                attempt,
                duration,
                return_code,
                command_log,
            )

        self.state_store.mark_failed(
            state_path,
            state,
            step,
            self.report_date,
        )
        return False

    def _log_failure(self, item, step, attempt, duration, return_code, command_log):
        reason = (
            f"código de saída {return_code}"
            if return_code
            else "arquivos esperados ausentes, vazios ou sem registros"
        )

        self.logger.error(
            "FALHA coleção=%s etapa=%s tentativa=%d/%d duração=%.1fs "
            "motivo=%s log=%s",
            item,
            step,
            attempt,
            self.config.max_retries,
            duration,
            reason,
            command_log,
        )
