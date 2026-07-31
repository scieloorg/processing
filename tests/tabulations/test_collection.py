import tempfile
import unittest
from pathlib import Path
from unittest.mock import ANY, Mock

from tabulations.collection import CollectionProcessor


class CollectionProcessorTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.work_dir = self.root / "scl-BR"
        self.work_dir.mkdir()
        self.state = {"steps": {}}
        self.state_store = Mock()
        self.state_store.prepare_collection.return_value = (
            self.work_dir,
            self.state,
            False,
        )
        self.commands = Mock()
        self.commands.run.return_value = True
        self.artifacts = Mock()
        self.artifacts.publish_collection.return_value = self.work_dir / "tabs_bra.zip"
        self.notifier = Mock()
        self.logger = Mock()
        self.processor = CollectionProcessor(
            self.state_store,
            self.commands,
            self.artifacts,
            self.notifier,
            self.logger,
            "2026-07-30",
        )

    def test_maps_scl_to_bra_and_forwards_nationality(self):
        result = self.processor.process("scl-BR", False)

        self.assertTrue(result)
        self.assertEqual(self.commands.run.call_count, 4)
        first_step = self.commands.run.call_args_list[0].args
        self.assertEqual(
            first_step[:4],
            (
                "scl-BR",
                "publication_all",
                "processing_publication_all",
                "scl",
            ),
        )
        self.assertEqual(first_step[8], ("-n", "BR"))
        self.assertEqual(first_step[10], ("documents_counts.csv",))
        self.assertEqual(
            self.commands.run.call_args_list[1].args[10],
            ("journals.csv",),
        )
        self.assertEqual(self.commands.run.call_args_list[2].args[10], ())
        self.assertEqual(
            self.commands.run.call_args_list[3].args[10],
            ("SciELO_bra_AllTitles_2026-07-30.csv",),
        )
        self.artifacts.publish_collection.assert_called_once_with(
            self.work_dir,
            "bra",
            "SciELO_bra_AllTitles_2026-07-30.csv",
            False,
        )

    def test_runs_every_step_and_reports_all_failures(self):
        self.commands.run.side_effect = (False, True, False, True)

        result = self.processor.process("scl-BR", True)

        self.assertFalse(result)
        self.assertEqual(self.commands.run.call_count, 4)
        self.artifacts.publish_collection.assert_not_called()
        message = self.notifier.send.call_args.args[0]
        self.assertIn(
            "Etapas: publication_all, publication_journals_status_changes.",
            message,
        )

    def test_omits_nationality_when_suffix_is_empty(self):
        self.artifacts.publish_collection.return_value = self.work_dir / "tabs_arg.zip"

        result = self.processor.process("arg-", False)

        self.assertTrue(result)
        first_step = self.commands.run.call_args_list[0].args
        self.assertEqual(first_step[3], "arg")
        self.assertEqual(first_step[8], ())

    def test_rejects_invalid_collection_before_preparing_state(self):
        result = self.processor.process("invalid", False)

        self.assertFalse(result)
        self.state_store.prepare_collection.assert_not_called()
        self.commands.run.assert_not_called()

    def test_returns_failure_when_archive_cannot_be_published(self):
        self.artifacts.publish_collection.side_effect = RuntimeError("broken")

        result = self.processor.process("scl-BR", False)

        self.assertFalse(result)
        self.logger.error.assert_called_with(
            "COLEÇÃO falhou=%s etapa=compactação motivo=%s",
            "scl-BR",
            ANY,
        )
