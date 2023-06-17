"""
Main module for the w3schools scraper, contains the Base class.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import requests
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from typing import Literal

    from bs4.element import NavigableString, Tag

from html_to_json import convert_tables

from .endpoints import EXCLUDE_TOPICS
from .endpoints import W3SchoolsNavigator as Navigator

try:
    import lxml  # type: ignore  # noqa: F401  # pylint: disable=unused-import

    HTML_PARSER = "lxml"
except ImportError:
    HTML_PARSER = "html.parser"

with open("user-agent.txt", "r") as file:
    USER_AGENT = file.read()

HEADERS = {
    "User-Agent": USER_AGENT,
}

log = logging.getLogger("src.base")


class Base:
    """Base class for the w3schools scraper"""

    soup: BeautifulSoup
    main_div: Tag | NavigableString | None  # type: ignore

    def __init__(
        self,
        url: str,
    ) -> None:
        self._url = url
        self.url = url
        self.pages: dict[str, BeautifulSoup] = {}
        self.page = self.download_page()
        self.__counter = 0

    def __string_parse(self, string: str) -> str:
        """Parse the string to be used as filename"""
        string = string.strip()
        return string.replace("<br>", "\n").replace("<br/>", "\n")

    def to_file(
        self,
        soup: BeautifulSoup | Tag | None = None,
        *,
        filename: str = "test.html",
        full: bool = False,
    ) -> None:
        """Write the html to a file"""
        if soup is None:
            soup = self.soup

        with open(filename, "w+", encoding="utf-8") as file:
            file.write(soup.prettify() if full else self.main_div.prettify())  # type: ignore

    def to_image(self, soup: BeautifulSoup | None, *, filename: str) -> str:
        import imgkit

        if soup is None:
            soup = self.soup
        try:
            filename = filename or f"/files/{soup.name}.{' '.join(soup['class'])}{self.__counter}.jpg"
            imgkit.from_string(
                soup.prettify(),
                filename,
                css=["/lib/w3schools32.css"],
                # automatic resize image
                options={
                    "format": "png",
                    "encoding": "UTF-8",
                },
            )
            self.__counter += 1
            return filename
        except OSError:
            log.error("failed to convert to image", exc_info=True)
            return ""

    def download_page(self) -> str:
        """Download the page from the url"""
        try:
            self.soup = self.pages[self.url]
            log.debug("recieved page from cache")
            return self.soup.prettify()
        except KeyError:
            log.debug("page not in cache, downloading...")
            return self._download_page()

    def _download_page(self) -> str:
        retry = 5
        while retry:
            try:
                response = requests.get(self.url, timeout=3, headers=HEADERS)
            except (requests.ReadTimeout, requests.ConnectionError):
                log.debug("request timed out, retrying...")
                retry -= 1
                continue
            log.debug(
                "recived response from %s with status code %s",
                self.url,
                response.status_code,
            )
            if response.ok:
                self.soup: BeautifulSoup = BeautifulSoup(response.text, HTML_PARSER)
                # W3Schools all main content lies in a div with class=w3-main
                self.main_div: Tag = self.soup.find(Navigator.MAIN_TG.value, {"class": Navigator.MAIN.value})  # type: ignore

                if self.main_div is None:
                    log.error("failed to get main_div, recieved None instead")
                    raise RuntimeError("failed to find main div")

                self.pages[self.url] = self.soup

                return response.text

            log.debug("failed getting proper response, retrying...")
            retry -= 1

        log.info("failed to get data from %s returning `<html></html>`", self.url)

        return "<html></html>"

    def get_next_button_url(self) -> str | None:
        """Get the url of the next button"""
        endpoint = self._get_button_endpoint(Navigator.NEXT.value, "Next")
        return f"{self._url}{endpoint}" if endpoint is not None else None

    def get_previous_button_url(self) -> str | None:
        """Get the url of the previous button"""
        endpoint = self._get_button_endpoint(Navigator.PREVIOUS.value, "Previous")
        return f"{self._url}{endpoint}" if endpoint is not None else None

    def _get_button_endpoint(self, finder: str, button_name: str) -> str | None:
        # sourcery skip: assign-if-exp, reintroduce-else
        to_find = {"class": finder}
        anchor: Tag | NavigableString | None = self.main_div.find("a", to_find)
        if anchor is not None and button_name in anchor.text:
            return anchor["href"]  # type: ignore
        return None

    def paginate_next(self) -> None:
        """Paginate to the next page"""
        self._paginate(to="next")

    def paginate_prev(self) -> None:
        """Paginate to the previous page"""
        self._paginate(to="previous")

    def _paginate(self, *, to: Literal["next", "previous"]) -> None:
        url: str | None = getattr(self, f"get_{to}_button_url")()

        if url is None:
            raise RuntimeError(f"failed to get {to!r} page")

        self.url = url
        self.page = self.download_page()

    def get_intro_panel(self) -> Tag | NavigableString | None:
        """Get the intro panel"""
        return self.main_div.find(
            Navigator.PANEL_INFO_TG.value, {"class": Navigator.PANEL_INFO.value}
        )

    def get_paragraph_intros(self) -> list[Tag | NavigableString]:
        """Get the intros"""
        return self.main_div.find_all(
            Navigator.PARAGRAPHS_INTRO_TG.value,
            {"class": Navigator.PARAGRAPHS_INTRO.value},
        )

    def get_headers(self) -> list[Tag | NavigableString]:
        """Get the headers"""
        return self.main_div.find_all("h2")

    def get_h2_sibling(
        self, header: Tag | NavigableString
    ) -> Tag | NavigableString | None:
        """Get the sibling of the header"""
        sib = header.find_next_sibling()

        # W3Schools uses <h2> tags for headers and <p> tags for paragraphs
        # <h2> and <p> tags are siblings along with <div> tags (for code blocks/examples)

        # every topic is separated by a <hr> tag

        return None if sib and sib.name == "hr" else sib

    def _get_all_h2_siblings(
        self, header: Tag | NavigableString
    ) -> list[Tag | NavigableString]:
        """Get the siblings of the header"""
        siblings = []
        sib = self.get_h2_sibling(header)
        while sib is not None:
            siblings.append(sib)
            sib = self.get_h2_sibling(sib)
        return siblings

    def get_topic(self, header: Tag | NavigableString) -> dict:
        """Get the topic"""
        siblings = self._get_all_h2_siblings(header)

        if header.text in EXCLUDE_TOPICS:
            return {}

        payload = {"header": header.text, "rest": []}
        for sibling in siblings:
            _payload = {"text": "", "type": ""}
            _copy_payload = _payload.copy()

            if sibling.name == "p":
                _payload["text"] = self.__string_parse(sibling.text)
                _payload["type"] = "p"
                if sibling.find("img") is not None and sibling.find("img").has_attr("src"):  # type: ignore
                    if not sibling.text:
                        _payload["url"] = self._url + sibling.find("img")["src"]  # type: ignore
                    _payload["type"] = "img"

            elif sibling.name == "ul":
                st = "".join("\n" + self.__string_parse(li.text) for li in sibling.find_all("li"))  # type: ignore
                _payload["text"] = st
                _payload["type"] = "ul"

            elif sibling.name == "ol":
                st = "".join("\n" + self.__string_parse(li.text) for li in sibling.find_all("li"))  # type: ignore
                _payload["text"] = st
                _payload["type"] = "ol"

            elif sibling.name == "div":
                if sibling.has_attr("class") and "w3-clear" in sibling["class"]:  # type: ignore
                    continue

                if sibling.has_attr("class") and "w3-panel" in sibling["class"]:  # type: ignore
                    _payload["text"] = self.__string_parse(sibling.text)
                    _payload["type"] = "panel"

                elif sibling.has_attr("class") and "w3-example" in sibling["class"]:  # type: ignore
                    internal_sibling = sibling.find("div", {"class": "w3-code"})  # type: ignore
                    if internal_sibling is not None:
                        _payload["text"] = self.__string_parse(BeautifulSoup(str(internal_sibling).replace("<br/>", "\n"), HTML_PARSER).text)  # type: ignore
                        _payload["type"] = "code"
                        # I don't know why but the code blocks have <br/> tags instead of \n

                elif not sibling.has_attr("class"):  # type: ignore
                    _payload["text"] = str(sibling)
                    _payload["type"] = "div"
                    _payload["file"] = self.to_image(sibling)  # type: ignore

            elif sibling.name == "table":
                _payload["text"] = str(convert_tables(str(sibling))[0])
                _payload["type"] = "table"

            if _payload != _copy_payload:
                payload["rest"].append(_payload)
        return payload
