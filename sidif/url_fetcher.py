"""
Created on 2026-08-11

Light-weight SiDIF fetching from URLs including wiki pages

@author: wf
"""

import re
from urllib.request import urlopen


class UrlFetcher:
    """
    UrlFetcher allows to fetch SiDIF content from a given URL
    while avoiding to use extra libraries to do so. For MediaWiki pages
    that render as HTML by default this is possible due to the convention followed
    in the SiDIF carrying pages. See https://contexts.bitplan.com/index.php/Main_Page for a list of Example
    Context pages with embeded SiDIF sections.
    """

    # SiDIF is encoded via traditional syntaxhighlight
    source_pattern = re.compile(r"<source[^>]*>\n?(.*?)</source>", re.DOTALL)

    def __init__(self, debug: bool = False):
        self.debug = debug

    @classmethod
    def is_html(cls, text: str) -> bool:
        """
        check whether the given text is an HTML document

        Args:
            text(str): the text to check

        Returns:
            bool: True if the text starts with an HTML marker
        """
        start = text.lstrip()[:15].lower()
        html = start.startswith("<!doctype html") or start.startswith("<html")
        return html

    @classmethod
    def raw_url(cls, page_url: str) -> str:
        """
        get the action=raw wikitext URL for the given wiki page URL

        Args:
            page_url(str): the URL of the wiki page

        Returns:
            str: the URL that delivers the raw wikitext of the page
        """
        separator = "&" if "?" in page_url else "?"
        url = f"{page_url}{separator}action=raw"
        return url

    def fetch(self, url: str) -> str:
        """
        fetch the text content of the given URL

        Args:
            url(str): the URL to fetch

        Returns:
            str: the text content
        """
        text = urlopen(url).read().decode()
        return text

    def fetch_wikitext(self, page_url: str) -> str:
        """
        fetch the raw wikitext for the given wiki page URL

        Args:
            page_url(str): the URL of the wiki page

        Returns:
            str: the wikitext of the page
        """
        url = self.raw_url(page_url)
        wikitext = self.fetch(url)
        return wikitext

    def extract_sidif(self, wikitext: str) -> str:
        """
        extract the SiDIF content from the given wikitext by concatenating
        the content of all source tag blocks

        Args:
            wikitext(str): the wikitext to extract the SiDIF from

        Returns:
            str: the SiDIF content, empty if there is no source block
        """
        blocks = self.source_pattern.findall(wikitext)
        sidif = "\n".join(blocks)
        return sidif

    def sidif_for_page(self, page_url: str) -> str:
        """
        get the SiDIF content embedded in the given wiki page

        Args:
            page_url(str): the URL of the wiki page

        Returns:
            str: the SiDIF content of the page
        """
        wikitext = self.fetch_wikitext(page_url)
        sidif = self.extract_sidif(wikitext)
        return sidif

    def sidif_of_url(self, url: str) -> str:
        """
        get the SiDIF content of the given URL - plain SiDIF is returned as is,
        an HTML response is treated as a wiki page and refetched via raw_url
        with the SiDIF extracted from its source blocks

        Args:
            url(str): the URL to get the SiDIF content for

        Returns:
            str: the SiDIF content
        """
        text = self.fetch(url)
        if self.is_html(text):
            text = self.sidif_for_page(url)
        return text
