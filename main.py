from __future__ import annotations

import logging
import re

import bs4

# overload prettify of bs4.BeautifulSoup
orig_prettify = bs4.BeautifulSoup.prettify
r = re.compile(r"^(\s*)", re.MULTILINE)


def prettify(self, encoding=None, formatter="minimal", indent_width=4):
    return r.sub(r"\1" * indent_width, orig_prettify(self, encoding, formatter))


bs4.BeautifulSoup.prettify = prettify  # type: ignore  monkey patching


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.getLogger("requests").setLevel(logging.DEBUG)


formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name:<10}: {module}.{funcName} - {message}",
    "%Y-%m-%d %H:%M:%S",
    style="{",
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
