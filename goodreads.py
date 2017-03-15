#!/usr/bin/python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

"""
    Variety quote plugin sourcing quotes from goodreads.com
    This script is placed in '~/.config/variety/plugins' and then activated from inside Variety's
    Preferences Quotes menu
"""

import logging
import random

from locale import gettext as _
from variety.Util import Util
from variety.plugins.IQuoteSource import IQuoteSource


logger = logging.getLogger("variety")


class GoodreadsSource(IQuoteSource):
    """
        Retrives quotes from goodreads.com. Reads the popular quotes.

        Attributes:
            quotes(list): list containing the quotes
    """

    def __init__(self):
        super(IQuoteSource, self).__init__()
        self.quotes = []

    @classmethod
    def get_info(cls):
        return {
            "name": "Goodreads",
            "description": _("Popular quotes from goodreads.com"),
            "author": "Denis Mach",
            "version": "0.1"
        }

    def supports_search(self):
        return False

    def activate(self):
        if self.active:
            return
        self.active = True

        self.quotes = []
        self.fetch_goodreads_quotes()

    def deactivate(self):
        self.quotes = []
        self.active = False

    def fetch_goodreads_quotes(self):
        BASE_URL = 'https://www.goodreads.com/quotes'

        self.quotes = []

        # iterate through goodreads pagination
        for i in range(1, 20):
            query = '?page=' + str(i)
            url = BASE_URL + query
            bs = Util.html_soup(url)

            # this is the element that contains the quote text
            quoteElems = bs.find_all("div", {"class": "quoteText"})

            # process the selected elems to get the quote text
            for tag in quoteElems:
                # ignore the tag that contains the author info
                quote_stripped_author = tag.contents[:-1]
                quoteFragments = []
                self._create_quote_fragments(quoteFragments, quote_stripped_author)
                
                # create a new entry
                new_quote = self.assemble_quote(tag, quoteFragments, url)
                self.quotes.append(new_quote)

        if not self.quotes:
            logger.warning("Could not find quotes for URL " + BASE_URL)

    def _create_quote_fragments(self, quoteFragments, quote_stripped_author):
        # the quote might be seperated by several <br>
        # have to traverse them to gather up the quote text pieces
        for quote_pieces in quote_stripped_author:
            fragment = ''
            try:
                fragment = quote_pieces.text.strip()
            except:
                fragment = quote_pieces.strip()
            quoteFragments.append(fragment)

    def assemble_quote(self, tag, quoteFragments, url):
        # there is a unicode  hyphen that seperates the quote and author
        # we want to extract only the quote by splitting
        quoteText = " ".join(quoteFragments)
        splitQuote = quoteText.split(u"\u2015")

        # this gets rid of the unicode quotations and stuff
        # TODO need an algo to detect multiple quotes to ignore their removal
        quoteText = splitQuote[0].encode("ascii", "ignore")
        quoteText = ' '.join(quoteText.split())
        author = tag.find("a", {"class": "authorOrTitle"}).contents[
            0].strip().encode("ascii", "ignore")
        newItem = {"quote": quoteText, "author": author,
                   "sourceName": "goodreads", "link": url}

        return newItem

    def get_for_author(self, author):
        return []

    def get_for_keyword(self, keyword):
        return []

    def get_random(self):
        if self.quotes:
            return [random.choice(self.quotes)]
        else:
            return self.quotes
