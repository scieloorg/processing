import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import Mock, call, patch

from tabulations.workflow import SlackNotifier, Workflow
from tests.tabulations.fixtures import make_config


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.config = make_config(self.root)
        self.state_store = Mock()
        self.state_store.load_pending.return_value = []
        self.processor = Mock()
        self.processor.process.return_value = True
        self.artifacts = Mock()
        self.notifier = Mock()
        self.logger = Mock()
        self.workflow = Workflow(
            self.config,
            self.state_store,
            self.processor,
            self.artifacts,
            self.notifier,
            self.logger,
        )

    def test_pending_collections_run_before_requested_without_duplicates(self):
        self.state_store.load_pending.return_value = [
            "mex-MX",
            "arg-AR",
            "mex-MX",
        ]

        collections = self.workflow._collections_to_process(
            ["arg-AR", "bol-BO"],
        )

        self.assertEqual(
            collections,
            ["mex-MX", "arg-AR", "bol-BO"],
        )

    def test_continues_after_unexpected_collection_error(self):
        self.processor.process.side_effect = (
            RuntimeError("broken"),
            True,
        )

        failed = self.workflow._process_collections(
            ["arg-AR", "bol-BO"],
            False,
        )

        self.assertEqual(failed, ["arg-AR"])
        self.assertEqual(
            self.processor.process.call_args_list,
            [call("arg-AR", False), call("bol-BO", False)],
        )
        self.logger.exception.assert_called_once()

    def test_failure_exit_policy_preserves_collection_checkpoints(self):
        for exit_on_failure, expected in ((True, 1), (False, 0)):
            with self.subTest(exit_on_failure=exit_on_failure):
                config = make_config(
                    self.root / str(exit_on_failure),
                    exit_on_failure=exit_on_failure,
                )
                state_store = Mock()
                state_store.load_pending.return_value = []
                processor = Mock()
                processor.process.return_value = False
                artifacts = Mock()
                workflow = Workflow(
                    config,
                    state_store,
                    processor,
                    artifacts,
                    Mock(),
                    Mock(),
                )

                result = workflow.run(["arg-AR"])

                self.assertEqual(result, expected)
                pending = list(state_store.save_pending.call_args.args[0])
                self.assertEqual(pending, ["arg-AR"])
                state_store.clear_collections.assert_not_called()
                artifacts.clear_network.assert_not_called()

    def test_success_cleans_checkpoints_and_network_state(self):
        result = self.workflow.run(["arg-AR", "bol-BO"])

        self.assertEqual(result, 0)
        pending = list(self.state_store.save_pending.call_args.args[0])
        self.assertEqual(pending, [])
        self.state_store.clear_collections.assert_called_once_with(
            ["arg-AR", "bol-BO"],
        )
        self.artifacts.clear_network.assert_called_once_with()

    def test_collection_failure_prevents_network_publication(self):
        self.processor.process.side_effect = lambda item, network_mode: (
            item != "scl-BR"
        )

        result = self.workflow.run([])

        self.assertEqual(result, 1)
        self.artifacts.prepare_network.assert_called_once_with()
        self.artifacts.publish_network.assert_not_called()
        self.artifacts.clear_network.assert_not_called()
        pending = list(self.state_store.save_pending.call_args.args[0])
        self.assertEqual(pending, ["scl-BR"])
        self.logger.error.assert_any_call(
            "REDE não_publicada motivo=coleções_com_falha "
            "arquivo_anterior=preservado"
        )


class SlackNotifierTest(unittest.TestCase):
    def setUp(self):
        self.logger = Mock()

    def test_does_nothing_without_webhook(self):
        notifier = SlackNotifier("", self.logger)

        with patch("tabulations.workflow.urllib.request.urlopen") as open_url:
            result = notifier.send("message")

        self.assertIsNone(result)
        open_url.assert_not_called()

    def test_posts_json_message(self):
        notifier = SlackNotifier("https://example.test/slack", self.logger)
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)

        with patch(
            "tabulations.workflow.urllib.request.urlopen",
            return_value=response,
        ) as open_url:
            notifier.send("processing complete")

        request = open_url.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.test/slack")
        self.assertEqual(
            json.loads(request.data.decode()),
            {"text": "processing complete"},
        )
        self.assertEqual(open_url.call_args.kwargs, {"timeout": 10})

    def test_network_failure_is_nonfatal(self):
        notifier = SlackNotifier("https://example.test/slack", self.logger)

        with patch(
            "tabulations.workflow.urllib.request.urlopen",
            side_effect=urllib.error.URLError("offline"),
        ):
            result = notifier.send("message")

        self.assertIsNone(result)
        self.logger.warning.assert_called_once()
