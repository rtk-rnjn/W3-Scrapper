from __future__ import annotations

from enum import Enum


class W3SchoolsNavigator(Enum):
    """W3Schools Navigator"""

    NEXT = "w3-right w3-btn"
    PREVIOUS = "w3-left w3-btn"

    MAIN = "w3-main"
    MAIN_TG = "div"

    PANEL_INFO = "w3-panel w3-info"
    PANEL_INFO_TG = "div"

    PARAGRAPHS_INTRO = "intro"
    PARAGRAPHS_INTRO_TG = "p"

    def __str__(self) -> str:
        return self.value


# fmt: off
class W3SchoolsEndpoints(Enum):
    """W3Schools endpoints"""

    HTML     = "https://www.w3schools.com/html/"
    TAGS     = "https://www.w3schools.com/tags/"
    CSS      = "https://www.w3schools.com/css/"
    JAVASCRIPT   = "https://www.w3schools.com/js/"
    SQL      = "https://www.w3schools.com/sql/"
    PYTHON   = "https://www.w3schools.com/python/"
    JAVA     = "https://www.w3schools.com/java/"
    PHP      = "https://www.w3schools.com/php/"
    W3CSS    = "https://www.w3schools.com/w3css/"
    C        = "https://www.w3schools.com/c/"
    CPP      = "https://www.w3schools.com/cpp/"
    CS       = "https://www.w3schools.com/cs/"
    REACT    = "https://www.w3schools.com/react/"
    R        = "https://www.w3schools.com/r/"
    JQUERY   = "https://www.w3schools.com/jquery/"

    def __str__(self) -> str:
        return self.value
# fmt: on

EXCLUDE_TOPICS = [
    "Test Yourself With Exercises",
    "Exercise",
    "Examples"
    "Report Error",
    "Thank You For Helping Us!",
]


class W3SchoolsCodeSelector(Enum):
    """W3Schools Code Selector"""

    GENERAL = "w3-code"
    GENERAL_TG = "div"

    HTML = "w3-code notranslate htmlHigh"
    HTML_TG = "div"

    CSS = "w3-code notranslate cssHigh"
    CSS_TG = "div"

    JAVASCRIPT = "w3-code notranslate javascriptHigh"
    JAVASCRIPT_TG = "div"

    SQL = "w3-code notranslate sqlHigh"
    SQL_TG = "div"

    PYTHON = "w3-code notranslate pythonHigh"
    PYTHON_TG = "div"

    JAVA = "w3-white language-java"
    JAVA_TG = "pre"

    PHP = "w3-code notranslate htmlHigh"
    PHP_TG = "div"

    W3CSS = "w3-code notranslate cssHigh"
    W3CSS_TG = "div"

    C = "w3-code notranslate javaHigh"
    C_TG = "div"

    CPP = "w3-code notranslate javaHigh"
    CPP_TG = "div"

    CS = "w3-white language-csharp"
    CS_TG = "pre"

    REACT = "xw3-white language-jsx"
    REACT_TG = "pre"

    R = "w3-code notranslate pythonHigh"
    R_TG = "div"

    JQUERY = "w3-code notranslate jsHigh"
    JQUERY_TG = "div"
