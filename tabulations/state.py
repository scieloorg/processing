import csv
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path


class StateStore:
    def __init__(self, checkpoint_dir, failed_collections_file):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.failed_collections_file = Path(failed_collections_file)

    def prepare_collection(self, item, report_date):
        """Carrega o checkpoint atual ou reinicia a coleção para a data informada."""
        work_dir = self.checkpoint_dir / item
        state_path = work_dir / "state.json"
        existed = work_dir.exists()
        state = self._load_state(state_path, report_date)

        if state is not None:
            return work_dir, state, False

        if existed:
            if work_dir.is_dir():
                shutil.rmtree(work_dir)
            else:
                work_dir.unlink()

        work_dir.mkdir(parents=True)
        state = {
            "version": 1,
            "report_date": report_date,
            "steps": {},
        }
        self._write_json(state_path, state)

        return work_dir, state, existed

    def is_completed(self, state, step, work_dir, outputs, data_outputs=()):
        """Verifica se a etapa concluída ainda possui todos os arquivos válidos."""
        saved_step = state.get("steps", {}).get(step, {})

        if saved_step.get("status") != "completed":
            return False

        return self.outputs_valid(work_dir, outputs, data_outputs)

    def outputs_valid(self, work_dir, outputs, data_outputs=()):
        work_dir = Path(work_dir)
        paths = [work_dir / output for output in outputs]

        if not all(path.is_file() and path.stat().st_size > 0 for path in paths):
            return False

        return all(self._has_data_row(work_dir / output) for output in data_outputs)

    def mark_completed(self, state_path, state, step, report_date, duration, outputs):
        state["report_date"] = report_date
        state.setdefault("steps", {})[step] = {
            "status": "completed",
            "report_date": report_date,
            "completed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "duration_seconds": round(duration, 2),
            "outputs": list(outputs),
        }
        self._write_json(Path(state_path), state)

    def mark_failed(self, state_path, state, step, report_date, failed_at=None):
        failed_at = failed_at or datetime.now(timezone.utc)

        if isinstance(failed_at, datetime):
            failed_at = failed_at.isoformat(timespec="seconds")

        state["report_date"] = report_date
        state.setdefault("steps", {})[step] = {
            "status": "failed",
            "report_date": report_date,
            "failed_at": failed_at,
        }
        self._write_json(Path(state_path), state)

    def load_pending(self):
        try:
            lines = self.failed_collections_file.read_text(
                encoding="utf-8"
            ).splitlines()
        except FileNotFoundError:
            return []

        collections = (line.strip() for line in lines)

        return list(dict.fromkeys(item for item in collections if item))

    def save_pending(self, collections):
        """Substitui atomicamente a fila de coleções pendentes, sem duplicações."""
        collections = (str(item).strip() for item in collections if str(item).strip())
        collections = list(dict.fromkeys(collections))

        if not collections:
            self.failed_collections_file.unlink(missing_ok=True)
            return

        content = "".join(f"{item}\n" for item in collections)
        self._atomic_write(self.failed_collections_file, content)

    def clear_collections(self, collections):
        for item in dict.fromkeys(collections):
            work_dir = self.checkpoint_dir / item

            if work_dir.is_dir():
                shutil.rmtree(work_dir)
            elif work_dir.exists():
                work_dir.unlink()

    def _load_state(self, state_path, report_date):
        if not state_path.is_file():
            return None

        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return None

        if not isinstance(state, dict):
            return None

        if state.get("report_date") != report_date:
            return None

        if not isinstance(state.get("steps"), dict):
            return None

        return state

    def _write_json(self, path, state):
        content = json.dumps(state, indent=2, sort_keys=True) + "\n"
        self._atomic_write(path, content)

    def _has_data_row(self, path):
        try:
            with path.open("r", encoding="utf-8", newline="") as source:
                rows = csv.reader(source, strict=True)
                next(rows, None)
                return any(any(field.strip() for field in row) for row in rows)
        except (OSError, UnicodeError, csv.Error):
            return False

    def _atomic_write(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None

        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as output:
                temporary = Path(output.name)
                output.write(content)

            os.replace(temporary, path)
        except Exception:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

            raise
