import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from tabulations.state import StateStore


class StateStoreTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.checkpoint_dir = self.root / "checkpoints"
        self.queue_file = self.root / "failed.queue"
        self.store = StateStore(self.checkpoint_dir, self.queue_file)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_prepares_new_collection(self):
        work_dir, state, restarted = self.store.prepare_collection(
            "arg-AR",
            "2026-07-30",
        )

        self.assertFalse(restarted)
        self.assertEqual(
            state,
            {
                "version": 1,
                "report_date": "2026-07-30",
                "steps": {},
            },
        )
        self.assertEqual(
            json.loads((work_dir / "state.json").read_text()),
            state,
        )

    def test_keeps_current_checkpoint(self):
        work_dir, state, restarted = self.store.prepare_collection(
            "arg-AR",
            "2026-07-30",
        )
        output = work_dir / "documents.csv"
        output.write_text("header\nvalue\n", encoding="utf-8")

        loaded_dir, loaded_state, loaded_restarted = self.store.prepare_collection(
            "arg-AR", "2026-07-30"
        )

        self.assertFalse(restarted)
        self.assertFalse(loaded_restarted)
        self.assertEqual(loaded_dir, work_dir)
        self.assertEqual(loaded_state, state)
        self.assertTrue(output.is_file())

    def test_discards_corrupt_old_or_undated_checkpoint(self):
        cases = (
            "{not-json",
            json.dumps({"report_date": "2026-07-29", "steps": {}}),
            json.dumps({"version": 1, "steps": {}}),
        )

        for position, content in enumerate(cases):
            with self.subTest(position=position):
                item = f"arg-{position}"
                work_dir = self.checkpoint_dir / item
                work_dir.mkdir(parents=True)
                stale_output = work_dir / "stale.csv"
                stale_output.write_text("stale\n", encoding="utf-8")
                (work_dir / "state.json").write_text(
                    content,
                    encoding="utf-8",
                )

                _, state, restarted = self.store.prepare_collection(
                    item,
                    "2026-07-30",
                )

                self.assertTrue(restarted)
                self.assertFalse(stale_output.exists())
                self.assertEqual(state["report_date"], "2026-07-30")
                self.assertEqual(state["steps"], {})

    def test_completed_step_requires_nonempty_outputs(self):
        work_dir, state, _ = self.store.prepare_collection(
            "arg-AR",
            "2026-07-30",
        )
        state["steps"]["publication_all"] = {"status": "completed"}
        output = work_dir / "documents.csv"
        output.touch()

        self.assertFalse(
            self.store.is_completed(
                state,
                "publication_all",
                work_dir,
                ("documents.csv",),
            )
        )

        output.write_text("header\n", encoding="utf-8")

        self.assertTrue(
            self.store.is_completed(
                state,
                "publication_all",
                work_dir,
                ("documents.csv",),
            )
        )
        self.assertFalse(
            self.store.is_completed(
                state,
                "publication_all",
                work_dir,
                ("documents.csv",),
                ("documents.csv",),
            )
        )

        output.write_text("header\nvalue\n", encoding="utf-8")

        self.assertTrue(
            self.store.is_completed(
                state,
                "publication_all",
                work_dir,
                ("documents.csv",),
                ("documents.csv",),
            )
        )

    def test_marks_completed_and_failed_steps_atomically(self):
        work_dir, state, _ = self.store.prepare_collection(
            "arg-AR",
            "2026-07-30",
        )
        state_path = work_dir / "state.json"

        with mock.patch(
            "tabulations.state.os.replace",
            wraps=os.replace,
        ) as replace:
            self.store.mark_completed(
                state_path,
                state,
                "publication_all",
                "2026-07-30",
                1.236,
                ("documents.csv",),
            )
            self.store.mark_failed(
                state_path,
                state,
                "export_kbart",
                "2026-07-30",
                datetime(2026, 7, 30, 12, 30, tzinfo=timezone.utc),
            )

        saved = json.loads(state_path.read_text(encoding="utf-8"))

        self.assertEqual(replace.call_count, 2)
        self.assertEqual(
            saved["steps"]["publication_all"]["duration_seconds"],
            1.24,
        )
        self.assertEqual(
            saved["steps"]["publication_all"]["outputs"],
            ["documents.csv"],
        )
        self.assertEqual(
            saved["steps"]["export_kbart"]["failed_at"],
            "2026-07-30T12:30:00+00:00",
        )
        self.assertEqual(
            list(work_dir.glob(".*.tmp")),
            [],
        )


class QueueStoreTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.checkpoint_dir = self.root / "checkpoints"
        self.queue_file = self.root / "failed.queue"
        self.store = StateStore(self.checkpoint_dir, self.queue_file)

    def test_pending_queue_is_deduplicated_and_atomic(self):
        with mock.patch(
            "tabulations.state.os.replace",
            wraps=os.replace,
        ) as replace:
            self.store.save_pending(["arg-AR", " mex-MX ", "arg-AR", "", "mex-MX"])

        self.assertEqual(replace.call_count, 1)
        self.assertEqual(
            self.queue_file.read_text(encoding="utf-8"),
            "arg-AR\nmex-MX\n",
        )
        self.assertEqual(
            self.store.load_pending(),
            ["arg-AR", "mex-MX"],
        )
        self.assertEqual(list(self.root.glob(".failed.queue.*.tmp")), [])

        self.store.save_pending([])

        self.assertFalse(self.queue_file.exists())

    def test_load_pending_deduplicates_existing_file(self):
        self.queue_file.write_text(
            "arg-AR\n\narg-AR\n mex-MX \n",
            encoding="utf-8",
        )

        self.assertEqual(
            self.store.load_pending(),
            ["arg-AR", "mex-MX"],
        )

    def test_clear_collections_removes_only_requested_checkpoints(self):
        for item in ("arg-AR", "mex-MX"):
            work_dir, _, _ = self.store.prepare_collection(
                item,
                "2026-07-30",
            )
            (work_dir / "output.csv").write_text("value\n", encoding="utf-8")

        self.store.clear_collections(["arg-AR", "arg-AR"])

        self.assertFalse((self.checkpoint_dir / "arg-AR").exists())
        self.assertTrue((self.checkpoint_dir / "mex-MX").is_dir())
