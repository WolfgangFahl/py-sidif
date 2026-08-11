"""
Created on 2026-08-11

@author: wf
"""

from sidif.sidif import SiDIFParser
from sidif.url_fetcher import UrlFetcher
from tests.basetest import Basetest


class TestUrlFetcher(Basetest):
    """
    test fetching SiDIF from URLs including MediaWiki pages
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.base_url = "https://contexts.bitplan.com/index.php"
        # Context pages with Context since earlier than 2025 - stable names
        self.context_names = [
            "BookContext",
            "CityContext",
            "ConfIDentMetadataSchema",
            "CrSchema",
            "FamilyContext",
            "Infrastructure",
            "MetaModel",
            "OpenSourceProjectsContext",
            "Presentation",
            "QueryContext",
            "ResearchContext",
            "SMWCon",
            "SmartRQM",
            "TeachingSchema",
            "WebContext",
            "WikiContext",
        ]

    def test_is_html(self):
        """
        test the HTML detection
        """
        cases = [
            ("<!DOCTYPE html>\n<html>", True),
            ("<html lang='en'>", True),
            ("Paris isA City\n", False),
        ]
        for text, expected in cases:
            self.assertEqual(expected, UrlFetcher.is_html(text), text)

    def test_raw_url(self):
        """
        test the raw URL derivation
        """
        uf = UrlFetcher()
        cases = [
            (f"{self.base_url}/MetaModel", f"{self.base_url}/MetaModel?action=raw"),
            (
                f"{self.base_url}?title=MetaModel",
                f"{self.base_url}?title=MetaModel&action=raw",
            ),
        ]
        for page_url, expected in cases:
            self.assertEqual(expected, uf.raw_url(page_url))

    def test_extract_sidif(self):
        """
        test extracting SiDIF from wikitext source blocks
        """
        uf = UrlFetcher()
        wikitext = """= Model =
<source lang='xml' id='sidif'>
Paris isA City
</source>
"""
        sidif = uf.extract_sidif(wikitext)
        self.assertEqual("Paris isA City\n", sidif)

    def test_sidif_of_url(self):
        """
        test the plumbing entry point on a wiki page URL and a plain SiDIF URL
        """
        uf = UrlFetcher(debug=self.debug)
        for url in [
            f"{self.base_url}/MetaModel",
            "https://raw.githubusercontent.com/WolfgangFahl/py-sidif/refs/heads/main/sidif_examples/familyTree.sidif",
        ]:
            sidif = uf.sidif_of_url(url)
            self.assertFalse(UrlFetcher.is_html(sidif), url)
            self.assertTrue(len(sidif) > 0, url)

    def test_context_pages(self):
        """
        test fetching and parsing the SiDIF of the stable context pages
        of contexts.bitplan.com
        """
        uf = UrlFetcher(debug=self.debug)
        sp = SiDIFParser(showErrors=False)
        for context_name in self.context_names:
            with self.subTest(context=context_name):
                page_url = f"{self.base_url}/{context_name}"
                sidif = uf.sidif_of_url(page_url)
                self.assertTrue(len(sidif) > 0, context_name)
                result, error = sp.parseText(sidif, title=context_name)
                self.assertIsNone(error, context_name)
                dif = result["links"][0]
                if self.debug:
                    print(f"{context_name}: {len(dif.triples)} triples")
                self.assertTrue(len(dif.triples) > 0, context_name)
