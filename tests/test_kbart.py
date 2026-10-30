import csv
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from export import kbart


class KbartJournalInclusionTest(unittest.TestCase):
    def setUp(self):
        for service in ("ratchet_server", "articlemeta_server", "publicationstats_server"):
            mocked_service = patch.object(kbart.utils, service)
            mocked_service.start()
            self.addCleanup(mocked_service.stop)

        with patch.object(kbart.Dumper, "write"):
            self.dumper = kbart.Dumper(collection="ven")

    def test_includes_journals_regardless_of_status(self):
        journals = [
            SimpleNamespace(scielo_issn=str(index), current_status=status)
            for index, status in enumerate(
                ("current", "suspended", "deceased", "other", None)
            )
        ]
        journals.append(SimpleNamespace(scielo_issn="missing-status"))
        self.dumper._articlemeta.journals.return_value = journals
        self.dumper.fmt_csv = MagicMock(side_effect=lambda journal: journal.scielo_issn)

        rows = list(self.dumper.items())

        self.assertEqual(rows, [journal.scielo_issn for journal in journals])
        self.dumper._articlemeta.journals.assert_called_once_with(
            collection="ven", issn=None,
        )

    def test_last_publication_fields_follow_journal_status(self):
        journal = SimpleNamespace(
            scielo_issn="1234-5678", collection_acronym="ven", title="Periódico",
            print_issn="1234-5678", electronic_issn=None, publisher_name=[],
            url=lambda: "https://ve.scielo.org/scielo.php?script=sci_serial",
        )
        first = SimpleNamespace(
            publication_date="2000-01-01", issue=SimpleNamespace(volume="1", number="1"),
        )
        last = SimpleNamespace(
            publication_date="2020-12-01", issue=SimpleNamespace(volume="21", number="4"),
        )
        self.dumper._first_included_document_by_journal = MagicMock(return_value=first)
        self.dumper._last_included_document_by_journal = MagicMock(return_value=last)

        for status in ("current", "suspended", "deceased", "other", None):
            with self.subTest(status=status):
                journal.current_status = status

                row = next(csv.reader([self.dumper.fmt_csv(journal)]))

                self.assertEqual(row[3:6], ["2000-01-01", "1", "1"])
                self.assertEqual(
                    row[6:9],
                    ["", "", ""] if status == "current" else ["2020-12-01", "21", "4"],
                )

class KbartTest(unittest.TestCase):

    def test_title_url_uses_https_for_updated_collections(self):
        url = "http://www.scielo.br/scielo.php?script=sci_issues&pid=0100-879X"

        result = kbart.title_url_for_collection(url, "scl")

        self.assertEqual(
            result,
            "https://www.scielo.br/scielo.php?script=sci_issues&pid=0100-879X"
        )

    def test_title_url_keeps_http_for_collections_without_https(self):
        url = "http://www.scielo.org.bo/scielo.php?script=sci_issues&pid=2077-3323"

        result = kbart.title_url_for_collection(url, "bol")

        self.assertEqual(result, url)

    def test_title_url_keeps_existing_https(self):
        url = "https://www.scielo.br/scielo.php?script=sci_issues&pid=0100-879X"

        result = kbart.title_url_for_collection(url, "scl")

        self.assertEqual(result, url)

    def test_fmt_csv_handles_none_url_and_title(self):
        with patch.object(kbart.utils, "ratchet_server"), \
             patch.object(kbart.utils, "articlemeta_server"), \
             patch.object(kbart.utils, "publicationstats_server"):
            dumper = kbart.Dumper(collection="rvt")
            dumper._first_included_document_by_journal = MagicMock(return_value=None)
            dumper._last_included_document_by_journal = MagicMock(return_value=None)

            mock_journal = MagicMock()
            mock_journal.title = None
            mock_journal.print_issn = "0043-3144"
            mock_journal.electronic_issn = "2309-5830"
            mock_journal.scielo_issn = "0043-3144"
            mock_journal.collection_acronym = "rvt"
            mock_journal.url.return_value = None
            mock_journal.publisher_name = ["The University of the West Indies"]

            result = dumper.fmt_csv(mock_journal)
            self.assertIn('"0043-3144"', result)
            self.assertIn('""', result)


if __name__ == "__main__":
    unittest.main()
