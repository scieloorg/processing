import unittest
from unittest.mock import MagicMock, patch

from export import kbart


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
