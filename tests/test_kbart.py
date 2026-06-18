# coding: utf-8
import unittest

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


if __name__ == "__main__":
    unittest.main()
